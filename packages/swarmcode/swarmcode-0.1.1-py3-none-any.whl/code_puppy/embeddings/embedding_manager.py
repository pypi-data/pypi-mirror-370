#!/usr/bin/env python3
"""
Main embedding manager that handles indexing, searching, and state management.
RooCode-style architecture with async operations and progress tracking.
"""

import os
import asyncio
import json
import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import pickle

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table

from .provider_factory import EmbeddingProviderFactory, EmbeddingProviderType
from .providers.base import BaseEmbeddingProvider

# Import instance manager for unique paths
try:
    from code_puppy.utils.instance_manager import get_embeddings_cache_dir
except ImportError:
    # Fallback if instance manager not available
    def get_embeddings_cache_dir():
        return Path.home() / ".code_puppy" / "embeddings"

logger = logging.getLogger(__name__)

class IndexingState(Enum):
    """State of the indexing system."""
    STANDBY = "standby"
    INITIALIZING = "initializing"
    INDEXING = "indexing"
    READY = "ready"
    ERROR = "error"

@dataclass
class IndexEntry:
    """Represents an indexed file or chunk."""
    file_path: str
    content: str
    embedding: List[float]
    chunk_index: int = 0
    total_chunks: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    indexed_at: datetime = field(default_factory=datetime.now)
    file_hash: Optional[str] = None

@dataclass
class SearchResult:
    """Result from a search query."""
    file_path: str
    content: str
    score: float
    chunk_index: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class IndexingProgress:
    """Track indexing progress."""
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    total_chunks: int = 0
    current_file: str = ""
    state: IndexingState = IndexingState.STANDBY
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100

class EmbeddingManager:
    """
    Main manager for embedding operations.
    Handles indexing, searching, caching, and state management.
    """
    
    def __init__(
        self,
        provider: Optional[BaseEmbeddingProvider] = None,
        cache_dir: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        console: Optional[Console] = None
    ):
        """Initialize the embedding manager."""
        self.provider = provider
        # Use instance-specific cache directory
        self.cache_dir = Path(cache_dir) if cache_dir else get_embeddings_cache_dir()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.console = console or Console()
        
        # State management
        self.progress = IndexingProgress()
        self.index: Dict[str, List[IndexEntry]] = {}
        self._file_hashes: Dict[str, str] = {}
        self._initialized = False
        
        # Progress callbacks
        self._progress_callbacks: List[Callable[[IndexingProgress], None]] = []
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self, provider_config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the manager with a provider."""
        try:
            self.progress.state = IndexingState.INITIALIZING
            
            # Create provider if not provided
            if not self.provider:
                if not provider_config:
                    # Default to OpenAI-compatible local provider
                    provider_config = {
                        "provider": "openai-compatible",
                        "base_url": "http://localhost:8001"
                    }
                
                provider_type = provider_config.get("provider", "openai-compatible")
                self.provider = EmbeddingProviderFactory.create_provider(
                    provider_type,
                    provider_config
                )
            
            # Initialize provider
            if not await self.provider.initialize():
                raise Exception("Failed to initialize embedding provider")
            
            # Load cached index if exists
            await self.load_cache()
            
            self._initialized = True
            self.progress.state = IndexingState.READY
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding manager: {e}")
            self.progress.state = IndexingState.ERROR
            self.progress.error = str(e)
            return False
    
    def add_progress_callback(self, callback: Callable[[IndexingProgress], None]):
        """Add a callback for progress updates."""
        self._progress_callbacks.append(callback)
    
    def _notify_progress(self):
        """Notify all progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(self.progress)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    async def index_file(self, file_path: str, content: str) -> int:
        """
        Index a single file.
        
        Returns:
            Number of chunks created
        """
        # Check if file needs reindexing
        file_hash = hashlib.md5(content.encode()).hexdigest()
        if file_path in self._file_hashes and self._file_hashes[file_path] == file_hash:
            logger.debug(f"Skipping {file_path} - already indexed and unchanged")
            return 0
        
        # Remove old entries if exists
        if file_path in self.index:
            del self.index[file_path]
        
        # Chunk the content
        chunks = self._chunk_text(content)
        
        # Create embeddings for all chunks
        texts = [chunk for chunk in chunks]
        if not texts:
            return 0
        
        result = await self.provider.embed_texts(texts)
        
        # Create index entries
        entries = []
        for i, (chunk, embedding) in enumerate(zip(chunks, result.embeddings)):
            entry = IndexEntry(
                file_path=file_path,
                content=chunk,
                embedding=embedding,
                chunk_index=i,
                total_chunks=len(chunks),
                file_hash=file_hash
            )
            entries.append(entry)
        
        # Store in index
        self.index[file_path] = entries
        self._file_hashes[file_path] = file_hash
        
        return len(entries)
    
    async def index_directory(
        self,
        directory: str,
        patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Index all files in a directory.
        
        Args:
            directory: Directory to index
            patterns: File patterns to include (e.g., ["*.py", "*.js"])
            ignore_patterns: Patterns to ignore
            show_progress: Show progress bar
        
        Returns:
            Indexing statistics
        """
        self.progress.state = IndexingState.INDEXING
        self.progress.started_at = datetime.now()
        self.progress.error = None
        
        # Default patterns
        if not patterns:
            patterns = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.cpp", "*.c", "*.h"]
        
        # Collect files
        files = []
        base_path = Path(directory)
        for pattern in patterns:
            files.extend(base_path.rglob(pattern))
        
        # Filter ignored patterns
        if ignore_patterns:
            import fnmatch
            filtered_files = []
            for file in files:
                skip = False
                for ignore in ignore_patterns:
                    if fnmatch.fnmatch(str(file), ignore):
                        skip = True
                        break
                if not skip:
                    filtered_files.append(file)
            files = filtered_files
        
        self.progress.total_files = len(files)
        self.progress.processed_files = 0
        self.progress.failed_files = 0
        self.progress.total_chunks = 0
        
        # Index files with progress
        if show_progress:
            await self._index_with_progress(files)
        else:
            await self._index_without_progress(files)
        
        # Save cache
        await self.save_cache()
        
        # Update state
        self.progress.state = IndexingState.READY
        self.progress.completed_at = datetime.now()
        
        # Return statistics
        return {
            "total_files": self.progress.total_files,
            "processed_files": self.progress.processed_files,
            "failed_files": self.progress.failed_files,
            "total_chunks": self.progress.total_chunks,
            "duration": (self.progress.completed_at - self.progress.started_at).total_seconds()
        }
    
    async def _index_with_progress(self, files: List[Path]):
        """Index files with progress bar."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[cyan]{task.completed}/{task.total}[/cyan] files"),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task(
                "[bold cyan]Indexing files...[/bold cyan]",
                total=len(files)
            )
            
            for file_path in files:
                self.progress.current_file = str(file_path)
                progress.update(
                    task,
                    description=f"[bold cyan]Indexing:[/bold cyan] {file_path.name}"
                )
                
                try:
                    # Read file
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Index it
                    chunks = await self.index_file(str(file_path), content)
                    
                    self.progress.processed_files += 1
                    self.progress.total_chunks += chunks
                    
                except Exception as e:
                    logger.error(f"Failed to index {file_path}: {e}")
                    self.progress.failed_files += 1
                
                progress.update(task, advance=1)
                self._notify_progress()
    
    async def _index_without_progress(self, files: List[Path]):
        """Index files without progress bar."""
        for file_path in files:
            self.progress.current_file = str(file_path)
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                chunks = await self.index_file(str(file_path), content)
                
                self.progress.processed_files += 1
                self.progress.total_chunks += chunks
                
            except Exception as e:
                logger.error(f"Failed to index {file_path}: {e}")
                self.progress.failed_files += 1
            
            self._notify_progress()
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """
        Search the index for relevant content.
        
        Args:
            query: Search query
            limit: Maximum results to return
            score_threshold: Minimum similarity score
        
        Returns:
            List of search results
        """
        if not self._initialized:
            raise RuntimeError("Manager not initialized")
        
        # Get query embedding
        query_embedding = await self.provider.embed_query(query)
        
        # Get score threshold from model profile if not provided
        if score_threshold is None:
            profile = self.provider.get_model_profile(self.provider.get_default_model())
            score_threshold = profile.score_threshold
        
        # Search through all entries
        results = []
        for file_path, entries in self.index.items():
            for entry in entries:
                # Calculate cosine similarity
                score = self._cosine_similarity(query_embedding, entry.embedding)
                
                if score >= score_threshold:
                    results.append(SearchResult(
                        file_path=file_path,
                        content=entry.content,
                        score=score,
                        chunk_index=entry.chunk_index,
                        metadata=entry.metadata
                    ))
        
        # Sort by score and limit
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
    
    def _chunk_text(self, text: str) -> List[str]:
        """Chunk text into overlapping segments."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end])
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def save_cache(self):
        """Save index to cache file."""
        cache_file = self.cache_dir / "index.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'index': self.index,
                    'file_hashes': self._file_hashes,
                    'metadata': {
                        'provider': str(self.provider),
                        'chunk_size': self.chunk_size,
                        'chunk_overlap': self.chunk_overlap
                    }
                }, f)
            logger.info(f"Saved index cache to {cache_file}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    async def load_cache(self):
        """Load index from cache file."""
        cache_file = self.cache_dir / "index.pkl"
        if not cache_file.exists():
            return
        
        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
                self.index = data.get('index', {})
                self._file_hashes = data.get('file_hashes', {})
                logger.info(f"Loaded {len(self.index)} files from cache")
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
    
    async def clear_index(self):
        """Clear the entire index."""
        self.index.clear()
        self._file_hashes.clear()
        self.progress = IndexingProgress()
        
        # Remove cache file
        cache_file = self.cache_dir / "index.pkl"
        if cache_file.exists():
            cache_file.unlink()
    
    async def close(self):
        """Clean up resources."""
        if self.provider:
            await self.provider.close()
        self._initialized = False