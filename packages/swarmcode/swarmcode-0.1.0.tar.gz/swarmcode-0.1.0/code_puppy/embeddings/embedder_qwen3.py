"""
Unified Qwen3 Embedding implementation.

This module provides the ACTUAL Qwen3-Embedding model, either through:
1. Direct HuggingFace transformers (recommended)
2. Ollama with custom modelfile (if configured)
"""

import os
import logging
from typing import List, Optional
from .embedder import LocalEmbedder

# Try to import HuggingFace version
try:
    from .qwen3_embedder import Qwen3Embedder
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logging.warning("HuggingFace transformers not available. Will fall back to Ollama.")

class Qwen3EmbeddingProvider:
    """
    Provider for Qwen3-Embedding-0.6B model.
    
    This class automatically selects the best available method:
    1. HuggingFace transformers (if available)
    2. Ollama with qwen3-embedding model (if configured)
    3. Fallback to generic Ollama model with warning
    """
    
    def __init__(
        self,
        prefer_huggingface: bool = True,
        device: Optional[str] = None,
        batch_size: int = 32
    ):
        """
        Initialize Qwen3 Embedding provider.
        
        Args:
            prefer_huggingface: Prefer HuggingFace over Ollama if both available
            device: Device for HuggingFace model (cuda/cpu/mps)
            batch_size: Batch size for processing
        """
        self.logger = logging.getLogger(__name__)
        self.embedder = None
        self.embedding_dim = 1536  # Qwen3-Embedding-0.6B dimension
        
        # Try HuggingFace first if preferred
        if prefer_huggingface and HUGGINGFACE_AVAILABLE:
            try:
                self.logger.info("Loading Qwen3-Embedding-0.6B from HuggingFace...")
                self.embedder = Qwen3Embedder(
                    model_name="Qwen/Qwen3-Embedding-0.6B",
                    device=device,
                    batch_size=batch_size
                )
                self.embedding_dim = self.embedder.get_embedding_dimension()
                self.logger.info(f"✓ Using HuggingFace Qwen3-Embedding-0.6B (dim={self.embedding_dim})")
                return
            except Exception as e:
                self.logger.warning(f"Failed to load HuggingFace model: {e}")
        
        # Try Ollama with custom qwen3-embedding model
        try:
            # Check if qwen3-embedding model exists in Ollama
            ollama_embedder = LocalEmbedder(model='qwen3-embedding')
            if ollama_embedder.validate_configuration():
                self.embedder = ollama_embedder
                self.embedding_dim = ollama_embedder.get_embedding_dimension()
                self.logger.info(f"✓ Using Ollama qwen3-embedding model (dim={self.embedding_dim})")
                return
        except Exception as e:
            self.logger.warning(f"Qwen3-embedding not found in Ollama: {e}")
        
        # Last resort: Use generic Qwen model with warning
        self.logger.warning(
            "⚠️  Qwen3-Embedding-0.6B not available!\n"
            "    Please either:\n"
            "    1. Install transformers: pip install transformers torch\n"
            "    2. Create Ollama model: See setup_qwen3_ollama.sh\n"
            "    Falling back to generic Qwen model (not optimal for embeddings)"
        )
        self.embedder = LocalEmbedder(model='qwen2.5:0.5b')
        self.embedding_dim = self.embedder.get_embedding_dimension()
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings using the best available method.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if self.embedder is None:
            raise RuntimeError("No embedding model available")
        
        return self.embedder.create_embeddings(texts)
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dim
    
    def validate_configuration(self) -> bool:
        """Validate the embedder configuration."""
        if self.embedder is None:
            return False
        return self.embedder.validate_configuration()
    
    def get_model_info(self) -> dict:
        """Get information about the current model."""
        if isinstance(self.embedder, LocalEmbedder):
            return {
                "type": "ollama",
                "model": self.embedder.model,
                "dimension": self.embedding_dim
            }
        elif HUGGINGFACE_AVAILABLE and hasattr(self.embedder, 'model_name'):
            return {
                "type": "huggingface",
                "model": self.embedder.model_name,
                "dimension": self.embedding_dim,
                "device": self.embedder.device
            }
        else:
            return {
                "type": "unknown",
                "dimension": self.embedding_dim
            }