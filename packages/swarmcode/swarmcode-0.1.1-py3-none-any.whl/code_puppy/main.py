import argparse
import asyncio
import os
import sys
import json
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console, ConsoleOptions, RenderResult
from rich.markdown import CodeBlock, Markdown
from rich.syntax import Syntax
from rich.text import Text

# Load system config FIRST before anything else
SYSTEM_CONFIG_PATH = Path.home() / ".code_puppy" / "system_config.json"
if SYSTEM_CONFIG_PATH.exists():
    try:
        with open(SYSTEM_CONFIG_PATH) as f:
            system_config = json.load(f)
            # Apply environment overrides from config
            for key, value in system_config.get("environment_overrides", {}).items():
                os.environ[key] = str(value)
            # Also set MODELS_JSON_PATH if specified
            if "models_json_path" in system_config:
                os.environ["MODELS_JSON_PATH"] = system_config["models_json_path"]
    except Exception as e:
        print(f"Warning: Could not load system config: {e}", file=sys.stderr)

from code_puppy import __version__, state_management
from code_puppy.agent import get_code_generation_agent, session_memory
from code_puppy.command_line.prompt_toolkit_completion import (
    get_input_with_combined_completion,
    get_prompt_with_active_model,
)
from code_puppy.config import ensure_config_exists
from code_puppy.state_management import get_message_history, set_message_history
from code_puppy.command_line.utils import sanitize_for_display, is_likely_command, sanitize_error_message

# Initialize rich console for pretty output
from code_puppy.tools.common import console
from code_puppy.version_checker import fetch_latest_version
from code_puppy.message_history_processor import message_history_processor

# from code_puppy.tools import *  # noqa: F403

import logging
from datetime import datetime

def setup_application_debug_logging():
    """Set up comprehensive debug logging for the entire application."""
    import sys
    from pathlib import Path
    
    # Create log file in current directory
    log_file = Path.cwd() / "code_puppy_debug.log"
    
    # Configure formatter with detailed information
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler for all debug logs
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler for warnings and errors
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log session start
    logging.info("="*80)
    logging.info("CODE PUPPY DEBUG SESSION STARTED")
    logging.info(f"Timestamp: {datetime.now().isoformat()}")
    logging.info(f"Version: {__version__}")
    logging.info(f"Working Directory: {Path.cwd()}")
    logging.info(f"Python Version: {sys.version}")
    logging.info(f"Command Line: {' '.join(sys.argv)}")
    logging.info("="*80)
    
    # Set environment variable so other modules know debug is on
    os.environ["CODE_PUPPY_DEBUG"] = "true"
    
    # Enable RAG debug mode too
    os.environ["RAG_DEBUG"] = "true"
    
    # Log all environment variables (masking sensitive ones)
    logging.debug("Environment Variables:")
    for key, value in os.environ.items():
        if any(sensitive in key.upper() for sensitive in ['KEY', 'TOKEN', 'SECRET', 'PASSWORD']):
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            logging.debug(f"  {key}={masked}")
        else:
            logging.debug(f"  {key}={value}")


# Define a function to get the secret file path
def get_secret_file_path():
    hidden_directory = os.path.join(os.path.expanduser("~"), ".agent_secret")
    if not os.path.exists(hidden_directory):
        os.makedirs(hidden_directory)
    return os.path.join(hidden_directory, "history.txt")


async def main():
    # Parse args first to check for debug flag
    parser = argparse.ArgumentParser(description="Code Puppy - A code generation agent")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--debug", "-d", action="store_true", help="Enable debug logging to code_puppy_debug.log"
    )
    parser.add_argument("command", nargs="*", help="Run a single command")
    args = parser.parse_args()
    
    # Set up debug logging if requested
    if args.debug:
        setup_application_debug_logging()
        console.print("[bold yellow]🐛 Debug mode enabled - logging to code_puppy_debug.log[/bold yellow]")
    
    # Ensure the config directory and puppy.cfg with name info exist (prompt user if needed)
    ensure_config_exists()
    current_version = __version__
    latest_version = fetch_latest_version("code-puppy")
    console.print(f"Current version: {current_version}")
    console.print(f"Latest version: {latest_version}")
    if latest_version and latest_version != current_version:
        console.print(
            f"[bold yellow]A new version of code puppy is available: {latest_version}[/bold yellow]"
        )
        console.print("[bold green]Please consider updating![/bold green]")
    global shutdown_flag
    shutdown_flag = False  # ensure this is initialized

    # Load environment variables from .env file
    load_dotenv()

    # args already parsed at the beginning of main()
    history_file_path = get_secret_file_path()

    if args.command:
        # Join the list of command arguments into a single string command
        command = " ".join(args.command)
        try:
            while not shutdown_flag:
                agent = get_code_generation_agent()
                async with agent.run_mcp_servers():
                    response = await agent.run(command)
                agent_response = response.output
                console.print(agent_response)
                break
        except AttributeError as e:
            error_msg = sanitize_error_message(e)
            console.print(f"[bold red]AttributeError:[/bold red] {error_msg}")
            console.print(
                "[bold yellow]\u26a0 The response might not be in the expected format, missing attributes like 'output_message'."
            )
        except Exception as e:
            error_msg = sanitize_error_message(e)
            console.print(f"[bold red]Unexpected Error:[/bold red] {error_msg}")
    elif args.interactive:
        await interactive_mode(history_file_path)
    else:
        parser.print_help()


# Add the file handling functionality for interactive mode
async def interactive_mode(history_file_path: str) -> None:
    from code_puppy.command_line.meta_command_handler import handle_meta_command

    """Run the agent in interactive mode."""
    console.print("[bold green]Code Puppy[/bold green] - Interactive Mode")
    
    # Show instance info for multi-instance awareness
    try:
        from code_puppy.utils.instance_manager import get_instance_manager
        instance_info = get_instance_manager().get_info()
        console.print(f"[dim]Instance: {instance_info['instance_id']} | PID: {instance_info['pid']}[/dim]")
        if instance_info.get('ports'):
            ports_str = ', '.join([f"{k}:{v}" for k, v in instance_info['ports'].items()])
            if ports_str:
                console.print(f"[dim]Allocated ports: {ports_str}[/dim]")
    except Exception:
        pass  # Don't fail if instance manager not available
    
    console.print("Type 'exit' or 'quit' to exit the interactive mode.")
    console.print("Type 'clear' to reset the conversation history.")
    console.print("Press [bold yellow]ESC[/bold yellow] to cancel input, [bold yellow]Ctrl+C[/bold yellow] to stop tasks.")
    console.print(
        "Type [bold blue]@[/bold blue] for path completion, or [bold blue]/m[/bold blue] to pick a model."
    )

    # Show meta commands right at startup - DRY!
    from code_puppy.command_line.meta_command_handler import META_COMMANDS_HELP

    console.print(META_COMMANDS_HELP)
    # Show MOTD if user hasn't seen it after an update
    try:
        from code_puppy.command_line.motd import print_motd

        print_motd(console, force=False)
    except Exception as e:
        console.print(f"[yellow]MOTD error: {e}[/yellow]")

    # Check if prompt_toolkit is installed
    try:
        import prompt_toolkit  # noqa: F401

        console.print("[dim]Using prompt_toolkit for enhanced tab completion[/dim]")
    except ImportError:
        console.print(
            "[yellow]Warning: prompt_toolkit not installed. Installing now...[/yellow]"
        )
        try:
            import subprocess

            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "prompt_toolkit"]
            )
            console.print("[green]Successfully installed prompt_toolkit[/green]")
        except Exception as e:
            console.print(f"[bold red]Error installing prompt_toolkit: {e}[/bold red]")
            console.print(
                "[yellow]Falling back to basic input without tab completion[/yellow]"
            )

    # Set up history file in home directory
    history_file_path_prompt = os.path.expanduser("~/.code_puppy_history.txt")
    history_dir = os.path.dirname(history_file_path_prompt)

    # Ensure history directory exists
    if history_dir and not os.path.exists(history_dir):
        try:
            os.makedirs(history_dir, exist_ok=True)
        except Exception as e:
            console.print(
                f"[yellow]Warning: Could not create history directory: {e}[/yellow]"
            )

    while True:
        console.print("[bold blue]Enter your coding task:[/bold blue]")

        try:
            # Use prompt_toolkit for enhanced input with path completion
            try:
                # Use the async version of get_input_with_combined_completion
                task = await get_input_with_combined_completion(
                    get_prompt_with_active_model(),
                    history_file=history_file_path_prompt,
                )
            except ImportError:
                # Fall back to basic input if prompt_toolkit is not available
                task = input(">>> ")

        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C, Ctrl+D, or ESC
            if os.environ.get("CODE_PUPPY_ESC_PRESSED") == "true":
                console.print("\n[yellow]Input cancelled (ESC)[/yellow]")
                os.environ.pop("CODE_PUPPY_ESC_PRESSED", None)
            else:
                console.print("\n[yellow]Input cancelled[/yellow]")
            continue

        # Log user input
        logging.debug(f"User input: {task}")
        
        # Check for exit commands
        if task.strip().lower() in ["exit", "quit"]:
            console.print("[bold green]Goodbye![/bold green]")
            logging.info("User exited interactive mode")
            break

        # Check for clear command (supports `clear`, `/clear`, and `~clear` for backward compatibility)
        if task.strip().lower() in ("clear", "/clear", "~clear"):
            state_management._message_history = []
            console.print("[bold yellow]Conversation history cleared![/bold yellow]")
            console.print(
                "[dim]The agent will not remember previous interactions.[/dim]\n"
            )
            logging.info("Conversation history cleared")
            continue

        # Handle / meta/config commands (also supports ~ for backward compatibility)
        # But only if it looks like an actual command, not pasted content
        if (task.strip().startswith("/") or task.strip().startswith("~")) and is_likely_command(task):
            logging.debug(f"Meta command: {task.strip()}")
            if handle_meta_command(task.strip(), console):
                continue
        if task.strip():
            # Sanitize task for safe display
            safe_task = sanitize_for_display(task)
            console.print(f"\n[bold blue]Processing task:[/bold blue] {safe_task}")
            console.print("[dim](Press Ctrl+C to cancel)[/dim]\n")
            logging.info(f"Processing task: {task}")
            
            # Check if RAG is enabled and display context (using V2)
            if os.getenv("ENABLE_RAG", "false").lower() == "true":
                try:
                    # Use the new V2 system
                    from code_puppy.rag_enhancer_v2 import display_rag_context
                    display_rag_context(task, console)
                except Exception as e:
                    # Only show error in debug mode
                    if os.getenv("RAG_DEBUG", "false").lower() == "true":
                        console.print(f"[dim]RAG context error: {e}[/dim]")
                    # Log the error
                    logging.debug(f"RAG context unavailable: {e}")

            # Write to the secret file for permanent history
            with open(history_file_path, "a") as f:
                f.write(f"{task}\n")

            try:
                prettier_code_blocks()
                local_cancelled = False
                
                # Import retry handler
                from code_puppy.retry_handler import RetryHandler, RateLimitTracker
                
                # Create rate limit tracker
                rate_tracker = RateLimitTracker(window_size=60, max_requests=50)
                
                async def run_agent_task():
                    try:
                        # Check and display rate limit status
                        rate_tracker.show_status()
                        await rate_tracker.wait_if_needed()
                        rate_tracker.add_request()
                        
                        agent = get_code_generation_agent()
                        async with agent.run_mcp_servers():
                            # Wrap the agent.run in retry handler
                            async def execute_agent():
                                return await agent.run(
                                    task,
                                    message_history=get_message_history()
                                )
                            
                            # Use retry handler for smart retries
                            return await RetryHandler.retry_with_backoff(execute_agent)
                    except Exception as e:
                        # Check if it's a rate limit error
                        if "request_limit" in str(e).lower() or "429" in str(e):
                            console.log("[yellow]Rate limit reached - will retry automatically[/yellow]")
                            # Try one more time with retry logic
                            return await RetryHandler.retry_with_backoff(execute_agent)
                        else:
                            # Sanitize error message for safe display
                            error_msg = sanitize_error_message(e)
                            console.log(f"Task failed: {error_msg}")
                            raise

                agent_task = asyncio.create_task(run_agent_task())

                import signal

                original_handler = None

                def keyboard_interrupt_handler(sig, frame):
                    nonlocal local_cancelled
                    if not agent_task.done():
                        set_message_history(
                            message_history_processor(
                                get_message_history()
                            )
                        )
                        agent_task.cancel()
                        local_cancelled = True

                try:
                    original_handler = signal.getsignal(signal.SIGINT)
                    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
                    result = await agent_task
                except asyncio.CancelledError:
                    pass
                finally:
                    if original_handler:
                        signal.signal(signal.SIGINT, original_handler)

                if local_cancelled:
                    console.print("[yellow]⚠ Task cancelled by user[/yellow]")
                else:
                    # Handle case where result might be None due to errors
                    if result is None:
                        console.print("[red]⚠ Task failed - no response received[/red]")
                        console.print("[yellow]Tip: Try again or use 'clear' to reset conversation[/yellow]")
                    elif hasattr(result, 'output'):
                        agent_response = result.output
                        console.print(agent_response)
                        filtered = message_history_processor(get_message_history())
                        set_message_history(filtered)
                    else:
                        console.print("[red]⚠ Unexpected response format[/red]")
                        console.print(f"[dim]Result: {result}[/dim]")

                # Show context status
                console.print(
                    f"[dim]Context: {len(get_message_history())} messages in history[/dim]\n"
                )

            except Exception:
                console.print_exception()


def prettier_code_blocks():
    class SimpleCodeBlock(CodeBlock):
        def __rich_console__(
            self, console: Console, options: ConsoleOptions
        ) -> RenderResult:
            code = str(self.text).rstrip()
            yield Text(self.lexer_name, style="dim")
            syntax = Syntax(
                code,
                self.lexer_name,
                theme=self.theme,
                background_color="default",
                line_numbers=True,
            )
            yield syntax
            yield Text(f"/{self.lexer_name}", style="dim")

    Markdown.elements["fence"] = SimpleCodeBlock


def main_entry():
    """Entry point for the installed CLI tool."""
    asyncio.run(main())


if __name__ == "__main__":
    main_entry()
