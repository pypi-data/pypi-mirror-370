"""Command to view tool logs."""

import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.json import JSON
from rich.panel import Panel
from datetime import datetime


def view_tool_logs(command: str, console: Console) -> bool:
    """Handle ~logs command to view tool execution logs.
    
    Args:
        command: The command string starting with ~logs
        console: Rich console for output
        
    Returns:
        True if command was handled
    """
    parts = command.split()
    
    # Default to showing recent logs
    count = 10
    mode = "recent"
    
    # Parse arguments
    if len(parts) > 1:
        if parts[1] == "errors":
            mode = "errors"
            count = int(parts[2]) if len(parts) > 2 else 10
        elif parts[1] == "clear":
            mode = "clear"
        elif parts[1] == "json":
            mode = "json"
            count = int(parts[2]) if len(parts) > 2 else 5
        elif parts[1] == "stats":
            mode = "stats"
        else:
            try:
                count = int(parts[1])
            except ValueError:
                console.print(f"[red]Invalid argument: {parts[1]}[/red]")
                console.print("Usage: ~logs [count|errors|clear|json|stats]")
                return True
    
    # Get log file path
    log_file = Path.home() / ".code_puppy" / "tool_logs.json"
    
    if not log_file.exists():
        console.print("[yellow]No log file found. Logs will be created when tools are used.[/yellow]")
        return True
    
    try:
        logs = json.loads(log_file.read_text() or "[]")
    except Exception as e:
        console.print(f"[red]Error reading logs: {e}[/red]")
        return True
    
    if mode == "clear":
        log_file.write_text("[]")
        console.print("[green]Logs cleared successfully[/green]")
        return True
    
    if mode == "stats":
        # Show statistics
        total = len(logs)
        errors = sum(1 for log in logs if not log.get("success", True))
        tools = {}
        methods = {}
        
        for log in logs:
            tool = log.get("tool", "unknown")
            tools[tool] = tools.get(tool, 0) + 1
            
            if tool == "smart_truncate":
                method = log.get("operation", {}).get("method") or log.get("tool")
                methods[method] = methods.get(method, 0) + 1
        
        console.print(Panel(f"""[bold cyan]Tool Log Statistics[/bold cyan]
        
Total entries: [yellow]{total}[/yellow]
Errors: [red]{errors}[/red]
Success rate: [green]{((total-errors)/total*100):.1f}%[/green] if total > 0 else N/A

[bold]Tools Used:[/bold]
{chr(10).join(f"  • {tool}: {count}" for tool, count in sorted(tools.items(), key=lambda x: -x[1]))}

[bold]Smart Truncate Methods:[/bold]
{chr(10).join(f"  • {method}: {count}" for method, count in sorted(methods.items(), key=lambda x: -x[1]))}
"""))
        return True
    
    if mode == "json":
        # Show raw JSON
        recent = logs[-count:]
        for log in recent:
            console.print(Panel(JSON(json.dumps(log, indent=2)), title=f"[cyan]{log.get('timestamp', 'N/A')}[/cyan]"))
        return True
    
    if mode == "errors":
        # Show only errors
        error_logs = [log for log in logs if not log.get("success", True)][-count:]
        if not error_logs:
            console.print("[green]No errors found in logs[/green]")
            return True
    else:
        # Show recent logs
        error_logs = logs[-count:]
    
    if not error_logs:
        console.print("[yellow]No logs to display[/yellow]")
        return True
    
    # Create table
    table = Table(title=f"Tool Execution Logs ({mode})")
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Tool", style="magenta")
    table.add_column("Method/Operation", style="yellow")
    table.add_column("Input → Output", style="white")
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")
    
    for log in error_logs:
        timestamp = log.get("timestamp", "N/A")
        if timestamp != "N/A":
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%H:%M:%S")
            except:
                pass
        
        tool = log.get("tool", "unknown")
        success = log.get("success", True)
        status = "[green]✓[/green]" if success else "[red]✗[/red]"
        
        # Get method/operation
        if tool == "smart_truncate":
            method = log.get("operation", {}).get("method") or log.get("tool")
            input_size = log.get("operation", {}).get("input_size", 0)
            output_size = log.get("operation", {}).get("output_size", 0)
            size_info = f"{input_size:,} → {output_size:,}"
        else:
            method = log.get("operation", {}).get("method", "execute")
            input_info = log.get("input", {})
            output_info = log.get("output", {})
            size_info = f"{input_info.get('size', 0):,} → {output_info.get('size', 0):,}"
        
        # Get details
        details = []
        if not success and log.get("error"):
            error = log["error"]
            details.append(f"Error: {error.get('type', 'Unknown')}")
            details.append(f"{error.get('message', '')[:50]}")
        elif log.get("details"):
            det = log["details"]
            if "reason" in det:
                details.append(f"Reason: {det['reason']}")
            if "chunks" in log:
                details.append(f"Chunks: {log['chunks']}")
            if "api_calls" in log:
                details.append(f"API calls: {log['api_calls']}")
        
        table.add_row(
            timestamp,
            tool,
            method,
            size_info,
            status,
            "\n".join(details) if details else "-"
        )
    
    console.print(table)
    console.print(f"\n[dim]Log file: {log_file}[/dim]")
    console.print("[dim]Commands: ~logs [count], ~logs errors, ~logs clear, ~logs json, ~logs stats[/dim]")
    
    return True