"""Paginated code map with intelligent chunking."""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from rich.text import Text
from rich.tree import Tree as RichTree
from rich.console import Console
from code_puppy.tools.common import should_ignore_path
from code_puppy.config import get_tool_output_limit
from code_puppy.tools.tool_logger import log_tool
import json


class PaginatedCodeMap:
    """Manages paginated code map generation and storage."""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}  # dir_path -> map_data
        self.page_size = 10000  # Characters per page
    
    def generate_map(self, directory: str, page: Optional[int] = None, 
                     search: Optional[str] = None) -> Tuple[str, Dict]:
        """
        Generate a paginated code map.
        
        Args:
            directory: Directory to map
            page: Page number to display (1-based), None for summary
            search: Optional search term to filter files
            
        Returns:
            Tuple of (output_text, metadata)
        """
        abs_dir = Path(directory).resolve()
        cache_key = str(abs_dir)
        
        # Check cache
        if cache_key not in self.cache or search:
            self._build_cache(abs_dir, search)
        
        map_data = self.cache[cache_key]
        
        # Return requested view
        if page is None:
            return self._generate_summary(map_data)
        else:
            return self._get_page(map_data, page)
    
    def _build_cache(self, directory: Path, search: Optional[str] = None):
        """Build the cached representation of the directory."""
        
        # Collect all files and directories
        structure = {
            "path": str(directory),
            "name": directory.name,
            "files": [],
            "dirs": [],
            "total_files": 0,
            "total_dirs": 0,
            "total_size": 0,
            "pages": [],
            "search_term": search
        }
        
        # Walk directory
        for root, dirs, files in os.walk(directory):
            # Filter hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            rel_path = Path(root).relative_to(directory)
            
            # Skip if we're searching and path doesn't match
            if search and search.lower() not in str(rel_path).lower():
                # Check if any files match
                matching_files = [f for f in files if search.lower() in f.lower()]
                if not matching_files:
                    continue
                files = matching_files
            
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                if not should_ignore_path(str(dir_path)):
                    structure["dirs"].append({
                        "name": dir_name,
                        "path": str(rel_path / dir_name),
                        "parent": str(rel_path)
                    })
                    structure["total_dirs"] += 1
            
            for file_name in files:
                file_path = Path(root) / file_name
                if not should_ignore_path(str(file_path)):
                    try:
                        size = file_path.stat().st_size
                        structure["files"].append({
                            "name": file_name,
                            "path": str(rel_path / file_name),
                            "parent": str(rel_path),
                            "size": size,
                            "extension": file_path.suffix
                        })
                        structure["total_files"] += 1
                        structure["total_size"] += size
                    except:
                        pass
        
        # Sort for consistent ordering
        structure["files"].sort(key=lambda x: x["path"])
        structure["dirs"].sort(key=lambda x: x["path"])
        
        # Create pages
        self._paginate_structure(structure)
        
        # Cache result
        self.cache[str(directory)] = structure
        
        # Log the operation
        log_tool(
            tool_name="paginated_codemap",
            input_data={"directory": str(directory), "search": search},
            output_data={"total_files": structure["total_files"], 
                        "total_dirs": structure["total_dirs"],
                        "num_pages": len(structure["pages"])},
            metadata={"cache_key": str(directory)}
        )
    
    def _paginate_structure(self, structure: Dict):
        """Split structure into pages."""
        pages = []
        current_page = []
        current_size = 0
        
        # Group by directory
        dir_groups = {}
        for file_info in structure["files"]:
            parent = file_info["parent"]
            if parent not in dir_groups:
                dir_groups[parent] = []
            dir_groups[parent].append(file_info)
        
        # Build pages
        for dir_path in sorted(dir_groups.keys()):
            dir_files = dir_groups[dir_path]
            dir_text = self._format_directory_section(dir_path, dir_files)
            dir_size = len(dir_text)
            
            if current_size + dir_size > self.page_size and current_page:
                # Save current page and start new one
                pages.append({
                    "content": current_page,
                    "size": current_size,
                    "dirs": len(set(f["parent"] for f in current_page))
                })
                current_page = []
                current_size = 0
            
            # Add to current page
            current_page.extend(dir_files)
            current_size += dir_size
        
        # Add final page
        if current_page:
            pages.append({
                "content": current_page,
                "size": current_size,
                "dirs": len(set(f["parent"] for f in current_page))
            })
        
        structure["pages"] = pages
    
    def _format_directory_section(self, dir_path: str, files: List[Dict]) -> str:
        """Format a directory section for display."""
        lines = []
        
        # Directory header
        if dir_path == ".":
            lines.append("📁 Root Directory")
        else:
            lines.append(f"📁 {dir_path}/")
        
        # Files in this directory
        for file_info in files:
            size_str = self._format_size(file_info["size"])
            ext = file_info["extension"]
            icon = self._get_file_icon(ext)
            lines.append(f"  {icon} {file_info['name']} ({size_str})")
        
        lines.append("")  # Empty line between directories
        return "\n".join(lines)
    
    def _generate_summary(self, map_data: Dict) -> Tuple[str, Dict]:
        """Generate a summary view of the code map."""
        lines = []
        
        lines.append(f"📊 Code Map Summary: {map_data['name']}")
        lines.append("=" * 50)
        
        if map_data.get("search_term"):
            lines.append(f"🔍 Search: '{map_data['search_term']}'")
            lines.append("")
        
        lines.append(f"📁 Total Directories: {map_data['total_dirs']:,}")
        lines.append(f"📄 Total Files: {map_data['total_files']:,}")
        lines.append(f"💾 Total Size: {self._format_size(map_data['total_size'])}")
        lines.append(f"📖 Total Pages: {len(map_data['pages'])}")
        lines.append("")
        
        # File type distribution
        ext_counts = {}
        for file_info in map_data["files"]:
            ext = file_info["extension"] or "no extension"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
        
        if ext_counts:
            lines.append("📈 File Types (top 10):")
            sorted_exts = sorted(ext_counts.items(), key=lambda x: -x[1])[:10]
            for ext, count in sorted_exts:
                icon = self._get_file_icon(ext)
                lines.append(f"  {icon} {ext}: {count:,} files")
            lines.append("")
        
        # Top-level directories
        top_dirs = set()
        for dir_info in map_data["dirs"][:20]:  # Show up to 20 top dirs
            parts = dir_info["path"].split("/")
            if len(parts) == 1:
                top_dirs.add(parts[0])
        
        if top_dirs:
            lines.append("📂 Top-Level Directories:")
            for dir_name in sorted(top_dirs)[:10]:
                lines.append(f"  📁 {dir_name}/")
            lines.append("")
        
        # Page navigation help
        lines.append("📖 Navigation:")
        lines.append(f"  Use ~codemap {map_data['path']} <page_num> to view specific pages")
        lines.append(f"  Pages available: 1-{len(map_data['pages'])}")
        lines.append("  Use ~codemap <dir> search <term> to search")
        
        output = "\n".join(lines)
        metadata = {
            "type": "summary",
            "total_pages": len(map_data["pages"]),
            "search_term": map_data.get("search_term")
        }
        
        return output, metadata
    
    def _get_page(self, map_data: Dict, page_num: int) -> Tuple[str, Dict]:
        """Get a specific page of the code map."""
        num_pages = len(map_data["pages"])
        
        if page_num < 1 or page_num > num_pages:
            return f"❌ Invalid page number. Available pages: 1-{num_pages}", {"error": "invalid_page"}
        
        page_data = map_data["pages"][page_num - 1]
        lines = []
        
        # Page header
        lines.append(f"📖 Code Map: {map_data['name']} (Page {page_num}/{num_pages})")
        lines.append("=" * 50)
        
        if map_data.get("search_term"):
            lines.append(f"🔍 Search: '{map_data['search_term']}'")
            lines.append("")
        
        # Group files by directory
        dir_groups = {}
        for file_info in page_data["content"]:
            parent = file_info["parent"]
            if parent not in dir_groups:
                dir_groups[parent] = []
            dir_groups[parent].append(file_info)
        
        # Display each directory section
        for dir_path in sorted(dir_groups.keys()):
            lines.append(self._format_directory_section(dir_path, dir_groups[dir_path]))
        
        # Page footer
        lines.append("-" * 50)
        lines.append(f"Page {page_num} of {num_pages} | Files: {len(page_data['content'])} | Directories: {page_data['dirs']}")
        
        # Navigation hints
        if page_num > 1:
            lines.append(f"Previous: ~codemap {map_data['path']} {page_num - 1}")
        if page_num < num_pages:
            lines.append(f"Next: ~codemap {map_data['path']} {page_num + 1}")
        
        output = "\n".join(lines)
        metadata = {
            "type": "page",
            "page": page_num,
            "total_pages": num_pages,
            "files_shown": len(page_data["content"]),
            "search_term": map_data.get("search_term")
        }
        
        return output, metadata
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _get_file_icon(self, extension: str) -> str:
        """Get an icon for a file extension."""
        icon_map = {
            ".py": "🐍",
            ".js": "📜",
            ".jsx": "⚛️",
            ".ts": "📘",
            ".tsx": "⚛️",
            ".html": "🌐",
            ".css": "🎨",
            ".json": "⚙️",
            ".md": "📝",
            ".txt": "📄",
            ".yml": "⚙️",
            ".yaml": "⚙️",
            ".sh": "📜",
            ".sql": "📊",
            ".png": "🖼️",
            ".jpg": "🖼️",
            ".jpeg": "🖼️",
            ".gif": "🖼️",
            ".svg": "🖼️",
            ".pdf": "📄",
            ".zip": "📦",
            ".tar": "📦",
            ".gz": "📦",
            ".mp4": "🎬",
            ".mp3": "🎵",
            ".wav": "🎵",
            ".csv": "📊",
            ".xlsx": "📊",
            ".doc": "📄",
            ".docx": "📄",
            ".pptx": "📄",
        }
        return icon_map.get(extension, "📄")
    
    def clear_cache(self, directory: Optional[str] = None):
        """Clear cached code maps."""
        if directory:
            cache_key = str(Path(directory).resolve())
            if cache_key in self.cache:
                del self.cache[cache_key]
        else:
            self.cache.clear()


# Global instance
_paginated_map = PaginatedCodeMap()


def handle_codemap_command(command: str, directory: str = ".") -> str:
    """
    Handle the ~codemap command with pagination.
    
    Examples:
        ~codemap                    # Summary of current directory
        ~codemap /path/to/dir       # Summary of specific directory  
        ~codemap . 1                # Page 1 of current directory
        ~codemap /path 2            # Page 2 of specific directory
        ~codemap . search test      # Search for 'test' in current directory
        ~codemap clear              # Clear cache
    """
    # FORCE LOGGING AT ENTRY
    log_tool(
        tool_name="codemap_entry",
        input_data={"command": command, "directory": directory},
        output_data=None,
        metadata={"stage": "command_received"}
    )
    
    parts = command.split()
    
    # Handle cache clearing
    if len(parts) > 1 and parts[1] == "clear":
        _paginated_map.clear_cache()
        log_tool(
            tool_name="codemap_cache_clear",
            input_data={"command": command},
            output_data={"result": "cache_cleared"},
            metadata={}
        )
        return "✅ Code map cache cleared"
    
    # Parse arguments
    target_dir = directory
    page = None
    search_term = None
    
    # Fix parsing - handle the full command properly
    if len(parts) > 1:
        idx = 1
        # Check if first arg after ~codemap is a directory
        if idx < len(parts) and not parts[idx].isdigit() and parts[idx] != "search":
            target_dir = parts[idx]
            idx += 1
        
        # Now parse remaining args
        while idx < len(parts):
            if parts[idx] == "search" and idx + 1 < len(parts):
                search_term = parts[idx + 1]
                idx += 2
            elif parts[idx].isdigit():
                page = int(parts[idx])
                idx += 1
            else:
                idx += 1
    
    # Log parsed arguments
    log_tool(
        tool_name="codemap_parsed",
        input_data={"command": command},
        output_data={"target_dir": target_dir, "page": page, "search": search_term},
        metadata={"stage": "arguments_parsed"}
    )
    
    # Generate map
    try:
        output, metadata = _paginated_map.generate_map(target_dir, page, search_term)
        
        # Log successful generation
        log_tool(
            tool_name="codemap",
            input_data={"directory": target_dir, "page": page, "search": search_term},
            output_data=metadata,
            metadata={"output_length": len(output)}
        )
        
        return output
        
    except Exception as e:
        error_msg = f"❌ Error generating code map: {str(e)}"
        
        # Log error
        log_tool(
            tool_name="codemap",
            input_data={"directory": target_dir, "page": page, "search": search_term},
            output_data=None,
            error=e,
            metadata={"error_type": type(e).__name__}
        )
        
        return error_msg