#!/usr/bin/env python3
"""
Ollama embedding provider implementation.
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import aiohttp
import json

from .base import BaseEmbeddingProvider, EmbeddingModelProfile, EmbeddingResult

logger = logging.getLogger(__name__)

class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    """Ollama embedding provider for local models."""
    
    MODELS = {
        "nomic-embed-text": EmbeddingModelProfile(dimension=768, score_threshold=0.4),
        "nomic-embed-code": EmbeddingModelProfile(
            dimension=3584, 
            score_threshold=0.15,
            query_prefix="Represent this query for searching relevant code: "
        ),
        "mxbai-embed-large": EmbeddingModelProfile(dimension=1024, score_threshold=0.4),
        "all-minilm": EmbeddingModelProfile(dimension=384, score_threshold=0.4),
        "bge-m3": EmbeddingModelProfile(dimension=1024, score_threshold=0.4),
        "snowflake-arctic-embed": EmbeddingModelProfile(dimension=1024, score_threshold=0.4),
    }
    
    DEFAULT_MODEL = "nomic-embed-text"
    
    def __init__(self, base_url: Optional[str] = None, **kwargs):
        """Initialize Ollama provider."""
        super().__init__(api_key=None, **kwargs)
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self) -> bool:
        """Initialize the provider."""
        # Create session
        self.session = aiohttp.ClientSession()
        
        # Check if Ollama is running
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status != 200:
                    logger.error(f"Ollama not accessible at {self.base_url}")
                    await self.close()
                    return False
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            await self.close()
            return False
        
        self._initialized = True
        return True
    
    async def embed_texts(
        self, 
        texts: List[str], 
        model: Optional[str] = None
    ) -> EmbeddingResult:
        """Embed multiple texts."""
        if not self._initialized:
            raise RuntimeError("Provider not initialized")
        
        model = model or self.DEFAULT_MODEL
        profile = self.get_model_profile(model)
        
        all_embeddings = []
        
        # Ollama doesn't batch, so we process one at a time
        for text in texts:
            # Apply query prefix if needed
            if profile.query_prefix:
                text = profile.query_prefix + text
            
            payload = {
                "model": model,
                "prompt": text
            }
            
            try:
                async with self.session.post(
                    f"{self.base_url}/api/embeddings",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    all_embeddings.append(data["embedding"])
                    
            except Exception as e:
                logger.error(f"Error embedding text with Ollama: {e}")
                raise
        
        return EmbeddingResult(
            embeddings=all_embeddings,
            model=model,
            usage=None  # Ollama doesn't provide usage stats
        )
    
    async def embed_query(
        self, 
        query: str, 
        model: Optional[str] = None
    ) -> List[float]:
        """Embed a single query with optional prefix."""
        model = model or self.DEFAULT_MODEL
        profile = self.get_model_profile(model)
        
        # Apply query prefix for queries
        if profile.query_prefix:
            query = profile.query_prefix + query
        
        result = await self.embed_texts([query], model)
        return result.embeddings[0]
    
    def get_model_profile(self, model: str) -> EmbeddingModelProfile:
        """Get model profile."""
        return self.MODELS.get(model, self.MODELS[self.DEFAULT_MODEL])
    
    def get_default_model(self) -> str:
        """Get default model."""
        return self.DEFAULT_MODEL
    
    async def validate_connection(self) -> Tuple[bool, Optional[str]]:
        """Validate connection to Ollama."""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if our default model is available
                    available_models = [m["name"] for m in data.get("models", [])]
                    if self.DEFAULT_MODEL in available_models:
                        return True, None
                    else:
                        return False, f"Model {self.DEFAULT_MODEL} not found in Ollama"
                else:
                    return False, f"Ollama API returned status {response.status}"
        except Exception as e:
            return False, str(e)
    
    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None
        self._initialized = False