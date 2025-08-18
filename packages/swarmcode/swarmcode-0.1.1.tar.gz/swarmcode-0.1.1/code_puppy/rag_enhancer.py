#!/usr/bin/env python3
"""
RAG (Retrieval Augmented Generation) enhancer for Code Puppy.
Adds embedding-based context retrieval to enhance responses.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.syntax import Syntax

logger = logging.getLogger(__name__)

class RAGEnhancer:
    """Enhances Code Puppy responses with RAG context."""
    
    def __init__(self, console: Console = None):
        """Initialize RAG enhancer."""
        self.console = console or Console()
        self.enabled = os.getenv("ENABLE_RAG", "false").lower() == "true"
        self.client = None
        self._initialized = False
        
        if self.enabled:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the embedding client."""
        try:
            from code_puppy.embeddings.lightweight_client import create_client
            
            project_name = os.getenv("RAG_PROJECT", "code_puppy_embeddings")
            self.client = create_client(project_name)
            
            # Check if services are healthy
            health = self.client.health_check()
            if health['embedding_service'] and health['qdrant']:
                self._initialized = True
                logger.info(f"RAG initialized with project: {project_name}")
            else:
                logger.warning("RAG services not healthy")
                self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize RAG: {e}")
            self.enabled = False
    
    def search_context(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant context."""
        if not self.enabled or not self._initialized:
            return []
        
        try:
            results = self.client.search_code(query, limit=limit, score_threshold=0.4)
            
            context_items = []
            for result in results:
                context_items.append({
                    'file': result.payload.get('file_path', 'unknown'),
                    'content': result.payload.get('content', ''),
                    'score': result.score,
                    'lines': (
                        result.payload.get('start_line', 0),
                        result.payload.get('end_line', 0)
                    )
                })
            
            return context_items
        except Exception as e:
            logger.error(f"Error searching context: {e}")
            return []
    
    def display_rag_context(self, query: str):
        """Display RAG context in the terminal UI."""
        if not self.enabled:
            return
        
        # Search for context
        contexts = self.search_context(query, limit=3)
        
        if not contexts:
            return
        
        # Create styled output
        self.console.print()
        self.console.print("🔍 [bold cyan]RAG Context Found[/bold cyan]", justify="left")
        self.console.print("─" * 60)
        
        for i, ctx in enumerate(contexts, 1):
            # Create a panel for each context item
            file_path = ctx['file']
            score = ctx['score']
            lines = ctx['lines']
            content = ctx['content'][:200]  # Show first 200 chars
            
            # Style the file path
            file_text = Text(f"📄 {file_path}", style="bold green")
            score_text = Text(f"Relevance: {score:.2%}", style="italic yellow")
            
            # Create content preview
            if content:
                # Try to detect language for syntax highlighting
                lang = "python" if file_path.endswith('.py') else "text"
                content_syntax = Syntax(
                    content, 
                    lang, 
                    theme="monokai",
                    line_numbers=False,
                    word_wrap=True
                )
            else:
                content_syntax = Text("(empty)", style="dim")
            
            # Create panel
            panel_content = Text()
            panel_content.append(file_text)
            panel_content.append(" · ")
            panel_content.append(score_text)
            if lines[0] > 0:
                panel_content.append(f" · Lines {lines[0]}-{lines[1]}")
            panel_content.append("\n\n")
            
            panel = Panel(
                content_syntax,
                title=f"[{i}] {file_path}",
                title_align="left",
                border_style="cyan",
                padding=(0, 1)
            )
            
            self.console.print(panel)
        
        self.console.print("─" * 60)
        self.console.print()
    
    def get_context_string(self, query: str, max_length: int = 2000) -> str:
        """Get context as a formatted string for injection into prompts."""
        if not self.enabled or not self._initialized:
            return ""
        
        contexts = self.search_context(query, limit=3)
        
        if not contexts:
            return ""
        
        context_parts = []
        context_parts.append("=== Relevant Code Context ===")
        
        for ctx in contexts:
            context_parts.append(f"\nFile: {ctx['file']} (relevance: {ctx['score']:.2%})")
            content = ctx['content'][:500]
            context_parts.append(content)
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        if len(context) > max_length:
            context = context[:max_length] + "\n..."
        
        return context
    
    def enhance_prompt(self, user_input: str) -> str:
        """Enhance the user prompt with RAG context."""
        if not self.enabled:
            return user_input
        
        context = self.get_context_string(user_input)
        
        if context:
            enhanced = f"{user_input}\n\n[Context from codebase:\n{context}\n]"
            return enhanced
        
        return user_input
    
    def index_workspace(self, workspace_path: str = ".", max_files: int = None):
        """Index the current workspace for RAG with progress indicator."""
        if not self.enabled or not self._initialized:
            self.console.print("[yellow]RAG indexing skipped (not enabled)[/yellow]")
            return
        
        from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
        from rich.live import Live
        from rich.table import Table
        from rich.panel import Panel
        import time
        
        path = Path(workspace_path)
        
        # Gather all Python files
        self.console.print("\n🔍 [bold cyan]Scanning workspace for Python files...[/bold cyan]")
        python_files = list(path.glob("**/*.py"))
        
        # Apply limit if specified (for testing)
        if max_files:
            python_files = python_files[:max_files]
        
        total_files = len(python_files)
        
        if total_files == 0:
            self.console.print("[yellow]No Python files found to index.[/yellow]")
            return
        
        self.console.print(f"📊 Found [bold green]{total_files}[/bold green] Python files to index\n")
        
        indexed_count = 0
        failed_count = 0
        total_chunks = 0
        
        # Create progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[cyan]{task.completed}/{task.total}[/cyan] files"),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            
            # Create main indexing task
            index_task = progress.add_task(
                "[bold cyan]Indexing files...[/bold cyan]",
                total=total_files
            )
            
            # Create a table for status
            for i, file_path in enumerate(python_files, 1):
                try:
                    # Update progress description with current file
                    rel_path = file_path.relative_to(path)
                    progress.update(
                        index_task,
                        description=f"[bold cyan]Indexing:[/bold cyan] {str(rel_path)[:50]}..."
                    )
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Index the full file content (or limit for large files)
                    max_content_size = 10000  # Limit to 10KB per file for performance
                    if len(content) > max_content_size:
                        content = content[:max_content_size]
                    
                    chunks = self.client.index_code(str(rel_path), content)
                    indexed_count += 1
                    total_chunks += chunks
                    
                    # Update progress
                    progress.update(index_task, advance=1)
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to index {file_path}: {e}")
                    progress.update(index_task, advance=1)
            
            # Final status
            progress.update(
                index_task,
                description="[bold green]✅ Indexing complete![/bold green]"
            )
        
        # Display summary
        summary = Table.grid(padding=1)
        summary.add_column(style="bold")
        summary.add_column()
        
        summary.add_row("📁 Files processed:", f"[cyan]{total_files}[/cyan]")
        summary.add_row("✅ Successfully indexed:", f"[green]{indexed_count}[/green]")
        if failed_count > 0:
            summary.add_row("❌ Failed:", f"[red]{failed_count}[/red]")
        summary.add_row("📦 Total chunks created:", f"[yellow]{total_chunks}[/yellow]")
        
        panel = Panel(
            summary,
            title="[bold cyan]RAG Indexing Complete[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()

# Global instance
_rag_enhancer = None

def get_rag_enhancer(console: Console = None) -> RAGEnhancer:
    """Get or create the global RAG enhancer."""
    global _rag_enhancer
    if _rag_enhancer is None:
        _rag_enhancer = RAGEnhancer(console)
    return _rag_enhancer

def display_rag_context(query: str, console: Console = None):
    """Display RAG context for a query."""
    enhancer = get_rag_enhancer(console)
    enhancer.display_rag_context(query)

def enhance_with_rag(user_input: str, console: Console = None) -> str:
    """Enhance user input with RAG context."""
    enhancer = get_rag_enhancer(console)
    return enhancer.enhance_prompt(user_input)