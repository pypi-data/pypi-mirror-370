# file_operations.py

import os
from typing import Any, Dict, List

from pydantic import BaseModel, StrictStr, StrictInt
from pydantic_ai import RunContext

from code_puppy.tools.common import console

# ---------------------------------------------------------------------------
# Module-level helper functions (exposed for unit tests _and_ used as tools)
# ---------------------------------------------------------------------------
from code_puppy.tools.common import should_ignore_path


class ListedFile(BaseModel):
    path: str | None
    type: str | None
    size: int = 0
    full_path: str | None
    depth: int | None


class ListFileOutput(BaseModel):
    files: List[ListedFile]


def _list_files(
    context: RunContext, directory: str = ".", recursive: bool = True
) -> ListFileOutput:
    results = []
    directory = os.path.abspath(directory)
    console.print("\n[bold white on blue] DIRECTORY LISTING [/bold white on blue]")
    console.print(
        f"\U0001f4c2 [bold cyan]{directory}[/bold cyan] [dim](recursive={recursive})[/dim]"
    )
    console.print("[dim]" + "-" * 60 + "[/dim]")
    if not os.path.exists(directory):
        console.print(
            f"[bold red]Error:[/bold red] Directory '{directory}' does not exist"
        )
        console.print("[dim]" + "-" * 60 + "[/dim]\n")
        return ListFileOutput(files=[ListedFile(**{"error": f"Directory '{directory}' does not exist"})])
    if not os.path.isdir(directory):
        console.print(f"[bold red]Error:[/bold red] '{directory}' is not a directory")
        console.print("[dim]" + "-" * 60 + "[/dim]\n")
        return ListFileOutput(files=[ListedFile(**{"error": f"'{directory}' is not a directory"})])
    
    # Count total files/dirs first
    total_files = 0
    total_dirs = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not should_ignore_path(os.path.join(root, d))]
        total_dirs += len(dirs)
        for f in files:
            if not should_ignore_path(os.path.join(root, f)):
                total_files += 1
        if not recursive:
            break
    
    # If too many files, use summary mode
    MAX_FILES = 500  # Limit to prevent token overflow
    use_summary = (total_files + total_dirs) > MAX_FILES
    
    if use_summary:
        # Import paginated code map for large directories
        from code_puppy.tools.paginated_code_map import handle_codemap_command
        from code_puppy.tools.tool_logger import log_tool
        
        log_tool(
            tool_name="list_files_using_codemap",
            input_data={"directory": directory, "total_files": total_files, "total_dirs": total_dirs},
            output_data=None,
            metadata={"reason": "directory_too_large", "limit": MAX_FILES}
        )
        
        # Get summary from paginated codemap
        summary_text = handle_codemap_command(f"~codemap {directory}", directory)
        
        console.print(f"[yellow]Directory contains {total_files:,} files and {total_dirs:,} directories.[/yellow]")
        console.print("[yellow]Showing summary to prevent token overflow:[/yellow]")
        console.print(summary_text)
        
        # Return a summary result
        return ListFileOutput(files=[
            ListedFile(**{
                "path": "SUMMARY",
                "type": "summary",
                "size": total_files,
                "full_path": directory,
                "depth": 0,
            })
        ])
    
    # Original logic for smaller directories
    folder_structure = {}
    file_list = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not should_ignore_path(os.path.join(root, d))]
        rel_path = os.path.relpath(root, directory)
        depth = 0 if rel_path == "." else rel_path.count(os.sep) + 1
        if rel_path == ".":
            rel_path = ""
        if rel_path:
            dir_path = os.path.join(directory, rel_path)
            results.append(
                ListedFile(**{
                    "path": rel_path,
                    "type": "directory",
                    "size": 0,
                    "full_path": dir_path,
                    "depth": depth,
                })
            )
            folder_structure[rel_path] = {
                "path": rel_path,
                "depth": depth,
                "full_path": dir_path,
            }
        for file in files:
            file_path = os.path.join(root, file)
            if should_ignore_path(file_path):
                continue
            rel_file_path = os.path.join(rel_path, file) if rel_path else file
            try:
                size = os.path.getsize(file_path)
                file_info = {
                    "path": rel_file_path,
                    "type": "file",
                    "size": size,
                    "full_path": file_path,
                    "depth": depth,
                }
                results.append(ListedFile(**file_info))
                file_list.append(file_info)
            except (FileNotFoundError, PermissionError):
                continue
        if not recursive:
            break

    def format_size(size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def get_file_icon(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".py", ".pyw"]:
            return "\U0001f40d"
        elif ext in [".js", ".jsx", ".ts", ".tsx"]:
            return "\U0001f4dc"
        elif ext in [".html", ".htm", ".xml"]:
            return "\U0001f310"
        elif ext in [".css", ".scss", ".sass"]:
            return "\U0001f3a8"
        elif ext in [".md", ".markdown", ".rst"]:
            return "\U0001f4dd"
        elif ext in [".json", ".yaml", ".yml", ".toml"]:
            return "\u2699\ufe0f"
        elif ext in [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"]:
            return "\U0001f5bc\ufe0f"
        elif ext in [".mp3", ".wav", ".ogg", ".flac"]:
            return "\U0001f3b5"
        elif ext in [".mp4", ".avi", ".mov", ".webm"]:
            return "\U0001f3ac"
        elif ext in [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]:
            return "\U0001f4c4"
        elif ext in [".zip", ".tar", ".gz", ".rar", ".7z"]:
            return "\U0001f4e6"
        elif ext in [".exe", ".dll", ".so", ".dylib"]:
            return "\u26a1"
        else:
            return "\U0001f4c4"

    if results:
        files = sorted(
            [f for f in results if f.type == "file"], key=lambda x: x.path
        )
        console.print(
            f"\U0001f4c1 [bold blue]{os.path.basename(directory) or directory}[/bold blue]"
        )
    all_items = sorted(results, key=lambda x: x.path)
    parent_dirs_with_content = set()
    for i, item in enumerate(all_items):
        if item.type == "directory" and not item.path:
            continue
        if os.sep in item.path:
            parent_path = os.path.dirname(item.path)
            parent_dirs_with_content.add(parent_path)
        depth = item.path.count(os.sep) + 1 if item.path else 0
        prefix = ""
        for d in range(depth):
            if d == depth - 1:
                prefix += "\u2514\u2500\u2500 "
            else:
                prefix += "    "
        name = os.path.basename(item.path) or item.path
        if item.type == "directory":
            console.print(f"{prefix}\U0001f4c1 [bold blue]{name}/[/bold blue]")
        else:
            icon = get_file_icon(item.path)
            size_str = format_size(item.size)
            console.print(
                f"{prefix}{icon} [green]{name}[/green] [dim]({size_str})[/dim]"
            )
    else:
        console.print("[yellow]Directory is empty[/yellow]")
    dir_count = sum(1 for item in results if item.type == "directory")
    file_count = sum(1 for item in results if item.type == "file")
    total_size = sum(item.size for item in results if item.type == "file")
    console.print("\n[bold cyan]Summary:[/bold cyan]")
    console.print(
        f"\U0001f4c1 [blue]{dir_count} directories[/blue], \U0001f4c4 [green]{file_count} files[/green] [dim]({format_size(total_size)} total)[/dim]"
    )
    console.print("[dim]" + "-" * 60 + "[/dim]\n")
    return ListFileOutput(files=results)


class ReadFileOutput(BaseModel):
    content: str | None

def _read_file(context: RunContext, file_path: str) -> ReadFileOutput:
    file_path = os.path.abspath(file_path)
    console.print(
        f"\n[bold white on blue] READ FILE [/bold white on blue] \U0001f4c2 [bold cyan]{file_path}[/bold cyan]"
    )
    console.print("[dim]" + "-" * 60 + "[/dim]")
    if not os.path.exists(file_path):
        return ReadFileOutput(content=f"File '{file_path}' does not exist")
    if not os.path.isfile(file_path):
        return ReadFileOutput(content=f"'{file_path}' is not a file")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Limit file content to prevent token explosion
        MAX_FILE_SIZE = 50000  # 50KB max
        if len(content) > MAX_FILE_SIZE:
            from code_puppy.tools.output_manager import OutputManager
            console.print(f"[yellow]File is {len(content):,} bytes - compacting to {MAX_FILE_SIZE:,} bytes[/yellow]")
            content = OutputManager._compact_file_content(content)
        
        return ReadFileOutput(content=content)
    except Exception as exc:
        return ReadFileOutput(content="FILE NOT FOUND")


class MatchInfo(BaseModel):
    file_path: str | None
    line_number: int | None
    line_content: str | None

class GrepOutput(BaseModel):
    matches: List[MatchInfo]

def _grep(
    context: RunContext, search_string: str, directory: str = "."
) -> GrepOutput:
    matches: List[MatchInfo] = []
    directory = os.path.abspath(directory)
    console.print(
        f"\n[bold white on blue] GREP [/bold white on blue] \U0001f4c2 [bold cyan]{directory}[/bold cyan] [dim]for '{search_string}'[/dim]"
    )
    console.print("[dim]" + "-" * 60 + "[/dim]")
    
    # Import output manager for smart compaction
    from code_puppy.tools.output_manager import OutputManager
    
    # Check cache first
    cached = OutputManager.get_cached_output("grep", {"search": search_string, "dir": directory})
    if cached:
        console.print("[dim]Using cached grep results[/dim]")
        # Parse cached results back to matches
        # For now, just return empty with note
        console.print(cached)
        return GrepOutput(matches=[])
    
    # Limit matches to prevent token explosion
    MAX_MATCHES = 50  # Reduced from 200
    MAX_OUTPUT_SIZE = 10000  # 10KB max for grep output
    total_output_size = 0

    for root, dirs, files in os.walk(directory, topdown=True):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if not should_ignore_path(os.path.join(root, d))]

        for f_name in files:
            file_path = os.path.join(root, f_name)

            if should_ignore_path(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                    for line_number, line_content in enumerate(fh, 1):
                        if search_string in line_content:
                            # Limit line content to 200 chars
                            truncated_content = line_content.strip()[:200]
                            if len(line_content.strip()) > 200:
                                truncated_content += "..."
                            
                            match_info = MatchInfo(**{
                                "file_path": file_path,
                                "line_number": line_number,
                                "line_content": truncated_content,
                            })
                            matches.append(match_info)
                            
                            # Track total output size
                            total_output_size += len(file_path) + len(truncated_content) + 20
                            
                            # Stop if we hit limits
                            if len(matches) >= MAX_MATCHES or total_output_size >= MAX_OUTPUT_SIZE:
                                console.print(
                                    f"[yellow]Limit reached ({len(matches)} matches, {total_output_size:,} bytes). Stopping search.[/yellow]"
                                )
                                # Cache the results
                                output_text = f"Found {len(matches)} matches for '{search_string}'"
                                OutputManager.cache_output("grep", {"search": search_string, "dir": directory}, output_text)
                                return GrepOutput(matches=matches)
            except FileNotFoundError:
                console.print(
                    f"[yellow]File not found (possibly a broken symlink): {file_path}[/yellow]"
                )
                continue
            except UnicodeDecodeError:
                console.print(
                    f"[yellow]Cannot decode file (likely binary): {file_path}[/yellow]"
                )
                continue
            except Exception as e:
                console.print(f"[red]Error processing file {file_path}: {e}[/red]")
                continue

    if not matches:
        console.print(
            f"[yellow]No matches found for '{search_string}' in {directory}[/yellow]"
        )
    else:
        console.print(
            f"[green]Found {len(matches)} match(es) for '{search_string}' in {directory}[/green]"
        )

    return GrepOutput(matches=[])


def register_file_operations_tools(agent):
    @agent.tool
    def list_files(
        context: RunContext, directory: str = ".", recursive: bool = True
    ) -> ListFileOutput:
        return _list_files(context, directory, recursive)

    @agent.tool
    def read_file(context: RunContext, file_path: str = "") -> ReadFileOutput:
        return _read_file(context, file_path)

    @agent.tool
    def grep(
        context: RunContext, search_string: str = "", directory: str = "."
    ) -> GrepOutput:
        return _grep(context, search_string, directory)
