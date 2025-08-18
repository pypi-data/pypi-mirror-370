#!/usr/bin/env python3
"""
RAG Enhancer V2 - Complete replacement using RooCode-style architecture.
This replaces the old rag_enhancer.py completely.
"""

import os
import sys
import logging
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import json

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

# Import instance manager for unique paths and ports
from code_puppy.utils.instance_manager import (
    get_rag_config_path,
    get_embeddings_cache_dir,
    allocate_port,
    get_port,
    get_instance_id
)

# Configure debug logging
DEBUG_MODE = os.getenv("RAG_DEBUG", "false").lower() == "true"
LOG_FILE = Path.cwd() / "rag_debug.log"

# Set up logging
def setup_debug_logging():
    """Configure comprehensive debug logging."""
    if DEBUG_MODE:
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(LOG_FILE, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler for errors
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Log startup
        logging.info("="*60)
        logging.info("RAG Debug Mode Enabled - Session Started")
        logging.info(f"Log file: {LOG_FILE}")
        logging.info(f"Working directory: {os.getcwd()}")
        logging.info("="*60)
    else:
        # Minimal logging when not in debug mode
        logging.basicConfig(level=logging.WARNING)

# Initialize logging
setup_debug_logging()
logger = logging.getLogger(__name__)

class RAGEnhancerV2:
    """
    New RAG Enhancer using RooCode-style architecture.
    Complete replacement for the old system.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the new RAG enhancer."""
        self.console = console or Console()
        self.enabled = os.getenv("ENABLE_RAG", "false").lower() == "true"
        self.manager = None
        self._initialized = False
        self.config = None
        
        logger.debug(f"RAGEnhancerV2 initialized - enabled: {self.enabled}")
        
        if self.enabled:
            self._load_config()
    
    def _load_config(self):
        """Load configuration from instance-specific file."""
        # Use instance-specific config path
        config_file = get_rag_config_path()
        
        # Also check legacy location for migration
        legacy_config = Path.home() / ".code_puppy" / "embeddings" / "config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded config from {config_file}: {self.config}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self.config = None
        elif legacy_config.exists():
            # Migrate from legacy config
            try:
                with open(legacy_config, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Migrating config from legacy location: {self.config}")
                # Save to new location
                config_file.parent.mkdir(parents=True, exist_ok=True)
                with open(config_file, 'w') as f:
                    json.dump(self.config, f, indent=2)
            except Exception as e:
                logger.error(f"Failed to migrate legacy config: {e}")
                self.config = None
        else:
            logger.warning(f"No config file found at {config_file}")
            # Allocate dynamic port for this instance
            embeddings_port = allocate_port("embeddings", 8001)
            
            # Default to OpenAI-compatible local with dynamic port
            self.config = {
                "provider": "openai-compatible",
                "base_url": f"http://localhost:{embeddings_port}",
                "model": "default"
            }
            logger.info(f"Using default config: {self.config}")
    
    async def initialize(self):
        """Initialize the RAG system asynchronously."""
        if not self.enabled:
            logger.debug("RAG not enabled, skipping initialization")
            return False
        
        try:
            logger.info("Initializing RAG system...")
            
            # Import the new embedding manager
            from code_puppy.embeddings.embedding_manager import EmbeddingManager
            
            # Create manager
            self.manager = EmbeddingManager(console=self.console)
            
            # Initialize with config
            success = await self.manager.initialize(self.config)
            
            if success:
                self._initialized = True
                logger.info("RAG system initialized successfully")
                logger.debug(f"Provider: {self.manager.provider}")
                logger.debug(f"Cache dir: {self.manager.cache_dir}")
            else:
                logger.error("Failed to initialize RAG manager")
                
            return success
            
        except Exception as e:
            logger.exception(f"Error initializing RAG: {e}")
            return False
    
    def display_rag_context(self, query: str):
        """Display RAG context in the terminal UI."""
        if not self.enabled or not self._initialized:
            logger.debug(f"Skipping context display - enabled: {self.enabled}, initialized: {self._initialized}")
            return
        
        logger.info(f"Searching for context: {query}")
        
        try:
            # Check if there's already a running event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, can't use run_until_complete
                # For now, skip RAG context display when in async context
                logger.info("Event loop already running, skipping RAG context display")
                return
            except RuntimeError:
                # No running loop, safe to create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def search():
                    results = await self.manager.search(query, limit=3)
                    return results
                
                results = loop.run_until_complete(search())
                loop.close()
            
            logger.debug(f"Found {len(results)} results")
            
            if not results:
                logger.info("No relevant context found")
                return
            
            # Display results
            self.console.print()
            self.console.print("🔍 [bold cyan]RAG Context Found[/bold cyan]", justify="left")
            self.console.print("─" * 60)
            
            for i, result in enumerate(results, 1):
                logger.debug(f"Result {i}: {result.file_path} (score: {result.score:.3f})")
                
                # Create syntax-highlighted panel
                lang = "python" if result.file_path.endswith('.py') else "text"
                content = result.content[:300]  # Limit display length
                
                syntax = Syntax(
                    content,
                    lang,
                    theme="monokai",
                    line_numbers=False,
                    word_wrap=True
                )
                
                panel = Panel(
                    syntax,
                    title=f"[{i}] {result.file_path} (score: {result.score:.2%})",
                    title_align="left",
                    border_style="cyan",
                    padding=(0, 1)
                )
                
                self.console.print(panel)
            
            self.console.print("─" * 60)
            self.console.print()
            
        except Exception as e:
            logger.exception(f"Error displaying context: {e}")
    
    async def index_workspace(self, directory: str = ".", max_files: Optional[int] = None):
        """Index a workspace directory."""
        if not self._initialized:
            logger.error("Cannot index - not initialized")
            return
        
        logger.info(f"Starting workspace indexing: {directory} (max_files: {max_files})")
        
        try:
            # Use the new manager's indexing
            stats = await self.manager.index_directory(
                directory,
                patterns=["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"],
                ignore_patterns=["*node_modules*", "*__pycache__*", "*.git*"],
                show_progress=True
            )
            
            logger.info(f"Indexing complete: {stats}")
            return stats
            
        except Exception as e:
            logger.exception(f"Error indexing workspace: {e}")
            return None

# Global instance
_rag_enhancer_v2: Optional[RAGEnhancerV2] = None

def get_rag_enhancer(console: Optional[Console] = None) -> RAGEnhancerV2:
    """Get or create the global RAG enhancer (V2)."""
    global _rag_enhancer_v2
    
    if _rag_enhancer_v2 is None:
        logger.info("Creating new RAGEnhancerV2 instance")
        _rag_enhancer_v2 = RAGEnhancerV2(console)
        
        # Try to initialize if enabled
        if _rag_enhancer_v2.enabled:
            try:
                # Check if there's already a running event loop
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an async context, can't use run_until_complete
                    # Just log that initialization should happen later
                    logger.info("Event loop already running, will initialize on first use")
                except RuntimeError:
                    # No running loop, safe to create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(_rag_enhancer_v2.initialize())
                    loop.close()
            except Exception as e:
                logger.error(f"Failed to auto-initialize: {e}")
    
    return _rag_enhancer_v2

def display_rag_context(query: str, console: Optional[Console] = None):
    """Display RAG context for a query (convenience function)."""
    logger.debug(f"display_rag_context called with query: {query}")
    enhancer = get_rag_enhancer(console)
    enhancer.display_rag_context(query)

def enable_debug_mode():
    """Enable debug mode at runtime."""
    global DEBUG_MODE
    DEBUG_MODE = True
    os.environ["RAG_DEBUG"] = "true"
    setup_debug_logging()
    logger.info("Debug mode enabled at runtime")

def disable_debug_mode():
    """Disable debug mode at runtime."""
    global DEBUG_MODE
    DEBUG_MODE = False
    os.environ["RAG_DEBUG"] = "false"
    logging.getLogger().setLevel(logging.WARNING)
    logger.info("Debug mode disabled")