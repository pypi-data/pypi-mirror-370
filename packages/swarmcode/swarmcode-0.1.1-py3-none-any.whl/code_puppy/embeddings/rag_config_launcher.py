#!/usr/bin/env python3
"""
Simple launcher for RAG configuration that works within Code Puppy's context.
"""

import os
import sys
import subprocess
from pathlib import Path
from rich.console import Console

def launch_rag_config(console: Console):
    """Launch RAG configuration in a subprocess to avoid event loop conflicts."""
    
    # Create a simple Python script to run the new interactive config
    script = '''
import sys
sys.path.insert(0, "/var/www/code_puppy")

from rich.console import Console
from code_puppy.embeddings.interactive_rag_config import InteractiveRAGConfig

console = Console()
config = InteractiveRAGConfig(console)
config.run()
'''
    
    # Write script to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        script_path = f.name
    
    try:
        # Run in subprocess
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]RAG configuration exited with code {result.returncode}[/red]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Configuration cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error launching configuration: {e}[/red]")
    finally:
        # Clean up temp file
        try:
            os.unlink(script_path)
        except:
            pass
    
    # Show current configuration after returning
    # Use instance-specific config path
    from code_puppy.utils.instance_manager import get_rag_config_path
    config_file = get_rag_config_path()
    if config_file.exists():
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        console.print("\n[bold green]Current RAG Configuration:[/bold green]")
        for key, value in config.items():
            if key == "api_key" and value:
                masked = value[:8] + "..." if len(value) > 8 else "***"
                console.print(f"  {key}: {masked}")
            else:
                console.print(f"  {key}: {value}")
    
    console.print("\n[dim]RAG configuration complete. You can now use /rag index to start indexing.[/dim]")