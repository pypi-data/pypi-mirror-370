#!/usr/bin/env python3
"""
Beautiful TUI for RAG configuration and management.
Uses rich and prompt_toolkit for an interactive experience.
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich import box

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout as PTLayout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, ConditionalContainer
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Button, RadioList, TextArea, Label, Frame, Box
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.filters import Condition

from .provider_factory import EmbeddingProviderFactory
from .embedding_manager import EmbeddingManager, IndexingState

class TUIState(Enum):
    """States of the TUI."""
    MAIN_MENU = "main_menu"
    PROVIDER_SELECTION = "provider_selection"
    PROVIDER_CONFIG = "provider_config"
    INDEX_CONFIG = "index_config"
    INDEXING = "indexing"
    SEARCH = "search"
    STATUS = "status"

@dataclass
class RAGConfig:
    """Configuration for RAG system."""
    provider: str = "openai-compatible"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    directory: str = "."
    patterns: List[str] = None
    ignore_patterns: List[str] = None
    
    def __post_init__(self):
        if self.patterns is None:
            self.patterns = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"]
        if self.ignore_patterns is None:
            self.ignore_patterns = ["*node_modules*", "*__pycache__*", "*.git*"]

class RAGTUI:
    """Terminal User Interface for RAG configuration."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the TUI."""
        self.console = console or Console()
        self.config = RAGConfig()
        self.manager: Optional[EmbeddingManager] = None
        self.state = TUIState.MAIN_MENU
        self.running = True
        
        # Create key bindings
        self.kb = KeyBindings()
        self._setup_keybindings()
        
        # Current selections
        self.current_menu_index = 0
        self.provider_index = 0
        
        # Available providers
        self.providers = [
            ("openai", "OpenAI", "Use OpenAI's embedding models"),
            ("ollama", "Ollama (Local)", "Run models locally with Ollama"),
            ("openai-compatible", "OpenAI Compatible", "Any OpenAI-compatible API"),
            ("cerebras", "Cerebras", "Fast inference with Cerebras"),
            ("mistral", "Mistral AI", "Mistral's embedding models"),
        ]
        
        # Menu items
        self.main_menu_items = [
            ("🔌 Configure Provider", self.show_provider_selection),
            ("📁 Select Directory", self.show_directory_selection),
            ("🚀 Start Indexing", self.start_indexing),
            ("🔍 Search", self.show_search),
            ("📊 View Status", self.show_status),
            ("❌ Exit", self.exit_tui),
        ]
    
    def _setup_keybindings(self):
        """Set up keyboard shortcuts."""
        
        @self.kb.add('c-c')
        @self.kb.add('c-q')
        def _(event):
            """Exit on Ctrl+C or Ctrl+Q."""
            self.running = False
            event.app.exit()
        
        @self.kb.add('escape')
        def _(event):
            """Go back on Escape."""
            if self.state != TUIState.MAIN_MENU:
                self.state = TUIState.MAIN_MENU
        
        @self.kb.add('up')
        def _(event):
            """Navigate up."""
            if self.state == TUIState.MAIN_MENU:
                self.current_menu_index = max(0, self.current_menu_index - 1)
            elif self.state == TUIState.PROVIDER_SELECTION:
                self.provider_index = max(0, self.provider_index - 1)
        
        @self.kb.add('down')
        def _(event):
            """Navigate down."""
            if self.state == TUIState.MAIN_MENU:
                self.current_menu_index = min(
                    len(self.main_menu_items) - 1,
                    self.current_menu_index + 1
                )
            elif self.state == TUIState.PROVIDER_SELECTION:
                self.provider_index = min(
                    len(self.providers) - 1,
                    self.provider_index + 1
                )
        
        @self.kb.add('enter')
        def _(event):
            """Select current item."""
            if self.state == TUIState.MAIN_MENU:
                _, action = self.main_menu_items[self.current_menu_index]
                action()
            elif self.state == TUIState.PROVIDER_SELECTION:
                self.select_provider()
    
    def create_main_menu(self) -> Panel:
        """Create the main menu panel."""
        # Create menu table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("", style="bold")
        
        for i, (label, _) in enumerate(self.main_menu_items):
            if i == self.current_menu_index:
                # Highlight selected item
                table.add_row(f"▶ {label}", style="bold cyan")
            else:
                table.add_row(f"  {label}", style="dim")
        
        # Create status summary
        status_text = Text()
        status_text.append("Provider: ", style="bold")
        status_text.append(f"{self.config.provider}\n", style="green")
        status_text.append("Directory: ", style="bold")
        status_text.append(f"{self.config.directory}\n", style="yellow")
        
        if self.manager and self.manager._initialized:
            status_text.append("Status: ", style="bold")
            status_text.append("✅ Ready\n", style="green")
            
            # Show index stats
            total_files = len(self.manager.index)
            total_chunks = sum(len(entries) for entries in self.manager.index.values())
            status_text.append(f"Indexed: {total_files} files, {total_chunks} chunks", style="dim")
        else:
            status_text.append("Status: ", style="bold")
            status_text.append("⚠️ Not initialized\n", style="yellow")
        
        # Combine menu and status
        layout = Table.grid(padding=1)
        layout.add_column()
        layout.add_row(Panel(status_text, title="Current Configuration", border_style="dim"))
        layout.add_row(Panel(table, title="Menu (↑↓ to navigate, Enter to select)", border_style="cyan"))
        
        return Panel(
            layout,
            title="🐶 [bold cyan]Code Puppy RAG Configuration[/bold cyan]",
            subtitle="[dim]Press Esc to go back, Ctrl+Q to exit[/dim]",
            border_style="cyan",
            box=box.DOUBLE
        )
    
    def create_provider_selection(self) -> Panel:
        """Create provider selection panel."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("", style="bold", width=20)
        table.add_column("", style="dim")
        
        for i, (key, name, desc) in enumerate(self.providers):
            if i == self.provider_index:
                table.add_row(f"▶ {name}", desc, style="bold cyan")
            else:
                table.add_row(f"  {name}", desc, style="dim")
        
        return Panel(
            table,
            title="🔌 [bold cyan]Select Embedding Provider[/bold cyan]",
            subtitle="[dim]↑↓ to navigate, Enter to select, Esc to cancel[/dim]",
            border_style="cyan",
            box=box.ROUNDED
        )
    
    def create_provider_config(self) -> Panel:
        """Create provider configuration panel."""
        config_items = []
        
        provider_key = self.providers[self.provider_index][0]
        provider_name = self.providers[self.provider_index][1]
        
        # Show configuration fields based on provider
        if provider_key == "openai":
            config_items.append(("API Key", self.config.api_key or "Not set"))
            config_items.append(("Model", self.config.model or "text-embedding-3-small"))
        elif provider_key == "ollama":
            config_items.append(("Base URL", self.config.base_url or "http://localhost:11434"))
            config_items.append(("Model", self.config.model or "nomic-embed-text"))
        elif provider_key == "openai-compatible":
            config_items.append(("Base URL", self.config.base_url or "http://localhost:8001"))
            config_items.append(("API Key", self.config.api_key or "Optional"))
            config_items.append(("Model", self.config.model or "default"))
        elif provider_key == "cerebras":
            config_items.append(("API Key", self.config.api_key or "Not set"))
        elif provider_key == "mistral":
            config_items.append(("API Key", self.config.api_key or "Not set"))
        
        # Create configuration table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Field", style="bold yellow", width=15)
        table.add_column("Value", style="cyan")
        
        for field, value in config_items:
            table.add_row(field + ":", value)
        
        # Add instructions
        instructions = Text()
        instructions.append("\n📝 Configuration will be saved to environment\n", style="dim")
        instructions.append("Press 'e' to edit, Enter to confirm, Esc to cancel", style="dim italic")
        
        layout = Table.grid()
        layout.add_column()
        layout.add_row(table)
        layout.add_row(instructions)
        
        return Panel(
            layout,
            title=f"⚙️ [bold cyan]Configure {provider_name}[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED
        )
    
    def create_indexing_panel(self) -> Panel:
        """Create indexing progress panel."""
        if not self.manager:
            return Panel(
                "[red]Manager not initialized[/red]",
                title="❌ Error",
                border_style="red"
            )
        
        progress = self.manager.progress
        
        # Create progress bar
        if progress.total_files > 0:
            bar_width = 40
            filled = int(bar_width * progress.progress_percent / 100)
            empty = bar_width - filled
            progress_bar = Text()
            progress_bar.append("█" * filled, style="green")
            progress_bar.append("░" * empty, style="dim")
            progress_bar.append(f" {progress.progress_percent:.1f}%", style="yellow")
        else:
            progress_bar = Text("Preparing...", style="dim")
        
        # Create status table
        table = Table(show_header=False, box=None)
        table.add_column("", style="bold", width=20)
        table.add_column("")
        
        table.add_row("State:", str(progress.state.value).upper(), style="cyan")
        table.add_row("Progress:", progress_bar)
        table.add_row("Files:", f"{progress.processed_files}/{progress.total_files}")
        table.add_row("Chunks:", str(progress.total_chunks), style="yellow")
        table.add_row("Failed:", str(progress.failed_files), style="red" if progress.failed_files > 0 else "green")
        
        if progress.current_file:
            current = Path(progress.current_file).name
            if len(current) > 40:
                current = current[:37] + "..."
            table.add_row("Current:", current, style="dim")
        
        if progress.error:
            table.add_row("Error:", progress.error, style="red")
        
        return Panel(
            table,
            title="📚 [bold cyan]Indexing Progress[/bold cyan]",
            subtitle="[dim]Press Esc to return to menu[/dim]",
            border_style="cyan" if progress.state == IndexingState.INDEXING else "green",
            box=box.ROUNDED
        )
    
    def create_search_panel(self) -> Panel:
        """Create search interface panel."""
        instructions = Text()
        instructions.append("🔍 Enter your search query\n\n", style="bold cyan")
        instructions.append("Type your query and press Enter to search\n", style="dim")
        instructions.append("Press Esc to return to menu", style="dim italic")
        
        return Panel(
            instructions,
            title="🔍 [bold cyan]Search Indexed Content[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED
        )
    
    def create_status_panel(self) -> Panel:
        """Create detailed status panel."""
        if not self.manager:
            status_text = Text("RAG system not initialized", style="yellow")
        else:
            table = Table(show_header=False, box=None)
            table.add_column("", style="bold", width=25)
            table.add_column("")
            
            # System status
            table.add_row("System Status:", "✅ Initialized" if self.manager._initialized else "❌ Not initialized")
            table.add_row("Provider:", str(self.manager.provider) if self.manager.provider else "None")
            table.add_row("Cache Directory:", str(self.manager.cache_dir))
            
            # Index statistics
            table.add_row("", "")  # Spacer
            table.add_row("[bold cyan]Index Statistics[/bold cyan]", "")
            table.add_row("Total Files:", str(len(self.manager.index)))
            
            total_chunks = sum(len(entries) for entries in self.manager.index.values())
            table.add_row("Total Chunks:", str(total_chunks))
            
            # Memory estimate (rough)
            memory_mb = (total_chunks * 1024 * 4) / (1024 * 1024)  # Assuming 1024 dims, 4 bytes per float
            table.add_row("Estimated Memory:", f"{memory_mb:.2f} MB")
            
            # Recent activity
            if self.manager.progress.started_at:
                table.add_row("", "")  # Spacer
                table.add_row("[bold cyan]Recent Activity[/bold cyan]", "")
                table.add_row("Last Indexing:", str(self.manager.progress.started_at))
                if self.manager.progress.completed_at:
                    duration = (self.manager.progress.completed_at - self.manager.progress.started_at).total_seconds()
                    table.add_row("Duration:", f"{duration:.2f} seconds")
            
            status_text = table
        
        return Panel(
            status_text,
            title="📊 [bold cyan]RAG System Status[/bold cyan]",
            subtitle="[dim]Press Esc to return to menu[/dim]",
            border_style="cyan",
            box=box.ROUNDED
        )
    
    def render(self) -> Panel:
        """Render the current state."""
        if self.state == TUIState.MAIN_MENU:
            return self.create_main_menu()
        elif self.state == TUIState.PROVIDER_SELECTION:
            return self.create_provider_selection()
        elif self.state == TUIState.PROVIDER_CONFIG:
            return self.create_provider_config()
        elif self.state == TUIState.INDEXING:
            return self.create_indexing_panel()
        elif self.state == TUIState.SEARCH:
            return self.create_search_panel()
        elif self.state == TUIState.STATUS:
            return self.create_status_panel()
        else:
            return Panel("Unknown state", style="red")
    
    def show_provider_selection(self):
        """Show provider selection screen."""
        self.state = TUIState.PROVIDER_SELECTION
    
    def select_provider(self):
        """Select the current provider."""
        provider_key = self.providers[self.provider_index][0]
        self.config.provider = provider_key
        self.state = TUIState.PROVIDER_CONFIG
    
    def show_directory_selection(self):
        """Show directory selection dialog."""
        # For now, just use current directory
        # TODO: Add file browser
        self.config.directory = os.getcwd()
        self.console.print(f"[green]Directory set to: {self.config.directory}[/green]")
        self.state = TUIState.MAIN_MENU
    
    async def start_indexing(self):
        """Start the indexing process."""
        self.state = TUIState.INDEXING
        
        # Initialize manager if needed
        if not self.manager:
            self.manager = EmbeddingManager(console=self.console)
            
            # Configure based on provider
            provider_config = {
                "provider": self.config.provider,
                "api_key": self.config.api_key,
                "base_url": self.config.base_url,
                "model": self.config.model
            }
            
            success = await self.manager.initialize(provider_config)
            if not success:
                self.console.print("[red]Failed to initialize manager[/red]")
                self.state = TUIState.MAIN_MENU
                return
        
        # Start indexing
        try:
            stats = await self.manager.index_directory(
                self.config.directory,
                patterns=self.config.patterns,
                ignore_patterns=self.config.ignore_patterns,
                show_progress=True
            )
            
            self.console.print(f"\n[green]✅ Indexing complete![/green]")
            self.console.print(f"Indexed {stats['processed_files']} files in {stats['duration']:.2f} seconds")
            
        except Exception as e:
            self.console.print(f"[red]Indexing failed: {e}[/red]")
        
        self.state = TUIState.MAIN_MENU
    
    def show_search(self):
        """Show search interface."""
        self.state = TUIState.SEARCH
        # TODO: Implement search UI
    
    def show_status(self):
        """Show detailed status."""
        self.state = TUIState.STATUS
    
    def exit_tui(self):
        """Exit the TUI."""
        self.running = False
    
    async def run(self):
        """Run the TUI main loop."""
        with Live(self.render(), console=self.console, refresh_per_second=4) as live:
            while self.running:
                # Update display
                live.update(self.render())
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.1)
                
                # Handle any async operations
                if self.state == TUIState.INDEXING and self.manager:
                    if self.manager.progress.state != IndexingState.INDEXING:
                        # Indexing finished
                        self.state = TUIState.MAIN_MENU

async def launch_rag_tui(console: Optional[Console] = None):
    """Launch the RAG configuration TUI."""
    tui = RAGTUI(console)
    
    # Create a simple interactive loop
    console = console or Console()
    
    while tui.running:
        # Clear screen
        console.clear()
        
        # Render current state
        console.print(tui.render())
        
        # Get input based on state
        if tui.state == TUIState.MAIN_MENU:
            console.print("\n[dim]Use arrow keys to navigate, Enter to select, Ctrl+Q to exit[/dim]")
            choice = console.input("\n> ")
            
            # Simple input handling
            if choice.lower() in ['q', 'quit', 'exit']:
                break
            elif choice == '1':
                tui.show_provider_selection()
            elif choice == '2':
                tui.show_directory_selection()
            elif choice == '3':
                await tui.start_indexing()
            elif choice == '4':
                tui.show_search()
            elif choice == '5':
                tui.show_status()
            elif choice == '6':
                break
        
        elif tui.state == TUIState.PROVIDER_SELECTION:
            console.print("\n[dim]Select provider number or 'b' to go back[/dim]")
            choice = console.input("\n> ")
            
            if choice.lower() == 'b':
                tui.state = TUIState.MAIN_MENU
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(tui.providers):
                    tui.provider_index = idx
                    tui.select_provider()
        
        elif tui.state == TUIState.PROVIDER_CONFIG:
            console.print("\n[dim]Press Enter to continue or 'b' to go back[/dim]")
            choice = console.input("\n> ")
            
            if choice.lower() == 'b':
                tui.state = TUIState.PROVIDER_SELECTION
            else:
                # For now, accept the defaults
                tui.state = TUIState.MAIN_MENU
        
        elif tui.state in [TUIState.STATUS, TUIState.SEARCH]:
            console.print("\n[dim]Press Enter to go back[/dim]")
            console.input()
            tui.state = TUIState.MAIN_MENU
    
    console.print("\n[bold green]Goodbye! 🐶[/bold green]")

if __name__ == "__main__":
    # Test the TUI
    asyncio.run(launch_rag_tui())