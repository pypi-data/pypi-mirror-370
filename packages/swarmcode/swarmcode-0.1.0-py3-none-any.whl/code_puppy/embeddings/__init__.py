"""
Code Puppy Embeddings Module - RooCode-style Architecture

This module provides flexible embeddings functionality with support for multiple providers
like OpenAI, Ollama, Mistral, Cerebras, and any OpenAI-compatible API.

Features:
- Multiple embedding provider support (OpenAI, Ollama, Mistral, etc.)
- Provider-agnostic architecture with configurable models
- Async non-blocking indexing with progress tracking
- Incremental indexing with file hash tracking
- Cache persistence between sessions
- Beautiful TUI for configuration
- Compatible with any OpenAI-format API
"""

from typing import Optional

# Try importing new RooCode-style components first
try:
    from .embedding_manager import (
        EmbeddingManager,
        IndexingState,
        IndexEntry,
        SearchResult,
        IndexingProgress
    )
    from .provider_factory import (
        EmbeddingProviderFactory,
        EmbeddingProviderType
    )
    from .providers.base import (
        BaseEmbeddingProvider,
        EmbeddingModelProfile,
        EmbeddingResult
    )
    from .rag_tui import launch_rag_tui
    
    # Mark new system as available
    ROOCODE_STYLE_AVAILABLE = True
    
except ImportError:
    # Fallback to old system if new modules not available
    ROOCODE_STYLE_AVAILABLE = False
    
    # Core components (old system)
    from .vector_store import QdrantVectorStore
    from .embedder import LocalEmbedder
    from .chunker import CodeChunker
    from .cache import EmbeddingCache
    from .memory import ConversationMemory
    from .manager import EmbeddingManager

    # Utilities
    from .batch_processor import BatchProcessor
    from .search import SearchService
    from .similarity import cosine_similarity, euclidean_distance
    from .progress import IndexingProgress
    from .context_injector import ContextInjector

    # Configuration
    from .config import EmbeddingConfig, get_embedding_config

__all__ = [
    # Core components
    'QdrantVectorStore',
    'LocalEmbedder',
    'CodeChunker',
    'EmbeddingCache',
    'ConversationMemory',
    'EmbeddingManager',
    
    # Utilities
    'BatchProcessor',
    'SearchService',
    'cosine_similarity',
    'euclidean_distance',
    'IndexingProgress',
    'ContextInjector',
    
    # Configuration
    'EmbeddingConfig',
    'get_embedding_config',
    
    # Convenience functions
    'initialize_embeddings',
    'get_manager',
]

# Global manager instance
_manager: Optional[EmbeddingManager] = None

def initialize_embeddings(workspace_path: str, config: Optional[dict] = None) -> EmbeddingManager:
    """
    Initialize the global embedding manager.
    
    Args:
        workspace_path: Path to the workspace to index
        config: Optional configuration dictionary
        
    Returns:
        EmbeddingManager instance
    """
    global _manager
    if _manager is None:
        _manager = EmbeddingManager(workspace_path, config or get_embedding_config())
    return _manager

def get_manager() -> Optional[EmbeddingManager]:
    """
    Get the global embedding manager instance.
    
    Returns:
        EmbeddingManager instance or None if not initialized
    """
    return _manager

def cleanup():
    """Clean up resources and stop background processes."""
    global _manager
    if _manager:
        _manager.stop_background_indexer()
        _manager = None