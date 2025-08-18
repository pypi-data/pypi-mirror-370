"""Smart tool output management with compaction and caching."""

import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from code_puppy.tools.tool_logger import log_tool
from code_puppy.tools.smart_truncate import smart_truncate

class OutputManager:
    """Manages tool outputs with intelligent compaction and caching."""
    
    # Maximum characters per tool output (50KB as requested)
    MAX_OUTPUT_SIZE = 50000
    
    # Cache for recent outputs
    _output_cache: Dict[str, Dict[str, Any]] = {}
    _cache_expiry = timedelta(minutes=15)
    
    @classmethod
    def compact_output(cls, tool_name: str, output: Any, preserve_structure: bool = True) -> str:
        """
        Compact tool output intelligently.
        
        Args:
            tool_name: Name of the tool
            output: The raw output from the tool
            preserve_structure: Whether to preserve structural information
            
        Returns:
            Compacted output string
        """
        # Convert output to string if needed
        if not isinstance(output, str):
            output = str(output)
        
        original_size = len(output)
        
        # If output is already small enough, return as-is
        if original_size <= cls.MAX_OUTPUT_SIZE:
            return output
        
        # Log that we're compacting
        log_tool(
            tool_name=f"{tool_name}_compaction",
            input_data={"original_size": original_size},
            output_data=None,
            metadata={"action": "compacting_output"}
        )
        
        # Tool-specific compaction strategies
        if tool_name == "grep":
            return cls._compact_grep_output(output)
        elif tool_name == "list_files":
            return cls._compact_file_list(output)
        elif tool_name == "read_file":
            return cls._compact_file_content(output)
        else:
            # Generic compaction using smart truncate
            return cls._generic_compact(output)
    
    @classmethod
    def _compact_grep_output(cls, output: str) -> str:
        """Compact grep output by limiting matches and summarizing."""
        lines = output.split('\n')
        
        # Keep first 100 matches and last 10
        if len(lines) > 110:
            kept_lines = lines[:100]
            kept_lines.append(f"\n... {len(lines) - 110} matches omitted for brevity ...\n")
            kept_lines.extend(lines[-10:])
            output = '\n'.join(kept_lines)
        
        # If still too large, use smart truncate
        if len(output) > cls.MAX_OUTPUT_SIZE:
            output = smart_truncate(output, cls.MAX_OUTPUT_SIZE)
        
        return output
    
    @classmethod
    def _compact_file_list(cls, output: str) -> str:
        """Compact file listing by summarizing directories."""
        lines = output.split('\n')
        
        # Count file types and directories
        file_types = {}
        dir_count = 0
        total_size = 0
        
        for line in lines:
            if '📁' in line:
                dir_count += 1
            elif any(icon in line for icon in ['📄', '🐍', '📜', '⚛️', '⚙️']):
                # Extract file extension if possible
                for ext in ['.py', '.js', '.tsx', '.json', '.xml', '.txt', '.md']:
                    if ext in line:
                        file_types[ext] = file_types.get(ext, 0) + 1
                        break
        
        # If we have a summary section, keep it
        summary_start = -1
        for i, line in enumerate(lines):
            if 'Summary:' in line or '📊' in line:
                summary_start = i
                break
        
        if summary_start > 0:
            # Keep header and summary
            result = lines[:min(10, len(lines))]  # Keep first 10 lines
            result.append("\n... detailed file listing omitted ...\n")
            result.extend(lines[summary_start:])  # Keep summary
            output = '\n'.join(result)
        
        # Final size check
        if len(output) > cls.MAX_OUTPUT_SIZE:
            output = smart_truncate(output, cls.MAX_OUTPUT_SIZE)
        
        return output
    
    @classmethod
    def _compact_file_content(cls, output: str) -> str:
        """Compact file content while preserving important parts."""
        lines = output.split('\n')
        
        if len(lines) > 500:
            # Keep first 200 lines, last 100 lines, and summarize middle
            kept_lines = lines[:200]
            kept_lines.append(f"\n... {len(lines) - 300} lines omitted ...\n")
            kept_lines.extend(lines[-100:])
            output = '\n'.join(kept_lines)
        
        # Final size check
        if len(output) > cls.MAX_OUTPUT_SIZE:
            output = smart_truncate(output, cls.MAX_OUTPUT_SIZE)
        
        return output
    
    @classmethod
    def _generic_compact(cls, output: str) -> str:
        """Generic compaction using smart truncate."""
        return smart_truncate(output, cls.MAX_OUTPUT_SIZE)
    
    @classmethod
    def cache_output(cls, tool_name: str, input_data: Any, output: str) -> str:
        """
        Cache tool output for potential reuse.
        
        Args:
            tool_name: Name of the tool
            input_data: Input parameters used
            output: The output to cache
            
        Returns:
            Cache key for retrieval
        """
        # Create cache key from tool name and input
        cache_data = f"{tool_name}:{json.dumps(input_data, sort_keys=True)}"
        cache_key = hashlib.md5(cache_data.encode()).hexdigest()
        
        cls._output_cache[cache_key] = {
            "tool": tool_name,
            "input": input_data,
            "output": output,
            "timestamp": datetime.now(),
            "size": len(output)
        }
        
        # Clean old cache entries
        cls._clean_cache()
        
        return cache_key
    
    @classmethod
    def get_cached_output(cls, tool_name: str, input_data: Any) -> Optional[str]:
        """
        Retrieve cached output if available and fresh.
        
        Args:
            tool_name: Name of the tool
            input_data: Input parameters used
            
        Returns:
            Cached output or None
        """
        cache_data = f"{tool_name}:{json.dumps(input_data, sort_keys=True)}"
        cache_key = hashlib.md5(cache_data.encode()).hexdigest()
        
        if cache_key in cls._output_cache:
            entry = cls._output_cache[cache_key]
            if datetime.now() - entry["timestamp"] < cls._cache_expiry:
                log_tool(
                    tool_name=f"{tool_name}_cache_hit",
                    input_data=input_data,
                    output_data={"size": entry["size"]},
                    metadata={"cache_key": cache_key}
                )
                return entry["output"]
        
        return None
    
    @classmethod
    def _clean_cache(cls):
        """Remove expired cache entries."""
        now = datetime.now()
        expired_keys = [
            key for key, entry in cls._output_cache.items()
            if now - entry["timestamp"] > cls._cache_expiry
        ]
        for key in expired_keys:
            del cls._output_cache[key]
    
    @classmethod
    def summarize_for_context(cls, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Summarize tool outputs in message history to reduce tokens.
        
        This preserves the thinking chain (assistant messages) while compacting
        tool outputs and system messages.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Compacted message list
        """
        compacted = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "assistant":
                # Preserve assistant thinking chain completely
                compacted.append(msg)
            elif role == "system" and "DIRECTORY LISTING" in content:
                # Compact directory listings aggressively
                compacted_content = cls._compact_file_list(content)
                compacted.append({
                    "role": role,
                    "content": compacted_content
                })
            elif role == "system" and "GREP" in content:
                # Compact grep results
                compacted_content = cls._compact_grep_output(content)
                compacted.append({
                    "role": role,
                    "content": compacted_content
                })
            elif role == "system" and len(content) > cls.MAX_OUTPUT_SIZE:
                # Compact any large system message
                compacted_content = cls._generic_compact(content)
                compacted.append({
                    "role": role,
                    "content": compacted_content
                })
            else:
                # Keep user messages and small system messages as-is
                compacted.append(msg)
        
        return compacted