#!/usr/bin/env python3
"""
Asynchronous RAG indexer that runs in the background.
"""

import os
import asyncio
import logging
import threading
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

logger = logging.getLogger(__name__)

@dataclass
class IndexingStatus:
    """Track the status of indexing operation."""
    is_running: bool = False
    total_files: int = 0
    indexed_files: int = 0
    failed_files: int = 0
    total_chunks: int = 0
    current_file: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    progress_percent: float = 0.0
    eta_seconds: Optional[float] = None
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time:
            end = self.end_time or datetime.now()
            return (end - self.start_time).total_seconds()
        return 0.0
    
    @property
    def files_per_second(self) -> float:
        """Calculate indexing speed."""
        if self.indexed_files > 0 and self.elapsed_time > 0:
            return self.indexed_files / self.elapsed_time
        return 0.0
    
    def estimate_remaining_time(self) -> Optional[float]:
        """Estimate remaining time in seconds."""
        if self.files_per_second > 0:
            remaining_files = self.total_files - self.indexed_files
            return remaining_files / self.files_per_second
        return None

class AsyncRAGIndexer:
    """Asynchronous RAG indexer that runs in the background."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for indexer."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the async indexer."""
        if not hasattr(self, '_initialized'):
            self.status = IndexingStatus()
            self._indexing_task: Optional[asyncio.Task] = None
            self._stop_event = asyncio.Event()
            self._initialized = True
            self.console = Console()
    
    async def index_workspace_async(
        self, 
        workspace_path: str = ".",
        max_files: Optional[int] = None,
        console: Optional[Console] = None
    ):
        """Index workspace asynchronously."""
        if self.status.is_running:
            return {"error": "Indexing already in progress"}
        
        # Reset status
        self.status = IndexingStatus(
            is_running=True,
            start_time=datetime.now()
        )
        
        try:
            # Import here to avoid circular dependency
            from code_puppy.embeddings.lightweight_client import create_client
            
            # Create client
            project_name = os.getenv("RAG_PROJECT", "code_puppy_embeddings")
            client = create_client(project_name)
            
            # Check health
            health = client.health_check()
            if not (health['embedding_service'] and health['qdrant']):
                self.status.error = "RAG services not healthy"
                self.status.is_running = False
                return {"error": self.status.error}
            
            # Gather files
            path = Path(workspace_path)
            python_files = []
            
            # Collect files with progress
            for file_path in path.glob("**/*.py"):
                if self._stop_event.is_set():
                    break
                python_files.append(file_path)
                # Update status periodically
                if len(python_files) % 100 == 0:
                    self.status.current_file = f"Scanning... ({len(python_files)} files found)"
                    await asyncio.sleep(0)  # Yield to other tasks
            
            # Apply limit if specified
            if max_files:
                python_files = python_files[:max_files]
            
            self.status.total_files = len(python_files)
            
            if self.status.total_files == 0:
                self.status.error = "No Python files found"
                self.status.is_running = False
                return {"error": self.status.error}
            
            # Index files
            for i, file_path in enumerate(python_files, 1):
                if self._stop_event.is_set():
                    self.status.error = "Indexing cancelled by user"
                    break
                
                try:
                    # Update status
                    rel_path = file_path.relative_to(path)
                    self.status.current_file = str(rel_path)
                    self.status.progress_percent = (i / self.status.total_files) * 100
                    self.status.eta_seconds = self.status.estimate_remaining_time()
                    
                    # Read file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Limit content size
                    max_content_size = 10000
                    if len(content) > max_content_size:
                        content = content[:max_content_size]
                    
                    # Index with client
                    chunks = client.index_code(str(rel_path), content)
                    self.status.indexed_files += 1
                    self.status.total_chunks += chunks
                    
                    # Yield periodically to prevent blocking
                    if i % 10 == 0:
                        await asyncio.sleep(0.01)
                    
                except Exception as e:
                    self.status.failed_files += 1
                    logger.error(f"Failed to index {file_path}: {e}")
            
            self.status.end_time = datetime.now()
            self.status.is_running = False
            
            return {
                "success": True,
                "indexed": self.status.indexed_files,
                "failed": self.status.failed_files,
                "chunks": self.status.total_chunks,
                "time": self.status.elapsed_time
            }
            
        except Exception as e:
            self.status.error = str(e)
            self.status.is_running = False
            logger.error(f"Indexing failed: {e}")
            return {"error": str(e)}
    
    def start_indexing(
        self,
        workspace_path: str = ".",
        max_files: Optional[int] = None,
        console: Optional[Console] = None
    ):
        """Start indexing in the background."""
        if self.status.is_running:
            return False
        
        # Reset stop event
        self._stop_event.clear()
        
        # Create and start task
        loop = asyncio.new_event_loop()
        threading.Thread(
            target=self._run_indexing_thread,
            args=(loop, workspace_path, max_files, console),
            daemon=True
        ).start()
        
        return True
    
    def _run_indexing_thread(self, loop, workspace_path, max_files, console):
        """Run indexing in a separate thread."""
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            self.index_workspace_async(workspace_path, max_files, console)
        )
    
    def stop_indexing(self):
        """Stop the indexing process."""
        if self.status.is_running:
            self._stop_event.set()
            return True
        return False
    
    def get_status_display(self) -> Panel:
        """Get a rich panel showing current indexing status."""
        if not self.status.is_running and not self.status.indexed_files:
            return Panel(
                "[dim]No indexing in progress[/dim]",
                title="RAG Indexing Status",
                border_style="dim"
            )
        
        # Create status table
        table = Table.grid(padding=0)
        table.add_column(style="bold", width=20)
        table.add_column()
        
        # Status indicator
        if self.status.is_running:
            status_text = Text("🔄 INDEXING", style="bold yellow blink")
        elif self.status.error:
            status_text = Text(f"❌ ERROR: {self.status.error}", style="bold red")
        else:
            status_text = Text("✅ COMPLETED", style="bold green")
        
        table.add_row("Status:", status_text)
        
        # Progress bar
        if self.status.total_files > 0:
            progress_bar = self._create_progress_bar()
            table.add_row("Progress:", progress_bar)
            
            # Stats
            table.add_row(
                "Files:",
                f"[cyan]{self.status.indexed_files}/{self.status.total_files}[/cyan] "
                f"([green]{self.status.progress_percent:.1f}%[/green])"
            )
            
            if self.status.failed_files > 0:
                table.add_row("Failed:", f"[red]{self.status.failed_files}[/red]")
            
            table.add_row("Chunks:", f"[yellow]{self.status.total_chunks}[/yellow]")
            
            # Current file
            if self.status.is_running and self.status.current_file:
                current = self.status.current_file
                if len(current) > 50:
                    current = "..." + current[-47:]
                table.add_row("Current:", f"[dim]{current}[/dim]")
            
            # Speed and ETA
            if self.status.files_per_second > 0:
                table.add_row(
                    "Speed:",
                    f"[cyan]{self.status.files_per_second:.1f}[/cyan] files/sec"
                )
                
                if self.status.eta_seconds and self.status.is_running:
                    eta_min = int(self.status.eta_seconds / 60)
                    eta_sec = int(self.status.eta_seconds % 60)
                    table.add_row("ETA:", f"[yellow]{eta_min:02d}:{eta_sec:02d}[/yellow]")
            
            # Elapsed time
            elapsed = int(self.status.elapsed_time)
            elapsed_min = elapsed // 60
            elapsed_sec = elapsed % 60
            table.add_row("Elapsed:", f"[dim]{elapsed_min:02d}:{elapsed_sec:02d}[/dim]")
        
        # Create panel
        title = "🔍 RAG Indexing Status"
        if self.status.is_running:
            title += " (Press ~rag stop to cancel)"
        
        return Panel(
            table,
            title=title,
            border_style="cyan" if self.status.is_running else "green",
            padding=(1, 2)
        )
    
    def _create_progress_bar(self) -> Text:
        """Create a text-based progress bar."""
        width = 30
        filled = int(width * self.status.progress_percent / 100)
        empty = width - filled
        
        bar = Text()
        bar.append("█" * filled, style="green")
        bar.append("░" * empty, style="dim")
        
        return bar

# Global indexer instance
_async_indexer: Optional[AsyncRAGIndexer] = None

def get_async_indexer() -> AsyncRAGIndexer:
    """Get or create the global async indexer."""
    global _async_indexer
    if _async_indexer is None:
        _async_indexer = AsyncRAGIndexer()
    return _async_indexer