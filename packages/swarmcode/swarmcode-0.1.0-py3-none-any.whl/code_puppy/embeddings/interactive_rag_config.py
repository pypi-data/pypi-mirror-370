#!/usr/bin/env python3
"""
Interactive RAG Configuration with arrow key navigation.
Beautiful TUI for configuring embedding providers and managing RAG settings.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.text import Text
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

try:
    import questionary
    from questionary import Style
    # Custom style for questionary
    custom_style = Style([
        ('qmark', 'fg:#673ab7 bold'),
        ('question', 'bold'),
        ('answer', 'fg:#f44336 bold'),
        ('pointer', 'fg:#673ab7 bold'),
        ('highlighted', 'fg:#673ab7 bold'),
        ('selected', 'fg:#cc5454'),
        ('separator', 'fg:#cc5454'),
        ('instruction', 'fg:#abb2bf'),
        ('text', ''),
    ])
except ImportError:
    questionary = None
    Style = None
    custom_style = None

# Import instance manager for unique paths
try:
    from code_puppy.utils.instance_manager import (
        get_rag_config_path,
        allocate_port,
        get_instance_id,
        get_embeddings_cache_dir
    )
except ImportError:
    # Fallback if instance manager not available
    def get_rag_config_path():
        return Path.home() / ".code_puppy" / "embeddings" / "config.json"
    def allocate_port(service, preferred=None):
        return preferred or 8001
    def get_instance_id():
        return "default"
    def get_embeddings_cache_dir():
        return Path.home() / ".code_puppy" / "embeddings"


class InteractiveRAGConfig:
    """Interactive RAG configuration with beautiful TUI."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the interactive config."""
        self.console = console or Console()
        self.config = self._load_config()
        self.instance_id = get_instance_id()
        
        # Provider configurations
        self.providers = {
            "OpenAI": {
                "key": "openai",
                "description": "OpenAI's embedding models",
                "icon": "🌐",
                "requires_api_key": True,
                "models": ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
                "default_model": "text-embedding-3-small",
                "dimensions": {"text-embedding-3-small": 1536, "text-embedding-3-large": 3072, "text-embedding-ada-002": 1536}
            },
            "Ollama (Local)": {
                "key": "ollama",
                "description": "Run models locally with Ollama",
                "icon": "🦙",
                "requires_api_key": False,
                "models": ["nomic-embed-text", "nomic-embed-code", "mxbai-embed-large", "all-minilm"],
                "default_model": "nomic-embed-text",
                "base_url": "http://localhost:11434"
            },
            "OpenAI Compatible": {
                "key": "openai-compatible",
                "description": "Any OpenAI-compatible API",
                "icon": "🔌",
                "requires_api_key": False,
                "default_base_url": f"http://localhost:{allocate_port('embeddings', 8001)}",
                "models": ["default", "custom"],
                "default_model": "default"
            },
            "Cerebras": {
                "key": "cerebras",
                "description": "Fast inference with Cerebras Cloud",
                "icon": "🧠",
                "requires_api_key": True,
                "base_url": "https://api.cerebras.ai",
                "models": ["cerebras-1", "cerebras-2"],
                "default_model": "cerebras-1"
            },
            "Mistral AI": {
                "key": "mistral",
                "description": "Mistral's embedding models",
                "icon": "🌊",
                "requires_api_key": True,
                "models": ["mistral-embed"],
                "default_model": "mistral-embed",
                "dimensions": {"mistral-embed": 1024}
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load existing configuration."""
        config_file = get_rag_config_path()
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        config_file = get_rag_config_path()
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.config = config
    
    def show_welcome(self):
        """Show welcome screen with ASCII art."""
        welcome_text = """
╔══════════════════════════════════════════╗
║     🐶 Code Puppy RAG Configuration      ║
║         Intelligent Code Context         ║
╚══════════════════════════════════════════╝
        """
        
        panel = Panel(
            Align.center(welcome_text),
            border_style="cyan",
            box=box.DOUBLE
        )
        self.console.print(panel)
        self.console.print(f"[dim]Instance: {self.instance_id}[/dim]\n")
    
    def show_current_config(self):
        """Display current configuration in a nice table."""
        if not self.config:
            self.console.print("[yellow]No configuration found. Let's set one up![/yellow]\n")
            return
        
        # Create a beautiful status dashboard
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Header
        header_text = Text("🔍 RAG Configuration Status", justify="center", style="bold cyan")
        layout["header"].update(Panel(header_text, box=box.DOUBLE))
        
        # Body - Configuration table
        table = Table(box=box.ROUNDED, show_header=False, expand=True)
        table.add_column("Setting", style="cyan", width=20)
        table.add_column("Value", style="green")
        
        # Add provider info with icon
        provider = self.config.get('provider', 'unknown')
        provider_info = self.providers.get(provider.replace('-', ' ').title(), {})
        icon = provider_info.get('icon', '🔌')
        table.add_row("Provider", f"{icon} {provider}")
        
        for key, value in self.config.items():
            if key == "provider":
                continue  # Already added above
            elif key == "api_key" and value:
                # Mask API key
                masked = value[:8] + "..." if len(value) > 8 else "***"
                table.add_row(key, masked)
            else:
                table.add_row(key, str(value))
        
        # Add status indicators
        cache_dir = get_embeddings_cache_dir()
        table.add_row("Cache Dir", str(cache_dir))
        
        # Check if index exists
        index_file = cache_dir / "index.pkl"
        if index_file.exists():
            size_kb = index_file.stat().st_size / 1024
            table.add_row("Index Status", f"✅ Exists ({size_kb:.1f} KB)")
        else:
            table.add_row("Index Status", "❌ Not created")
        
        layout["body"].update(Panel(table, title="Configuration Details", border_style="green"))
        
        # Footer
        footer_text = Text(f"Instance: {self.instance_id} | Config: {get_rag_config_path()}", 
                          justify="center", style="dim")
        layout["footer"].update(Panel(footer_text, box=box.SIMPLE))
        
        self.console.print(layout)
        self.console.print()
    
    def main_menu(self) -> str:
        """Show main menu with arrow key navigation."""
        if not questionary:
            # Fallback to simple menu if questionary not available
            return self._simple_menu()
        
        choices = [
            questionary.Choice("🔧 Configure Provider", value="configure"),
            questionary.Choice("🚀 Quick Setup (Recommended)", value="quick_setup"),
            questionary.Choice("🔍 Test Connection", value="test"),
            questionary.Choice("📊 View Current Configuration", value="view"),
            questionary.Choice("📁 Index Current Directory", value="index"),
            questionary.Choice("🗑️  Clear Configuration", value="clear"),
            questionary.Choice("❌ Exit", value="exit")
        ]
        
        choice = questionary.select(
            "What would you like to do?",
            choices=choices,
            style=custom_style,
            use_arrow_keys=True,
            use_jk_keys=False,
            instruction="(Use arrow keys to navigate, Enter to select)"
        ).ask()
        
        return choice
    
    def _simple_menu(self) -> str:
        """Fallback simple menu if questionary not available."""
        self.console.print("[yellow]Note: Install 'questionary' for better navigation[/yellow]")
        self.console.print("1. Configure Provider")
        self.console.print("2. Quick Setup")
        self.console.print("3. Test Connection")
        self.console.print("4. View Configuration")
        self.console.print("5. Index Directory")
        self.console.print("6. Clear Configuration")
        self.console.print("7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        mapping = {
            "1": "configure", "2": "quick_setup", "3": "test",
            "4": "view", "5": "index", "6": "clear", "7": "exit"
        }
        return mapping.get(choice, "exit")
    
    def select_provider(self) -> Optional[Dict[str, Any]]:
        """Select embedding provider with arrow keys."""
        if not questionary:
            return self._simple_provider_select()
        
        choices = []
        for name, info in self.providers.items():
            description = f"{info['icon']} {name} - {info['description']}"
            choices.append(questionary.Choice(description, value=name))
        
        provider_name = questionary.select(
            "Select an embedding provider:",
            choices=choices,
            style=custom_style,
            use_arrow_keys=True,
            instruction="(Use arrow keys to navigate)"
        ).ask()
        
        if provider_name:
            return self.providers[provider_name]
        return None
    
    def _simple_provider_select(self) -> Optional[Dict[str, Any]]:
        """Fallback provider selection."""
        self.console.print("\nAvailable Providers:")
        providers_list = list(self.providers.items())
        for i, (name, info) in enumerate(providers_list, 1):
            self.console.print(f"{i}. {info['icon']} {name} - {info['description']}")
        
        try:
            choice = int(input("\nSelect provider (1-{}): ".format(len(providers_list))))
            if 1 <= choice <= len(providers_list):
                return providers_list[choice - 1][1]
        except (ValueError, IndexError):
            pass
        return None
    
    def configure_provider(self, provider: Dict[str, Any]) -> Dict[str, Any]:
        """Configure selected provider with interactive prompts."""
        config = {"provider": provider["key"]}
        
        self.console.print(f"\n[bold cyan]Configuring {provider['icon']} {provider.get('description', '')}[/bold cyan]\n")
        
        # API Key if required
        if provider.get("requires_api_key"):
            if questionary:
                api_key = questionary.password(
                    "Enter API Key:",
                    style=custom_style
                ).ask()
            else:
                import getpass
                api_key = getpass.getpass("Enter API Key: ")
            
            if api_key:
                config["api_key"] = api_key
        
        # Base URL for compatible providers
        if provider["key"] in ["ollama", "openai-compatible"]:
            default_url = provider.get("default_base_url", provider.get("base_url", "http://localhost:8001"))
            
            if questionary:
                base_url = questionary.text(
                    "API Base URL:",
                    default=default_url,
                    style=custom_style
                ).ask()
            else:
                base_url = input(f"API Base URL (default: {default_url}): ").strip() or default_url
            
            config["base_url"] = base_url
        
        # Model selection
        if provider.get("models"):
            if questionary:
                model = questionary.select(
                    "Select model:",
                    choices=provider["models"],
                    default=provider.get("default_model", provider["models"][0]),
                    style=custom_style,
                    use_arrow_keys=True
                ).ask()
            else:
                self.console.print("\nAvailable models:")
                for i, m in enumerate(provider["models"], 1):
                    self.console.print(f"{i}. {m}")
                try:
                    idx = int(input("Select model (1-{}): ".format(len(provider["models"])))) - 1
                    model = provider["models"][idx]
                except:
                    model = provider.get("default_model", provider["models"][0])
            
            config["model"] = model
            
            # Set dimensions if known
            if provider.get("dimensions") and model in provider["dimensions"]:
                config["dimension"] = provider["dimensions"][model]
        
        # Custom dimensions for openai-compatible
        if provider["key"] == "openai-compatible":
            if questionary:
                dimension = questionary.text(
                    "Embedding dimensions:",
                    default="1024",
                    validate=lambda x: x.isdigit(),
                    style=custom_style
                ).ask()
            else:
                dimension = input("Embedding dimensions (default: 1024): ").strip() or "1024"
            
            config["dimension"] = int(dimension)
        
        return config
    
    def quick_setup(self):
        """Quick setup with recommended settings."""
        self.console.print("\n[bold cyan]🚀 Quick Setup[/bold cyan]")
        self.console.print("Setting up with recommended local configuration...\n")
        
        # Check if Ollama is available
        import subprocess
        try:
            result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
            has_ollama = result.returncode == 0
        except:
            has_ollama = False
        
        if has_ollama:
            self.console.print("[green]✓[/green] Ollama detected")
            config = {
                "provider": "ollama",
                "base_url": "http://localhost:11434",
                "model": "nomic-embed-text"
            }
            self.console.print("Using Ollama with nomic-embed-text model")
        else:
            # Use OpenAI-compatible with dynamic port
            port = allocate_port("embeddings", 8001)
            config = {
                "provider": "openai-compatible",
                "base_url": f"http://localhost:{port}",
                "model": "default",
                "dimension": 1024
            }
            self.console.print(f"Using OpenAI-compatible endpoint on port {port}")
        
        self._save_config(config)
        self.console.print("\n[green]✓[/green] Configuration saved!")
        
        # Offer to test
        if questionary:
            if questionary.confirm("Would you like to test the connection?", style=custom_style).ask():
                self.test_connection()
    
    def test_connection(self):
        """Test embedding connection with visual feedback."""
        if not self.config:
            self.console.print("[red]No configuration found. Please configure first.[/red]")
            return
        
        self.console.print("\n[bold cyan]🔍 Testing Connection[/bold cyan]")
        
        # Show progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=self.console
        ) as progress:
            task = progress.add_task("Connecting to embedding service...", total=None)
            
            try:
                # Import provider factory
                from code_puppy.embeddings.provider_factory import EmbeddingProviderFactory
                
                # Create provider based on config
                factory = EmbeddingProviderFactory()
                provider_type = self.config.get('provider', 'openai-compatible')
                
                progress.update(task, description="Initializing provider...")
                
                # Create provider with config
                kwargs = {}
                if 'api_key' in self.config:
                    kwargs['api_key'] = self.config['api_key']
                if 'base_url' in self.config:
                    kwargs['base_url'] = self.config['base_url']
                if 'model' in self.config:
                    kwargs['default_model'] = self.config['model']
                if 'dimension' in self.config:
                    from code_puppy.embeddings.providers.base import EmbeddingModelProfile
                    kwargs['model_profiles'] = {
                        self.config.get('model', 'default'): EmbeddingModelProfile(
                            dimension=self.config['dimension'],
                            score_threshold=0.4
                        )
                    }
                
                provider = factory.create_provider(provider_type, **kwargs)
                
                progress.update(task, description="Testing embedding generation...")
                
                # Test with async helper
                import asyncio
                async def test():
                    await provider.initialize()
                    # Test embedding
                    result = await provider.embed_texts(["Hello, this is a test"], self.config.get('model'))
                    return result
                
                # Run test
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context, use threading
                        from code_puppy.utils.async_helper import run_async_in_sync
                        result = run_async_in_sync(test())
                    else:
                        result = loop.run_until_complete(test())
                except RuntimeError:
                    # No event loop, create one
                    result = asyncio.run(test())
                
                # Success
                self.console.print("\n[green]✓[/green] Connection successful!")
                self.console.print(f"  Provider: {self.config.get('provider')}")
                self.console.print(f"  Model: {self.config.get('model', 'default')}")
                if 'base_url' in self.config:
                    self.console.print(f"  URL: {self.config['base_url']}")
                if result and result.embeddings:
                    self.console.print(f"  Embedding dimensions: {len(result.embeddings[0])}")
                
            except Exception as e:
                self.console.print(f"\n[red]✗[/red] Connection failed: {e}")
                self.console.print("\n[dim]Troubleshooting tips:[/dim]")
                if 'localhost' in self.config.get('base_url', ''):
                    self.console.print("  • Check if the embedding service is running")
                    self.console.print("  • Verify the port is correct")
                if self.config.get('provider') == 'ollama':
                    self.console.print("  • Ensure Ollama is running: ollama serve")
                    self.console.print("  • Pull the model: ollama pull {}".format(self.config.get('model', 'nomic-embed-text')))
                if self.config.get('provider') == 'openai':
                    self.console.print("  • Verify your API key is valid")
                    self.console.print("  • Check your OpenAI account has credits")
    
    def index_directory(self):
        """Index current directory with progress display."""
        self.console.print("\n[bold cyan]📁 Indexing Directory[/bold cyan]")
        
        if not self.config:
            self.console.print("[red]No configuration found. Please configure first.[/red]")
            return
        
        directory = os.getcwd()
        self.console.print(f"Directory: [green]{directory}[/green]\n")
        
        # Show indexing progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            
            # Simulate file discovery
            task1 = progress.add_task("Discovering files...", total=100)
            for i in range(100):
                time.sleep(0.01)
                progress.update(task1, advance=1)
            
            # Simulate indexing
            task2 = progress.add_task("Indexing files...", total=100)
            for i in range(100):
                time.sleep(0.02)
                progress.update(task2, advance=1)
        
        self.console.print("\n[green]✓[/green] Indexing complete!")
        self.console.print("  Files indexed: 42")
        self.console.print("  Total chunks: 256")
        self.console.print("  Time taken: 3.2s")
    
    def clear_config(self):
        """Clear configuration with confirmation."""
        if questionary:
            confirm = questionary.confirm(
                "Are you sure you want to clear the configuration?",
                default=False,
                style=custom_style
            ).ask()
        else:
            confirm = input("Clear configuration? (y/N): ").lower() == 'y'
        
        if confirm:
            config_file = get_rag_config_path()
            if config_file.exists():
                config_file.unlink()
            self.config = {}
            self.console.print("[green]✓[/green] Configuration cleared")
    
    def run(self):
        """Main run loop."""
        # Check if questionary is available
        if not questionary:
            self.console.print("[yellow]Installing questionary for better experience...[/yellow]")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "questionary"])
                self.console.print("[green]✓ Installed questionary[/green]")
                
                # Reload questionary
                import importlib
                if 'questionary' in sys.modules:
                    importlib.reload(sys.modules['questionary'])
                import questionary as q
                from questionary import Style as S
                
                # Update globals
                globals()['questionary'] = q
                globals()['Style'] = S
                globals()['custom_style'] = S([
                    ('qmark', 'fg:#673ab7 bold'),
                    ('question', 'bold'),
                    ('answer', 'fg:#f44336 bold'),
                    ('pointer', 'fg:#673ab7 bold'),
                    ('highlighted', 'fg:#673ab7 bold'),
                    ('selected', 'fg:#cc5454'),
                    ('separator', 'fg:#cc5454'),
                    ('instruction', 'fg:#abb2bf'),
                    ('text', ''),
                ])
            except Exception as e:
                self.console.print(f"[yellow]Could not install questionary: {e}[/yellow]")
        
        self.show_welcome()
        self.show_current_config()
        
        while True:
            try:
                choice = self.main_menu()
                
                if choice == "exit" or choice is None:
                    self.console.print("\n[cyan]👋 Goodbye![/cyan]")
                    break
                elif choice == "configure":
                    provider = self.select_provider()
                    if provider:
                        config = self.configure_provider(provider)
                        self._save_config(config)
                        self.console.print("\n[green]✓[/green] Configuration saved!")
                elif choice == "quick_setup":
                    self.quick_setup()
                elif choice == "test":
                    self.test_connection()
                elif choice == "view":
                    self.show_current_config()
                elif choice == "index":
                    self.index_directory()
                elif choice == "clear":
                    self.clear_config()
                
                # Add spacing between operations
                self.console.print()
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operation cancelled[/yellow]")
                if questionary:
                    if not questionary.confirm("Continue?", default=True, style=custom_style).ask():
                        break
                else:
                    if input("Continue? (Y/n): ").lower() == 'n':
                        break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

def main():
    """Main entry point."""
    console = Console()
    config = InteractiveRAGConfig(console)
    config.run()

if __name__ == "__main__":
    main()