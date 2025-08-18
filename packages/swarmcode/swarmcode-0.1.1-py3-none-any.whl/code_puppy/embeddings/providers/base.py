#!/usr/bin/env python3
"""
Base embedding provider interface - RooCode style architecture.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingModelProfile:
    """Profile for an embedding model."""
    dimension: int
    score_threshold: float = 0.4
    query_prefix: Optional[str] = None
    context_window: int = 8192
    max_batch_size: int = 100

@dataclass
class EmbeddingResult:
    """Result from embedding operation."""
    embeddings: List[List[float]]
    model: str
    usage: Optional[Dict[str, int]] = None

class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize the provider."""
        self.api_key = api_key
        self.config = kwargs
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider and validate configuration."""
        pass
    
    @abstractmethod
    async def embed_texts(
        self, 
        texts: List[str], 
        model: Optional[str] = None
    ) -> EmbeddingResult:
        """Embed a list of texts."""
        pass
    
    @abstractmethod
    async def embed_query(
        self, 
        query: str, 
        model: Optional[str] = None
    ) -> List[float]:
        """Embed a single query with optional query prefix."""
        pass
    
    @abstractmethod
    def get_model_profile(self, model: str) -> EmbeddingModelProfile:
        """Get the profile for a specific model."""
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """Get the default model for this provider."""
        pass
    
    @abstractmethod
    async def validate_connection(self) -> Tuple[bool, Optional[str]]:
        """Validate the connection to the provider."""
        pass
    
    async def close(self):
        """Clean up resources."""
        pass
    
    def __str__(self) -> str:
        """String representation of the provider."""
        return f"{self.__class__.__name__}()"