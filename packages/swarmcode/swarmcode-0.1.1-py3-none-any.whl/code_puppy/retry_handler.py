"""Smart retry mechanism for API rate limits and errors."""

import asyncio
import time
from typing import Any, Callable, Optional, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
import random

console = Console()

class RetryHandler:
    """Handles retries with exponential backoff and visual feedback."""
    
    # Retry configuration
    MAX_RETRIES = 5
    BASE_DELAY = 10  # Base delay in seconds
    MAX_DELAY = 120  # Maximum delay in seconds
    JITTER_RANGE = 0.3  # Add random jitter (±30%)
    
    # Error patterns that trigger retry
    RETRY_ERRORS = [
        "request_limit",
        "rate_limit",
        "429",  # Too Many Requests
        "503",  # Service Unavailable
        "timeout",
        "connection",
        "Wrong API Key",  # Temporary API key issues
    ]
    
    @classmethod
    def should_retry(cls, error: Exception) -> bool:
        """Determine if an error should trigger a retry."""
        error_str = str(error).lower()
        return any(pattern.lower() in error_str for pattern in cls.RETRY_ERRORS)
    
    @classmethod
    def calculate_delay(cls, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        # Exponential backoff: 10, 20, 40, 80, 120 (capped)
        delay = min(cls.BASE_DELAY * (2 ** attempt), cls.MAX_DELAY)
        
        # Add jitter to prevent thundering herd
        jitter = delay * cls.JITTER_RANGE * (2 * random.random() - 1)
        return max(1, delay + jitter)
    
    @classmethod
    async def show_countdown(cls, delay: float, attempt: int, max_attempts: int, error_msg: str):
        """Show animated countdown with progress."""
        remaining = int(delay)
        
        # Emoji animation for visual feedback
        spinner_frames = ["⏳", "⌛", "⏳", "⌛"]
        loading_frames = ["◐", "◓", "◑", "◒"]
        
        with Live(console=console, refresh_per_second=2) as live:
            while remaining > 0:
                frame_idx = (int(delay) - remaining) % len(spinner_frames)
                spinner = spinner_frames[frame_idx]
                loader = loading_frames[frame_idx % len(loading_frames)]
                
                # Create status panel
                status_text = Text()
                status_text.append(f"{spinner} ", style="yellow")
                status_text.append(f"Rate limit hit! ", style="bold red")
                status_text.append(f"Retrying in ", style="white")
                status_text.append(f"{remaining}s", style="bold cyan")
                status_text.append(f" {loader}\n", style="yellow")
                
                # Progress bar
                progress = "█" * (int(delay) - remaining) + "░" * remaining
                status_text.append(f"[{progress}]\n", style="dim")
                
                # Attempt info
                status_text.append(f"Attempt ", style="dim")
                status_text.append(f"{attempt + 1}/{max_attempts}", style="bold yellow")
                status_text.append(f" | Error: ", style="dim")
                status_text.append(f"{error_msg[:50]}...", style="red")
                
                panel = Panel(
                    status_text,
                    title="🔄 Auto-Retry",
                    border_style="yellow",
                    padding=(1, 2)
                )
                
                live.update(panel)
                await asyncio.sleep(1)
                remaining -= 1
        
        # Show resuming message
        console.print(f"[bold green]✓[/bold green] Resuming request...")
    
    @classmethod
    async def retry_with_backoff(cls, func: Callable, *args, **kwargs) -> Any:
        """Execute function with smart retry logic."""
        last_error = None
        
        for attempt in range(cls.MAX_RETRIES):
            try:
                # Try to execute the function
                result = await func(*args, **kwargs)
                
                # If successful and we had retried, show success
                if attempt > 0:
                    console.print(f"[bold green]✓ Request successful after {attempt} retries![/bold green]")
                
                return result
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                # Check if we should retry
                if not cls.should_retry(e):
                    # Don't retry for non-retryable errors
                    raise
                
                # Check if we've exhausted retries
                if attempt >= cls.MAX_RETRIES - 1:
                    console.print(f"[bold red]✗ Max retries ({cls.MAX_RETRIES}) exceeded[/bold red]")
                    raise
                
                # Calculate delay with backoff
                delay = cls.calculate_delay(attempt)
                
                # Log the retry attempt
                console.print(f"\n[yellow]⚠ {error_msg}[/yellow]")
                
                # Show countdown animation
                await cls.show_countdown(delay, attempt, cls.MAX_RETRIES, error_msg)
        
        # If we get here, we've exhausted retries
        raise last_error

class RateLimitTracker:
    """Track and predict rate limits to prevent hitting them."""
    
    def __init__(self, window_size: int = 60, max_requests: int = 50):
        self.window_size = window_size  # Time window in seconds
        self.max_requests = max_requests
        self.requests: list[float] = []
    
    def add_request(self):
        """Record a new request."""
        now = time.time()
        self.requests.append(now)
        # Clean old requests outside window
        cutoff = now - self.window_size
        self.requests = [t for t in self.requests if t > cutoff]
    
    def can_make_request(self) -> tuple[bool, float]:
        """Check if we can make a request without hitting rate limit."""
        now = time.time()
        cutoff = now - self.window_size
        recent_requests = [t for t in self.requests if t > cutoff]
        
        if len(recent_requests) >= self.max_requests:
            # Calculate when the oldest request will expire
            oldest = min(recent_requests)
            wait_time = (oldest + self.window_size) - now
            return False, wait_time
        
        return True, 0
    
    def get_remaining_requests(self) -> int:
        """Get number of requests remaining in current window."""
        now = time.time()
        cutoff = now - self.window_size
        recent_requests = [t for t in self.requests if t > cutoff]
        return max(0, self.max_requests - len(recent_requests))
    
    async def wait_if_needed(self):
        """Wait if we're approaching rate limit."""
        can_proceed, wait_time = self.can_make_request()
        
        if not can_proceed and wait_time > 0:
            console.print(f"[yellow]⏸ Preemptive rate limit pause: {wait_time:.1f}s[/yellow]")
            
            # Show a simple countdown
            for i in range(int(wait_time), 0, -1):
                console.print(f"[dim]Waiting... {i}s[/dim]", end="\r")
                await asyncio.sleep(1)
            
            console.print("[green]✓ Continuing...[/green]" + " " * 20)
    
    def show_status(self):
        """Display current rate limit status."""
        remaining = self.get_remaining_requests()
        
        # Create visual indicator
        bar_length = 20
        filled = int((remaining / self.max_requests) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Color based on remaining
        if remaining < 10:
            color = "red"
            emoji = "🔴"
        elif remaining < 25:
            color = "yellow"
            emoji = "🟡"
        else:
            color = "green"
            emoji = "🟢"
        
        console.print(
            f"{emoji} Rate Limit: [{color}]{remaining}/{self.max_requests}[/{color}] "
            f"[{bar}]",
            style="dim"
        )