"""
Embedding providers for Code Puppy.
"""

from .base import BaseEmbeddingProvider, EmbeddingModelProfile, EmbeddingResult
from .openai_provider import OpenAIEmbeddingProvider
from .ollama_provider import OllamaEmbeddingProvider
from .openai_compatible import OpenAICompatibleProvider

__all__ = [
    'BaseEmbeddingProvider',
    'EmbeddingModelProfile', 
    'EmbeddingResult',
    'OpenAIEmbeddingProvider',
    'OllamaEmbeddingProvider',
    'OpenAICompatibleProvider'
]