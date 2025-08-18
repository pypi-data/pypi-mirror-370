import os
import re
from typing import List, Tuple

from rich.table import Table


def list_directory(path: str = None) -> Tuple[List[str], List[str]]:
    """
    Returns (dirs, files) for the specified path, splitting out directories and files.
    """
    if path is None:
        path = os.getcwd()
    entries = []
    try:
        entries = [e for e in os.listdir(path)]
    except Exception as e:
        raise RuntimeError(f"Error listing directory: {e}")
    dirs = [e for e in entries if os.path.isdir(os.path.join(path, e))]
    files = [e for e in entries if not os.path.isdir(os.path.join(path, e))]
    return dirs, files


def make_directory_table(path: str = None) -> Table:
    """
    Returns a rich.Table object containing the directory listing.
    """
    if path is None:
        path = os.getcwd()
    dirs, files = list_directory(path)
    table = Table(
        title=f"\U0001f4c1 [bold blue]Current directory:[/bold blue] [cyan]{path}[/cyan]"
    )
    table.add_column("Type", style="dim", width=8)
    table.add_column("Name", style="bold")
    for d in sorted(dirs):
        table.add_row("[green]dir[/green]", f"[cyan]{d}[/cyan]")
    for f in sorted(files):
        table.add_row("[yellow]file[/yellow]", f"{f}")
    return table


def escape_rich_markup(text: str) -> str:
    """
    Escape Rich markup characters in text to prevent injection attacks.
    This prevents user input from being interpreted as Rich formatting.
    """
    if not text:
        return text
    
    # Escape square brackets used for Rich markup
    text = text.replace('[', '\\[').replace(']', '\\]')
    
    # Also escape curly braces that might be interpreted
    text = text.replace('{', '\\{').replace('}', '\\}')
    
    return text


def sanitize_for_display(text: str, max_display_length: int = 25, max_total_length: int = 10000) -> str:
    """
    Sanitize text for safe display in console output.
    Handles Rich markup, ANSI sequences, and other edge cases.
    If text is longer than max_display_length, shows a summary instead.
    """
    if not text:
        return text
    
    # First clean the text
    # Remove ANSI escape sequences
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned_text = ansi_escape.sub('', text)
    
    # Remove null bytes and other control characters (except newlines and tabs)
    cleaned_text = ''.join(char if char in ('\n', '\t') or (ord(char) >= 32 and ord(char) != 127) else '' for char in cleaned_text)
    
    # Check if this looks like pasted content (multi-line or long)
    is_pasted = '\n' in cleaned_text or len(cleaned_text) > max_display_length
    
    if is_pasted:
        # For pasted content, show a summary
        line_count = cleaned_text.count('\n') + 1
        char_count = len(cleaned_text)
        
        # Extract first line for preview (if reasonable)
        first_line = cleaned_text.split('\n')[0]
        if len(first_line) <= 50:
            preview = escape_rich_markup(first_line[:50])
            if line_count > 1:
                return f"[dim][pasted content: {char_count} characters, {line_count} lines][/dim]\n[dim]Preview: {preview}...[/dim]"
            else:
                return f"[dim][pasted content: {char_count} characters][/dim]\n[dim]Preview: {preview}...[/dim]"
        else:
            # For very long first lines, just show character count
            if line_count > 1:
                return f"[dim][pasted content: {char_count} characters, {line_count} lines][/dim]"
            else:
                return f"[dim][pasted content: {char_count} characters][/dim]"
    else:
        # For short, typed content, just escape markup
        return escape_rich_markup(cleaned_text)


def is_likely_command(text: str) -> bool:
    """
    Determine if text is likely an intentional command vs pasted content.
    Commands are typically short, single-line, and start with specific patterns.
    """
    if not text:
        return False
    
    # Strip whitespace for analysis
    stripped = text.strip()
    
    # Multi-line input is likely pasted content, not a command
    if '\n' in stripped:
        return False
    
    # Very long single lines are likely pasted content
    if len(stripped) > 200:
        return False
    
    # Check if it starts with known command prefixes
    command_prefixes = ('/', '~')
    if not any(stripped.startswith(prefix) for prefix in command_prefixes):
        return False
    
    # Check if it matches known command patterns
    known_commands = [
        r'^[/~](help|h|cd|codemap|m|motd|show|set|logs|rag|clear|exit|quit)(\s|$)',
    ]
    
    for pattern in known_commands:
        if re.match(pattern, stripped, re.IGNORECASE):
            return True
    
    # If it starts with / or ~ but doesn't match known commands,
    # and it contains certain patterns, it's likely pasted content
    suspicious_patterns = ['[/', ']/', '/{', '}/', '[', ']', '{', '}', '\\']
    if any(pattern in stripped for pattern in suspicious_patterns):
        return False
    
    # Check if the rest looks like a simple command (alphanumeric with spaces)
    # This helps distinguish "/somecommand args" from "/weird[stuff]"
    command_part = stripped[1:].strip()  # Remove the / or ~ prefix
    if command_part and not re.match(r'^[a-zA-Z0-9_\-\s./]+$', command_part):
        return False
    
    # Default to treating unknown slash commands as commands 
    # (will show "unknown command" error)
    return True


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize exception messages for safe display.
    """
    error_msg = str(error)
    return sanitize_for_display(error_msg)
