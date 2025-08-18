#!/usr/bin/env python3
"""
OpenAI-compatible embedding provider for custom endpoints.
Works with any API that follows OpenAI's embedding format.
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import aiohttp
import json

from .base import BaseEmbeddingProvider, EmbeddingModelProfile, EmbeddingResult

logger = logging.getLogger(__name__)

class OpenAICompatibleProvider(BaseEmbeddingProvider):
    """Provider for any OpenAI-compatible embedding API."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8001",
        model_profiles: Optional[Dict[str, EmbeddingModelProfile]] = None,
        default_model: str = "default",
        **kwargs
    ):
        """Initialize OpenAI-compatible provider."""
        super().__init__(api_key, **kwargs)
        self.base_url = base_url.rstrip('/')
        self.default_model = default_model
        
        # Allow custom model profiles
        if model_profiles:
            self.models = model_profiles
        else:
            # Default profile
            self.models = {
                "default": EmbeddingModelProfile(dimension=1024, score_threshold=0.4)
            }
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self) -> bool:
        """Initialize the provider."""
        # Don't create session here - create it on demand in the same event loop
        self._headers = {"Content-Type": "application/json"}
        
        # Add auth header if API key provided
        if self.api_key:
            self._headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Try to validate connection
        valid, error = await self.validate_connection()
        if not valid:
            logger.warning(f"Connection validation failed (may be normal for some providers): {error}")
            # Don't fail initialization - some providers don't support test embedding
        
        self._initialized = True
        return True
    
    async def _ensure_session(self):
        """Ensure we have a session for the current event loop."""
        # Get current event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return None
            
        # Check if we have a session and if it's for the current loop
        if self.session is None or self.session.closed or self.session._loop != loop:
            # Close old session if it exists
            if self.session and not self.session.closed:
                await self.session.close()
            
            # Create new session for current loop
            self.session = aiohttp.ClientSession(headers=self._headers)
        
        return self.session
    
    async def embed_texts(
        self, 
        texts: List[str], 
        model: Optional[str] = None
    ) -> EmbeddingResult:
        """Embed multiple texts."""
        if not self._initialized:
            raise RuntimeError("Provider not initialized")
        
        # Ensure we have a valid session for current event loop
        session = await self._ensure_session()
        if not session:
            raise RuntimeError("Failed to create session")
        
        model = model or self.default_model
        
        payload = {
            "model": model,
            "input": texts,
            "encoding_format": "float"
        }
        
        try:
            async with session.post(
                f"{self.base_url}/v1/embeddings",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error: {response.status} - {error_text}")
                
                data = await response.json()
                
                # Handle both OpenAI format and simplified format
                if "data" in data:
                    # OpenAI format
                    embeddings = [item["embedding"] for item in data["data"]]
                elif "embeddings" in data:
                    # Simplified format
                    embeddings = data["embeddings"]
                else:
                    raise Exception(f"Unexpected response format: {data.keys()}")
                
                usage = data.get("usage", None)
                
                return EmbeddingResult(
                    embeddings=embeddings,
                    model=model,
                    usage=usage
                )
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout embedding texts with {self.base_url}")
            raise Exception("Embedding request timed out")
        except Exception as e:
            logger.error(f"Error embedding texts: {e}")
            raise
    
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
        return self.models.get(model, list(self.models.values())[0])
    
    def get_default_model(self) -> str:
        """Get default model."""
        return self.default_model
    
    async def validate_connection(self) -> Tuple[bool, Optional[str]]:
        """Validate connection."""
        try:
            # Ensure we have a valid session
            session = await self._ensure_session()
            if not session:
                return False, "Failed to create session"
            
            # Try a health check first
            try:
                async with session.get(
                    f"{self.base_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return True, None
            except:
                pass  # Health endpoint may not exist
            
            # Try a test embedding
            result = await self.embed_texts(["test"], self.default_model)
            return True, None
        except Exception as e:
            return False, str(e)
    
    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None
        self._initialized = False
    
    @classmethod
    def for_qwen3_embedding(cls, base_url: str = "http://localhost:8001"):
        """Factory method for Qwen3-Embedding-0.6B."""
        return cls(
            base_url=base_url,
            model_profiles={
                "Qwen3-Embedding-0.6B": EmbeddingModelProfile(
                    dimension=1024, 
                    score_threshold=0.4
                )
            },
            default_model="Qwen3-Embedding-0.6B"
        )