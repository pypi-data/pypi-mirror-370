#!/usr/bin/env python3
"""
Keyboard monitoring utilities for Code Puppy.
Provides cross-platform keyboard event detection.
"""

import asyncio
import sys
import os
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

class KeyboardMonitor:
    """Monitor keyboard input for special keys like ESC."""
    
    def __init__(self):
        self.monitoring = False
        self.escape_pressed = False
        self._monitor_task: Optional[asyncio.Task] = None
        
    async def start_monitoring(self, on_escape: Optional[Callable] = None):
        """Start monitoring for ESC key press."""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.escape_pressed = False
        
        async def monitor():
            """Monitor stdin for ESC key."""
            try:
                # Only monitor if we have a real terminal
                if not sys.stdin.isatty():
                    return
                    
                reader = asyncio.StreamReader()
                protocol = asyncio.StreamReaderProtocol(reader)
                
                try:
                    await asyncio.get_event_loop().connect_read_pipe(
                        lambda: protocol, sys.stdin
                    )
                except Exception:
                    # Can't connect to stdin, skip monitoring
                    return
                
                while self.monitoring:
                    try:
                        # Read with timeout
                        char = await asyncio.wait_for(
                            reader.read(1), 
                            timeout=0.1
                        )
                        
                        if char and ord(char) == 27:  # ESC key
                            self.escape_pressed = True
                            if on_escape:
                                await on_escape()
                            break
                            
                    except asyncio.TimeoutError:
                        continue
                    except Exception:
                        break
                        
            except Exception as e:
                logger.debug(f"Keyboard monitoring error: {e}")
        
        self._monitor_task = asyncio.create_task(monitor())
        
    def stop_monitoring(self):
        """Stop monitoring keyboard input."""
        self.monitoring = False
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            
    def was_escape_pressed(self) -> bool:
        """Check if ESC was pressed."""
        return self.escape_pressed
        
    def reset(self):
        """Reset the escape flag."""
        self.escape_pressed = False


# Global instance for convenience
_keyboard_monitor = KeyboardMonitor()

def get_keyboard_monitor() -> KeyboardMonitor:
    """Get the global keyboard monitor instance."""
    return _keyboard_monitor