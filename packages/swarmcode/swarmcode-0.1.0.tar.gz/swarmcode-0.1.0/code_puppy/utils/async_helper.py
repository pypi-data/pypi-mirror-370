#!/usr/bin/env python3
"""
Helper utilities for running async code in different contexts.
"""

import asyncio
import threading
from typing import Any, Coroutine, Optional
import logging

logger = logging.getLogger(__name__)

def run_async_in_sync(coro: Coroutine) -> Any:
    """
    Run an async coroutine from synchronous code, handling event loop conflicts.
    
    Args:
        coro: The coroutine to run
        
    Returns:
        The result of the coroutine
    """
    try:
        # Check if there's already a running event loop
        loop = asyncio.get_running_loop()
        
        # We're in an async context
        # Create a new thread to run the coroutine to avoid event loop conflicts
        result = None
        exception = None
        
        def run_in_thread():
            nonlocal result, exception
            new_loop = None
            try:
                # Create a new event loop for this thread
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                result = new_loop.run_until_complete(coro)
            except Exception as e:
                exception = e
                logger.error(f"Error in thread: {e}")
            finally:
                # Ensure the loop is closed properly
                if new_loop:
                    try:
                        # Cancel any remaining tasks
                        pending = asyncio.all_tasks(new_loop)
                        for task in pending:
                            task.cancel()
                        # Run the loop one more time to handle cancellations
                        if pending:
                            new_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    except Exception:
                        pass
                    finally:
                        new_loop.close()
        
        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()
        
        if exception:
            raise exception
        return result
        
    except RuntimeError:
        # No running loop, safe to create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(coro)
            return result
        finally:
            loop.close()