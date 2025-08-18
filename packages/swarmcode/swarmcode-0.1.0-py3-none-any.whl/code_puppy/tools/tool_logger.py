"""JSON logging system for tool operations."""

import json
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import threading


class ToolLogger:
    """Thread-safe JSON logger for tool operations."""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize the logger.
        
        Args:
            log_file: Path to the log file. Defaults to ~/.code_puppy/tool_logs.json
        """
        if log_file is None:
            log_dir = Path.home() / ".code_puppy"
            log_dir.mkdir(exist_ok=True)
            self.log_file = log_dir / "tool_logs.json"
        else:
            self.log_file = Path(log_file)
        
        self.lock = threading.Lock()
        
        # Initialize log file if it doesn't exist
        if not self.log_file.exists():
            self.log_file.write_text("[]")
    
    def log(self, entry: Dict[str, Any]) -> None:
        """Add a log entry to the JSON log file.
        
        Args:
            entry: Dictionary containing log data
        """
        entry["timestamp"] = datetime.now().isoformat()
        
        with self.lock:
            try:
                # Read existing logs
                logs = json.loads(self.log_file.read_text() or "[]")
                
                # Keep only last 1000 entries to prevent file from growing too large
                if len(logs) > 1000:
                    logs = logs[-900:]
                
                # Add new entry
                logs.append(entry)
                
                # Write back
                self.log_file.write_text(json.dumps(logs, indent=2, default=str))
            except Exception as e:
                # If logging fails, don't crash the tool
                print(f"Logging error: {e}")
    
    def log_tool_execution(
        self,
        tool_name: str,
        input_data: Any,
        output_data: Any,
        error: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a tool execution with standardized format.
        
        Args:
            tool_name: Name of the tool being executed
            input_data: Input provided to the tool
            output_data: Output from the tool
            error: Any exception that occurred
            metadata: Additional metadata about the execution
        """
        entry = {
            "tool": tool_name,
            "input": {
                "data": str(input_data)[:1000] if input_data else None,  # Truncate huge inputs
                "size": len(str(input_data)) if input_data else 0
            },
            "output": {
                "data": str(output_data)[:1000] if output_data else None,  # Truncate huge outputs
                "size": len(str(output_data)) if output_data else 0
            },
            "success": error is None,
            "error": {
                "type": type(error).__name__ if error else None,
                "message": str(error) if error else None,
                "traceback": traceback.format_exc() if error else None
            } if error else None,
            "metadata": metadata or {}
        }
        
        self.log(entry)
    
    def log_smart_truncate(
        self,
        input_size: int,
        output_size: int,
        method: str,
        chunks: int = 0,
        api_calls: int = 0,
        error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log smart truncation operation details.
        
        Args:
            input_size: Size of input content
            output_size: Size of output after truncation
            method: Method used (ai_summary, simple_truncate, etc.)
            chunks: Number of chunks processed
            api_calls: Number of API calls made
            error: Any error that occurred
            details: Additional details
        """
        entry = {
            "tool": "smart_truncate",
            "operation": {
                "input_size": input_size,
                "output_size": output_size,
                "reduction_ratio": f"{(1 - output_size/input_size)*100:.1f}%" if input_size > 0 else "0%",
                "method": method,
                "chunks": chunks,
                "api_calls": api_calls
            },
            "success": error is None,
            "error": {
                "type": type(error).__name__ if error else None,
                "message": str(error) if error else None,
                "traceback": traceback.format_exc() if error else None
            } if error else None,
            "details": details or {}
        }
        
        self.log(entry)
    
    def get_recent_logs(self, count: int = 10) -> list:
        """Get recent log entries.
        
        Args:
            count: Number of recent entries to retrieve
            
        Returns:
            List of recent log entries
        """
        with self.lock:
            try:
                logs = json.loads(self.log_file.read_text() or "[]")
                return logs[-count:]
            except Exception:
                return []
    
    def get_error_logs(self, count: int = 10) -> list:
        """Get recent error log entries.
        
        Args:
            count: Number of recent error entries to retrieve
            
        Returns:
            List of recent error log entries
        """
        with self.lock:
            try:
                logs = json.loads(self.log_file.read_text() or "[]")
                errors = [log for log in logs if not log.get("success", True)]
                return errors[-count:]
            except Exception:
                return []
    
    def clear_logs(self) -> None:
        """Clear all logs."""
        with self.lock:
            self.log_file.write_text("[]")


# Global logger instance
_logger = None


def get_logger() -> ToolLogger:
    """Get or create the global tool logger instance."""
    global _logger
    if _logger is None:
        _logger = ToolLogger()
    return _logger


def log_tool(*args, **kwargs):
    """Convenience function to log tool execution."""
    get_logger().log_tool_execution(*args, **kwargs)


def log_smart_truncate(*args, **kwargs):
    """Convenience function to log smart truncate operations."""
    get_logger().log_smart_truncate(*args, **kwargs)