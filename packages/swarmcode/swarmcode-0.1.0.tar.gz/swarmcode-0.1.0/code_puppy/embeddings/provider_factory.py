#!/usr/bin/env python3
"""
Factory for creating embedding providers based on configuration.
RooCode-style architecture for flexible embedding model support.
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from enum import Enum

from .providers.base import BaseEmbeddingProvider, EmbeddingModelProfile
from .providers.openai_provider import OpenAIEmbeddingProvider
from .providers.ollama_provider import OllamaEmbeddingProvider
from .providers.openai_compatible import OpenAICompatibleProvider

logger = logging.getLogger(__name__)

class EmbeddingProviderType(Enum):
    """Supported embedding provider types."""
    OPENAI = "openai"
    OLLAMA = "ollama"
    OPENAI_COMPATIBLE = "openai-compatible"
    GEMINI = "gemini"
    MISTRAL = "mistral"
    CEREBRAS = "cerebras"
    CUSTOM = "custom"

class EmbeddingProviderFactory:
    """Factory for creating embedding providers."""
    
    @staticmethod
    def create_provider(
        provider_type: Union[str, EmbeddingProviderType],
        config: Optional[Dict[str, Any]] = None
    ) -> BaseEmbeddingProvider:
        """
        Create an embedding provider based on type and configuration.
        
        Args:
            provider_type: Type of provider to create
            config: Configuration for the provider
        
        Returns:
            Configured embedding provider instance
        """
        # Convert string to enum if needed
        if isinstance(provider_type, str):
            try:
                provider_type = EmbeddingProviderType(provider_type.lower())
            except ValueError:
                # Default to OpenAI-compatible for unknown types
                logger.warning(f"Unknown provider type: {provider_type}, using OpenAI-compatible")
                provider_type = EmbeddingProviderType.OPENAI_COMPATIBLE
        
        config = config or {}
        
        # Create provider based on type
        if provider_type == EmbeddingProviderType.OPENAI:
            return OpenAIEmbeddingProvider(
                api_key=config.get("api_key") or os.getenv("OPENAI_API_KEY"),
                base_url=config.get("base_url")
            )
        
        elif provider_type == EmbeddingProviderType.OLLAMA:
            return OllamaEmbeddingProvider(
                base_url=config.get("base_url") or os.getenv("OLLAMA_BASE_URL")
            )
        
        elif provider_type == EmbeddingProviderType.OPENAI_COMPATIBLE:
            return OpenAICompatibleProvider(
                api_key=config.get("api_key"),
                base_url=config.get("base_url", "http://localhost:8001"),
                model_profiles=config.get("model_profiles"),
                default_model=config.get("default_model", "default")
            )
        
        elif provider_type == EmbeddingProviderType.CEREBRAS:
            # Cerebras uses OpenAI-compatible format
            return OpenAICompatibleProvider(
                api_key=config.get("api_key") or os.getenv("CEREBRAS_API_KEY"),
                base_url="https://api.cerebras.ai/v1",
                model_profiles={
                    "cerebras-embed": EmbeddingModelProfile(
                        dimension=768,
                        score_threshold=0.4
                    )
                },
                default_model="cerebras-embed"
            )
        
        elif provider_type == EmbeddingProviderType.GEMINI:
            # TODO: Implement Gemini provider
            raise NotImplementedError("Gemini provider not yet implemented")
        
        elif provider_type == EmbeddingProviderType.MISTRAL:
            # Mistral uses OpenAI-compatible format
            return OpenAICompatibleProvider(
                api_key=config.get("api_key") or os.getenv("MISTRAL_API_KEY"),
                base_url="https://api.mistral.ai/v1",
                model_profiles={
                    "codestral-embed-2505": EmbeddingModelProfile(
                        dimension=1536,
                        score_threshold=0.4
                    )
                },
                default_model="codestral-embed-2505"
            )
        
        else:
            # Default to OpenAI-compatible
            return OpenAICompatibleProvider(**config)
    
    @staticmethod
    def create_from_config(config_path: Optional[str] = None) -> BaseEmbeddingProvider:
        """
        Create provider from configuration file or environment.
        
        Args:
            config_path: Path to configuration file (optional)
        
        Returns:
            Configured embedding provider
        """
        import json
        
        config = {}
        
        # Load from file if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        
        # Override with environment variables
        provider_type = os.getenv("EMBEDDING_PROVIDER", config.get("provider", "openai"))
        
        # Build config from environment
        env_config = {
            "api_key": os.getenv("EMBEDDING_API_KEY"),
            "base_url": os.getenv("EMBEDDING_BASE_URL"),
            "default_model": os.getenv("EMBEDDING_MODEL")
        }
        
        # Merge configs (env overrides file)
        final_config = {**config, **{k: v for k, v in env_config.items() if v}}
        
        return EmbeddingProviderFactory.create_provider(provider_type, final_config)
    
    @staticmethod
    def get_available_providers() -> Dict[str, Dict[str, Any]]:
        """
        Get information about available providers.
        
        Returns:
            Dictionary of provider information
        """
        return {
            "openai": {
                "name": "OpenAI",
                "models": ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
                "requires_api_key": True,
                "default_model": "text-embedding-3-small"
            },
            "ollama": {
                "name": "Ollama (Local)",
                "models": ["nomic-embed-text", "nomic-embed-code", "mxbai-embed-large", "all-minilm"],
                "requires_api_key": False,
                "default_model": "nomic-embed-text"
            },
            "openai-compatible": {
                "name": "OpenAI Compatible",
                "models": ["custom"],
                "requires_api_key": False,
                "default_model": "default"
            },
            "cerebras": {
                "name": "Cerebras",
                "models": ["cerebras-embed"],
                "requires_api_key": True,
                "default_model": "cerebras-embed"
            },
            "mistral": {
                "name": "Mistral AI",
                "models": ["codestral-embed-2505"],
                "requires_api_key": True,
                "default_model": "codestral-embed-2505"
            }
        }