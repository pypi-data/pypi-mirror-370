import os

from rich.console import Console

from code_puppy.command_line.model_picker_completion import (
    load_model_names,
    update_model_in_input,
)
from code_puppy.config import get_config_keys
from code_puppy.command_line.utils import make_directory_table
from code_puppy.command_line.motd import print_motd

META_COMMANDS_HELP = """
[bold magenta]Meta Commands Help[/bold magenta]
/help, /h             Show this help message
/cd <dir>             Change directory or show directories
/codemap [dir] [page] Show paginated code map (e.g., /codemap . 2)
/codemap search <term> Search for files/dirs containing term
/codemap clear        Clear code map cache
/m <model>            Set active model
/motd                 Show the latest message of the day (MOTD)
/show                 Show puppy config key-values
/set                  Set puppy config key-values
/logs                 View tool execution logs
/rag config           Launch interactive RAG configuration interface
/rag on/off           Enable/disable RAG (Retrieval Augmented Generation)
/rag index [dir] [n]  Index directory (optionally limit to n files)
/rag status           Show RAG system status (V2)
/rag debug            Debug mode control [on|off|clear|show]
/<unknown>            Show unknown meta command warning
"""


def handle_meta_command(command: str, console: Console) -> bool:
    """
    Handle meta/config commands prefixed with '/' (or '~' for backward compatibility).
    Returns True if the command was handled (even if just an error/help), False if not.
    """
    command = command.strip()
    
    # Support both / and ~ prefixes for backward compatibility
    # Convert ~ to / for uniform handling
    if command.startswith('~'):
        command = '/' + command[1:]

    if command.strip().startswith("/motd"):
        print_motd(console, force=True)
        return True

    # /codemap (code structure visualization with pagination)
    if command.startswith("/codemap"):
        # FORCE LOGGING - Log that we're handling codemap
        from code_puppy.tools.tool_logger import log_tool
        log_tool(
            tool_name="meta_command_codemap",
            input_data={"command": command, "cwd": os.getcwd()},
            output_data=None,
            metadata={"handler": "meta_command_handler"}
        )
        
        from code_puppy.tools.paginated_code_map import handle_codemap_command
        
        try:
            result = handle_codemap_command(command, os.getcwd())
            # Log success
            log_tool(
                tool_name="meta_command_codemap_success",
                input_data={"command": command},
                output_data={"result_length": len(result) if result else 0},
                metadata={"status": "success"}
            )
            console.print(result)
        except Exception as e:
            # Log error
            log_tool(
                tool_name="meta_command_codemap_error",
                input_data={"command": command},
                output_data=None,
                error=e,
                metadata={"error_message": str(e)}
            )
            console.print(f"[red]Error generating code map:[/red] {e}")
        return True

    if command.startswith("/cd"):
        tokens = command.split()
        if len(tokens) == 1:
            try:
                table = make_directory_table()
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error listing directory:[/red] {e}")
            return True
        elif len(tokens) == 2:
            dirname = tokens[1]
            target = os.path.expanduser(dirname)
            if not os.path.isabs(target):
                target = os.path.join(os.getcwd(), target)
            if os.path.isdir(target):
                os.chdir(target)
                console.print(
                    f"[bold green]Changed directory to:[/bold green] [cyan]{target}[/cyan]"
                )
            else:
                console.print(f"[red]Not a directory:[/red] [bold]{dirname}[/bold]")
            return True

    if command.strip().startswith("/show"):
        from code_puppy.command_line.model_picker_completion import get_active_model
        from code_puppy.config import (
            get_owner_name,
            get_puppy_name,
            get_yolo_mode,
            get_message_history_limit,
            get_tool_output_limit,
            get_smart_truncate,
        )

        puppy_name = get_puppy_name()
        owner_name = get_owner_name()
        model = get_active_model()
        yolo_mode = get_yolo_mode()
        msg_limit = get_message_history_limit()
        tool_limit = get_tool_output_limit()
        smart_truncate = get_smart_truncate()
        console.print(f"""[bold magenta]🐶 Puppy Status[/bold magenta]

[bold]puppy_name:[/bold]     [cyan]{puppy_name}[/cyan]
[bold]owner_name:[/bold]     [cyan]{owner_name}[/cyan]
[bold]model:[/bold]          [green]{model}[/green]
[bold]YOLO_MODE:[/bold]      {"[red]ON[/red]" if yolo_mode else "[yellow]off[/yellow]"}
[bold]message_history_limit:[/bold]   Keeping last [cyan]{msg_limit}[/cyan] messages in context
[bold]tool_output_limit:[/bold]       Max [cyan]{tool_limit:,}[/cyan] chars per tool output
[bold]smart_truncate:[/bold]          {"[green]ON[/green] (AI summarization)" if smart_truncate else "[yellow]OFF[/yellow] (simple truncation)"}
""")
        return True

    if command.startswith("/set"):
        # Syntax: /set KEY=VALUE or /set KEY VALUE
        from code_puppy.config import set_config_value

        tokens = command.split(None, 2)
        argstr = command[len("/set") :].strip()
        key = None
        value = None
        if "=" in argstr:
            key, value = argstr.split("=", 1)
            key = key.strip()
            value = value.strip()
        elif len(tokens) >= 3:
            key = tokens[1]
            value = tokens[2]
        elif len(tokens) == 2:
            key = tokens[1]
            value = ""
        else:
            console.print(
                f"[yellow]Usage:[/yellow] /set KEY=VALUE or /set KEY VALUE\nConfig keys: {', '.join(get_config_keys())}"
            )
            return True
        if key:
            set_config_value(key, value)
            console.print(
                f'[green]🌶 Set[/green] [cyan]{key}[/cyan] = "{value}" in puppy.cfg!'
            )
        else:
            console.print("[red]You must supply a key.[/red]")
        return True

    if command.startswith("/m"):
        # Try setting model and show confirmation
        new_input = update_model_in_input(command)
        if new_input is not None:
            from code_puppy.command_line.model_picker_completion import get_active_model
            from code_puppy.agent import get_code_generation_agent

            model = get_active_model()
            # Make sure this is called for the test
            get_code_generation_agent(force_reload=True)
            console.print(
                f"[bold green]Active model set and loaded:[/bold green] [cyan]{model}[/cyan]"
            )
            return True
        # If no model matched, show available models
        model_names = load_model_names()
        console.print("[yellow]Usage:[/yellow] /m <model-name>")
        console.print(f"[yellow]Available models:[/yellow] {', '.join(model_names)}")
        return True
    if command in ("/help", "/h"):
        console.print(META_COMMANDS_HELP)
        return True
    
    # Handle /logs command
    if command.startswith("/logs"):
        from code_puppy.command_line.view_logs import view_tool_logs
        return view_tool_logs(command, console)
    
    # /rag commands (RAG management) - MUST be before the generic / handler
    if command.startswith("/rag"):
        parts = command.split(maxsplit=3)
        
        if len(parts) == 1 or parts[1] == "status":
            # Show RAG status using V2 system
            rag_enabled = os.getenv("ENABLE_RAG", "false").lower() == "true"
            debug_mode = os.getenv("RAG_DEBUG", "false").lower() == "true"
            
            console.print(f"\n🔍 [bold]RAG Status (V2 System)[/bold]")
            console.print(f"  Enabled: {'✅ Yes' if rag_enabled else '❌ No'}")
            console.print(f"  Debug Mode: {'🐛 ON' if debug_mode else '⚫ OFF'}")
            
            if debug_mode:
                from pathlib import Path
                log_file = Path.cwd() / "rag_debug.log"
                if log_file.exists():
                    size = log_file.stat().st_size / 1024  # KB
                    console.print(f"  Debug Log: {log_file} ({size:.1f} KB)")
            
            if rag_enabled:
                try:
                    from code_puppy.rag_enhancer_v2 import get_rag_enhancer
                    enhancer = get_rag_enhancer(console)
                    if enhancer._initialized:
                        console.print(f"  System: ✅ Initialized")
                        if enhancer.config:
                            console.print(f"  Provider: {enhancer.config.get('provider', 'unknown')}")
                            console.print(f"  Model: {enhancer.config.get('model', 'default')}")
                        if enhancer.manager:
                            total_files = len(enhancer.manager.index)
                            console.print(f"  Indexed Files: {total_files}")
                    else:
                        console.print(f"  System: ❌ Not initialized")
                        console.print(f"  [dim]Use '/rag config' to configure[/dim]")
                except Exception as e:
                    console.print(f"  Error: {e}")
            else:
                console.print("  [dim]Use '/rag on' to enable RAG[/dim]")
            
        elif parts[1] == "on":
            os.environ["ENABLE_RAG"] = "true"
            console.print("✅ [bold green]RAG enabled[/bold green]")
            console.print("[dim]Context from embeddings will be shown for queries[/dim]")
            
        elif parts[1] == "off":
            os.environ["ENABLE_RAG"] = "false"
            console.print("❌ [bold yellow]RAG disabled[/bold yellow]")
            
        elif parts[1] == "config" or parts[1] == "configure":
            # Launch the RAG configuration in a subprocess to avoid event loop conflicts
            try:
                from code_puppy.embeddings.rag_config_launcher import launch_rag_config
                
                # Run in subprocess
                launch_rag_config(console)
                
            except Exception as e:
                console.print(f"[bold red]Error launching RAG configuration:[/bold red] {e}")
        
        elif parts[1] == "index":
            # Index directory using V2 system
            # Support formats: /rag index [dir] [limit]
            directory = "."
            max_files = None
            
            if len(parts) > 2:
                # Check if second param is a number (limit) or directory
                try:
                    max_files = int(parts[2])
                except ValueError:
                    directory = parts[2]
                    if len(parts) > 3:
                        try:
                            max_files = int(parts[3])
                        except ValueError:
                            pass
            
            console.print(f"🚀 [bold cyan]Starting RAG indexing (V2 System)...[/bold cyan]")
            console.print(f"  Directory: [green]{directory}[/green]")
            if max_files:
                console.print(f"  Limit: [yellow]{max_files} files[/yellow]")
            
            try:
                import asyncio
                from code_puppy.rag_enhancer_v2 import get_rag_enhancer
                
                os.environ["ENABLE_RAG"] = "true"  # Ensure RAG is enabled
                
                # Get or create enhancer
                enhancer = get_rag_enhancer(console)
                
                if not enhancer._initialized:
                    console.print("[bold yellow]RAG not initialized. Initializing now...[/bold yellow]")
                    
                    # Use async helper to handle event loop conflicts
                    from code_puppy.utils.async_helper import run_async_in_sync
                    
                    try:
                        success = run_async_in_sync(enhancer.initialize())
                    except Exception as e:
                        console.print(f"[bold red]Error initializing RAG:[/bold red] {e}")
                        return True
                    
                    if not success:
                        console.print("[bold red]Failed to initialize RAG[/bold red]")
                        console.print("[yellow]Tip: Use '/rag config' to configure provider[/yellow]")
                        return True
                
                # Run indexing
                console.print("\n[bold]Indexing in progress...[/bold]")
                
                # Use async helper to handle event loop conflicts
                from code_puppy.utils.async_helper import run_async_in_sync
                
                try:
                    stats = run_async_in_sync(
                        enhancer.index_workspace(directory, max_files)
                    )
                except Exception as e:
                    console.print(f"[bold red]Error during indexing:[/bold red] {e}")
                    if os.getenv("RAG_DEBUG", "false").lower() == "true":
                        import traceback
                        console.print(f"[dim]{traceback.format_exc()}[/dim]")
                    return True
                
                if stats:
                    console.print(f"\n✅ [bold green]Indexing complete![/bold green]")
                    console.print(f"  Files: {stats['processed_files']}")
                    console.print(f"  Chunks: {stats['total_chunks']}")
                    console.print(f"  Time: {stats['duration']:.2f}s")
                    if stats['failed_files'] > 0:
                        console.print(f"  Failed: [red]{stats['failed_files']}[/red]")
                else:
                    console.print("[red]Indexing failed[/red]")
                        
            except Exception as e:
                console.print(f"[bold red]Error indexing:[/bold red] {e}")
                if os.getenv("RAG_DEBUG", "false").lower() == "true":
                    import traceback
                    console.print(f"[dim]{traceback.format_exc()}[/dim]")
                
        elif parts[1] == "debug":
            # Toggle debug mode
            if len(parts) > 2:
                if parts[2] == "on":
                    os.environ["RAG_DEBUG"] = "true"
                    from code_puppy.rag_enhancer_v2 import enable_debug_mode
                    enable_debug_mode()
                    console.print("🐛 [bold green]RAG Debug mode enabled[/bold green]")
                    console.print(f"[dim]Logging to: {os.getcwd()}/rag_debug.log[/dim]")
                elif parts[2] == "off":
                    os.environ["RAG_DEBUG"] = "false"
                    from code_puppy.rag_enhancer_v2 import disable_debug_mode
                    disable_debug_mode()
                    console.print("⚫ [bold yellow]RAG Debug mode disabled[/bold yellow]")
                elif parts[2] == "clear":
                    # Clear debug log
                    from pathlib import Path
                    log_file = Path.cwd() / "rag_debug.log"
                    if log_file.exists():
                        log_file.unlink()
                        console.print("🗑️ [bold green]Debug log cleared[/bold green]")
                    else:
                        console.print("[dim]No debug log found[/dim]")
                elif parts[2] == "show":
                    # Show last lines of debug log
                    from pathlib import Path
                    log_file = Path.cwd() / "rag_debug.log"
                    if log_file.exists():
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                            last_lines = lines[-20:] if len(lines) > 20 else lines
                            console.print("\n[bold cyan]Last 20 lines of debug log:[/bold cyan]")
                            for line in last_lines:
                                console.print(f"[dim]{line.rstrip()}[/dim]")
                    else:
                        console.print("[dim]No debug log found[/dim]")
                else:
                    console.print("[yellow]Usage: /rag debug [on|off|clear|show][/yellow]")
            else:
                current = os.getenv("RAG_DEBUG", "false").lower() == "true"
                console.print(f"Debug mode: {'🐛 ON' if current else '⚫ OFF'}")
                console.print("[dim]Use: /rag debug [on|off|clear|show][/dim]")
        
        elif parts[1] == "stop":
            # This is for stopping async indexing (old system)
            console.print("[dim]Note: Stop command is for old async indexer[/dim]")
                
        else:
            console.print("[yellow]Unknown RAG command. Available commands:[/yellow]")
            console.print("  /rag config  - Configure RAG with interactive interface")
            console.print("  /rag on/off  - Enable or disable RAG")
            console.print("  /rag index   - Index directory for embeddings")
            console.print("  /rag status  - Show current status")
            console.print("  /rag debug   - Debug mode [on|off|clear|show]")
        
        return True
    
    # Generic / or ~ handler - must be LAST
    if command.startswith("/") or command.startswith("~"):
        name = command[1:].split()[0] if len(command) > 1 else ""
        if name:
            console.print(
                f"[yellow]Unknown meta command:[/yellow] {command}\n[dim]Type /help for options.[/dim]"
            )
        else:
            # Show current model ONLY here
            from code_puppy.command_line.model_picker_completion import get_active_model

            current_model = get_active_model()
            console.print(
                f"[bold green]Current Model:[/bold green] [cyan]{current_model}[/cyan]"
            )
        return True
    
    return False
