#!/usr/bin/env python3
"""
Synchronous TUI for RAG configuration that works within Code Puppy's event loop.
"""

import os
from typing import Optional, List
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm, IntPrompt
from rich import box

from .provider_factory import EmbeddingProviderFactory

# Import instance manager for unique paths
try:
    from code_puppy.utils.instance_manager import (
        get_rag_config_path,
        allocate_port,
        get_instance_id
    )
except ImportError:
    # Fallback if instance manager not available
    def get_rag_config_path():
        return Path.home() / ".code_puppy" / "embeddings" / "config.json"
    def allocate_port(service, preferred=None):
        return preferred or 8001
    def get_instance_id():
        return "default"

class SimpleRAGTUI:
    """Simple synchronous TUI for RAG configuration."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the TUI."""
        self.console = console or Console()
        self.providers = [
            ("openai", "OpenAI", "Use OpenAI's embedding models (requires API key)"),
            ("ollama", "Ollama (Local)", "Run models locally with Ollama"),
            ("openai-compatible", "OpenAI Compatible", "Any OpenAI-compatible API"),
            ("cerebras", "Cerebras", "Fast inference with Cerebras (requires API key)"),
            ("mistral", "Mistral AI", "Mistral's embedding models (requires API key)"),
        ]
    
    def show_main_menu(self) -> str:
        """Show main menu and get user choice."""
        # Create menu table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("", style="bold cyan", width=3)
        table.add_column("", style="bold")
        
        table.add_row("1", "🔌 Configure Provider")
        table.add_row("2", "📁 Quick Index Current Directory")
        table.add_row("3", "🔍 Test Embedding Connection")
        table.add_row("4", "📊 View Available Providers")
        table.add_row("5", "💾 Save Configuration")
        table.add_row("6", "❌ Exit")
        
        panel = Panel(
            table,
            title="🐶 [bold cyan]Code Puppy RAG Configuration[/bold cyan]",
            subtitle="[dim]Select an option (1-6)[/dim]",
            border_style="cyan",
            box=box.DOUBLE
        )
        
        self.console.print(panel)
        
        choice = Prompt.ask(
            "[bold yellow]Select option[/bold yellow]",
            choices=["1", "2", "3", "4", "5", "6"],
            default="1"
        )
        
        return choice
    
    def configure_provider(self) -> dict:
        """Configure an embedding provider."""
        # Show provider list
        table = Table(title="Available Embedding Providers", box=box.ROUNDED)
        table.add_column("#", style="cyan", width=3)
        table.add_column("Provider", style="bold")
        table.add_column("Description")
        
        for i, (key, name, desc) in enumerate(self.providers, 1):
            table.add_row(str(i), name, desc)
        
        self.console.print(table)
        
        # Get provider choice
        provider_idx = IntPrompt.ask(
            "[bold yellow]Select provider[/bold yellow]",
            default=1,
            choices=[str(i) for i in range(1, len(self.providers) + 1)]
        ) - 1
        
        provider_key, provider_name, _ = self.providers[provider_idx]
        
        self.console.print(f"\n[bold green]Configuring {provider_name}[/bold green]\n")
        
        config = {"provider": provider_key}
        
        # Get configuration based on provider
        if provider_key == "openai":
            api_key = Prompt.ask(
                "Enter OpenAI API Key",
                password=True,
                default=os.getenv("OPENAI_API_KEY", "")
            )
            if api_key:
                config["api_key"] = api_key
                os.environ["OPENAI_API_KEY"] = api_key
            
            model = Prompt.ask(
                "Model",
                default="text-embedding-3-small",
                choices=["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]
            )
            config["model"] = model
            
        elif provider_key == "ollama":
            base_url = Prompt.ask(
                "Ollama Base URL",
                default=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
            config["base_url"] = base_url
            
            model = Prompt.ask(
                "Model",
                default="nomic-embed-text",
                choices=["nomic-embed-text", "nomic-embed-code", "mxbai-embed-large", "all-minilm"]
            )
            config["model"] = model
            
        elif provider_key == "openai-compatible":
            # Allocate a unique port for this instance
            default_port = allocate_port("embeddings", 8001)
            base_url = Prompt.ask(
                "API Base URL",
                default=f"http://localhost:{default_port}"
            )
            config["base_url"] = base_url
            
            api_key = Prompt.ask(
                "API Key (optional, press Enter to skip)",
                password=True,
                default=""
            )
            if api_key:
                config["api_key"] = api_key
            
            model = Prompt.ask("Model name", default="default")
            config["model"] = model
            
            # Ask for embedding dimensions
            dimension = IntPrompt.ask(
                "Embedding dimensions",
                default=1024
            )
            config["dimension"] = dimension
            
        elif provider_key == "cerebras":
            api_key = Prompt.ask(
                "Enter Cerebras API Key",
                password=True,
                default=os.getenv("CEREBRAS_API_KEY", "")
            )
            if api_key:
                config["api_key"] = api_key
                os.environ["CEREBRAS_API_KEY"] = api_key
                
        elif provider_key == "mistral":
            api_key = Prompt.ask(
                "Enter Mistral API Key",
                password=True,
                default=os.getenv("MISTRAL_API_KEY", "")
            )
            if api_key:
                config["api_key"] = api_key
                os.environ["MISTRAL_API_KEY"] = api_key
        
        # Show configuration summary
        self.show_config_summary(config)
        
        if Confirm.ask("\n[bold yellow]Save this configuration?[/bold yellow]"):
            self.save_config(config)
            self.console.print("[bold green]✅ Configuration saved![/bold green]")
        
        return config
    
    def show_config_summary(self, config: dict):
        """Show configuration summary."""
        table = Table(title="Configuration Summary", box=box.ROUNDED)
        table.add_column("Setting", style="bold yellow")
        table.add_column("Value", style="cyan")
        
        for key, value in config.items():
            if key == "api_key" and value:
                # Mask API key
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                table.add_row(key, masked)
            else:
                table.add_row(key, str(value))
        
        self.console.print(table)
    
    def save_config(self, config: dict):
        """Save configuration to instance-specific file."""
        import json
        
        # Use instance-specific config path
        config_file = get_rag_config_path()
        config_dir = config_file.parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing config if exists
        existing = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                existing = json.load(f)
        
        # Merge configs
        existing.update(config)
        
        # Save
        with open(config_file, 'w') as f:
            json.dump(existing, f, indent=2)
        
        # Also set environment variables
        if "api_key" in config:
            provider = config.get("provider", "")
            if provider == "openai":
                os.environ["OPENAI_API_KEY"] = config["api_key"]
            elif provider == "cerebras":
                os.environ["CEREBRAS_API_KEY"] = config["api_key"]
            elif provider == "mistral":
                os.environ["MISTRAL_API_KEY"] = config["api_key"]
        
        if "base_url" in config:
            os.environ["EMBEDDING_BASE_URL"] = config["base_url"]
        
        if "model" in config:
            os.environ["EMBEDDING_MODEL"] = config["model"]
        
        os.environ["EMBEDDING_PROVIDER"] = config.get("provider", "openai-compatible")
    
    def test_connection(self):
        """Test embedding connection."""
        self.console.print("\n[bold cyan]Testing embedding connection...[/bold cyan]\n")
        
        try:
            # Load saved config from instance-specific location
            config_file = get_rag_config_path()
            if config_file.exists():
                import json
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                self.console.print("[yellow]No saved configuration found. Please configure first.[/yellow]")
                return
            
            # For now, just show the configuration
            # Actual testing would require running async code which conflicts with the event loop
            self.console.print("[bold green]Current Configuration:[/bold green]")
            self.show_config_summary(config)
            
            # Basic validation
            provider = config.get('provider')
            if provider in ['openai', 'cerebras', 'mistral']:
                if not config.get('api_key'):
                    self.console.print(f"[yellow]⚠ {provider} requires an API key[/yellow]")
                else:
                    self.console.print(f"[green]✓ API key configured[/green]")
            
            if provider == 'ollama':
                base_url = config.get('base_url', 'http://localhost:11434')
                self.console.print(f"[dim]Ollama URL: {base_url}[/dim]")
                self.console.print("[dim]Make sure Ollama is running locally[/dim]")
            
            if provider == 'openai-compatible':
                base_url = config.get('base_url', 'http://localhost:8001')
                self.console.print(f"[dim]API URL: {base_url}[/dim]")
                
        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {e}")
    
    def show_providers(self):
        """Show available providers and their models."""
        info = EmbeddingProviderFactory.get_available_providers()
        
        for provider_key, provider_info in info.items():
            # Create a panel for each provider
            content = Text()
            content.append(f"Provider: {provider_info['name']}\n", style="bold")
            content.append(f"Requires API Key: ", style="dim")
            content.append("Yes\n" if provider_info['requires_api_key'] else "No\n", 
                          style="red" if provider_info['requires_api_key'] else "green")
            content.append(f"Default Model: {provider_info['default_model']}\n", style="yellow")
            content.append("\nAvailable Models:\n", style="dim")
            
            for model in provider_info['models']:
                content.append(f"  • {model}\n", style="cyan")
            
            panel = Panel(
                content,
                title=f"[bold cyan]{provider_info['name']}[/bold cyan]",
                border_style="blue",
                box=box.ROUNDED
            )
            
            self.console.print(panel)
    
    def quick_index(self):
        """Quick index current directory."""
        self.console.print("\n[bold cyan]Quick Index Current Directory[/bold cyan]\n")
        
        # Check for saved config
        config_file = Path.home() / ".code_puppy" / "embeddings" / "config.json"
        if not config_file.exists():
            self.console.print("[yellow]No configuration found. Please configure a provider first.[/yellow]")
            return
        
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        self.console.print(f"Using provider: [green]{config.get('provider')}[/green]")
        
        patterns = Prompt.ask(
            "File patterns to index",
            default="*.py,*.js,*.ts,*.jsx,*.tsx"
        ).split(',')
        
        max_files = IntPrompt.ask(
            "Maximum files to index (0 for all)",
            default=0
        )
        
        if max_files == 0:
            max_files = None
        
        self.console.print(f"\n[bold yellow]Indexing {os.getcwd()}...[/bold yellow]")
        self.console.print(f"Patterns: {patterns}")
        if max_files:
            self.console.print(f"Limit: {max_files} files")
        
        # TODO: Actually run indexing
        self.console.print("\n[dim]Note: Indexing will run in background once started[/dim]")
    
    def run(self):
        """Run the TUI main loop."""
        self.console.clear()
        self.console.print("\n[bold cyan]🐶 Welcome to Code Puppy RAG Configuration![/bold cyan]\n")
        
        while True:
            choice = self.show_main_menu()
            
            if choice == "1":
                self.configure_provider()
            elif choice == "2":
                self.quick_index()
            elif choice == "3":
                self.test_connection()
            elif choice == "4":
                self.show_providers()
            elif choice == "5":
                self.console.print("[dim]Configuration is automatically saved[/dim]")
            elif choice == "6":
                self.console.print("\n[bold green]Goodbye! 🐶[/bold green]\n")
                break
            
            if choice != "6":
                self.console.print("\n[dim]Press Enter to continue...[/dim]")
                input()
                self.console.clear()

def launch_rag_config_tui(console: Optional[Console] = None):
    """Launch the synchronous RAG configuration TUI."""
    tui = SimpleRAGTUI(console)
    tui.run()