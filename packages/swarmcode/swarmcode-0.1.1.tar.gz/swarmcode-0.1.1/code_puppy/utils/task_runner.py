#!/usr/bin/env python3
"""
Enhanced task runner with better cancellation support.
"""

import asyncio
import signal
from typing import Optional, Any, Callable
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
import logging

logger = logging.getLogger(__name__)

class TaskRunner:
    """Run async tasks with cancellation support and visual feedback."""
    
    def __init__(self, console: Console):
        self.console = console
        self.cancelled = False
        self._original_handler = None
        
    async def run_with_cancellation(
        self, 
        task_func: Callable, 
        task_name: str = "task",
        show_spinner: bool = True
    ) -> Optional[Any]:
        """
        Run an async task with cancellation support.
        
        Args:
            task_func: Async function to run
            task_name: Name of the task for display
            show_spinner: Whether to show a spinner
            
        Returns:
            Result of the task or None if cancelled
        """
        self.cancelled = False
        task = asyncio.create_task(task_func())
        
        # Set up signal handler for Ctrl+C
        def signal_handler(sig, frame):
            if not task.done():
                self.cancelled = True
                task.cancel()
                
        self._original_handler = signal.signal(signal.SIGINT, signal_handler)
        
        try:
            if show_spinner:
                # Show spinner while task is running
                spinner = Spinner("dots", text=f"Processing {task_name}... (Press Ctrl+C to cancel)")
                with Live(spinner, console=self.console, refresh_per_second=10):
                    result = await task
            else:
                # Just run the task without spinner
                result = await task
                
            return result
            
        except asyncio.CancelledError:
            self.console.print(f"[yellow]✗ {task_name.capitalize()} cancelled[/yellow]")
            return None
            
        finally:
            # Restore original signal handler
            if self._original_handler:
                signal.signal(signal.SIGINT, self._original_handler)
                
    def was_cancelled(self) -> bool:
        """Check if the last task was cancelled."""
        return self.cancelled