#!/usr/bin/env python3
"""
OpenAI embedding provider implementation.
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import aiohttp
import json

from .base import BaseEmbeddingProvider, EmbeddingModelProfile, EmbeddingResult

logger = logging.getLogger(__name__)

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider."""
    
    MODELS = {
        "text-embedding-3-small": EmbeddingModelProfile(dimension=1536, score_threshold=0.4),
        "text-embedding-3-large": EmbeddingModelProfile(dimension=3072, score_threshold=0.4),
        "text-embedding-ada-002": EmbeddingModelProfile(dimension=1536, score_threshold=0.4),
    }
    
    DEFAULT_MODEL = "text-embedding-3-small"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        """Initialize OpenAI provider."""
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"), **kwargs)
        self.base_url = base_url or "https://api.openai.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self) -> bool:
        """Initialize the provider."""
        if not self.api_key:
            logger.error("OpenAI API key not provided")
            return False
        
        # Create session
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        # Validate connection
        valid, error = await self.validate_connection()
        if not valid:
            logger.error(f"Failed to validate OpenAI connection: {error}")
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
        
        # OpenAI has a limit on batch size, so we may need to chunk
        max_batch = 100
        all_embeddings = []
        total_usage = {"prompt_tokens": 0, "total_tokens": 0}
        
        for i in range(0, len(texts), max_batch):
            batch = texts[i:i + max_batch]
            
            payload = {
                "model": model,
                "input": batch,
                "encoding_format": "float"
            }
            
            try:
                async with self.session.post(
                    f"{self.base_url}/embeddings",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"OpenAI API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    
                    # Extract embeddings
                    batch_embeddings = [item["embedding"] for item in data["data"]]
                    all_embeddings.extend(batch_embeddings)
                    
                    # Accumulate usage
                    if "usage" in data:
                        total_usage["prompt_tokens"] += data["usage"].get("prompt_tokens", 0)
                        total_usage["total_tokens"] += data["usage"].get("total_tokens", 0)
                    
            except Exception as e:
                logger.error(f"Error embedding texts with OpenAI: {e}")
                raise
        
        return EmbeddingResult(
            embeddings=all_embeddings,
            model=model,
            usage=total_usage
        )
    
    async def embed_query(
        self, 
        query: str, 
        model: Optional[str] = None
    ) -> List[float]:
        """Embed a single query."""
        result = await self.embed_texts([query], model)
        return result.embeddings[0]
    
    def get_model_profile(self, model: str) -> EmbeddingModelProfile:
        """Get model profile."""
        return self.MODELS.get(model, self.MODELS[self.DEFAULT_MODEL])
    
    def get_default_model(self) -> str:
        """Get default model."""
        return self.DEFAULT_MODEL
    
    async def validate_connection(self) -> Tuple[bool, Optional[str]]:
        """Validate connection to OpenAI."""
        try:
            # Try a simple embedding request
            result = await self.embed_texts(["test"], self.DEFAULT_MODEL)
            return True, None
        except Exception as e:
            return False, str(e)
    
    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None
        self._initialized = False