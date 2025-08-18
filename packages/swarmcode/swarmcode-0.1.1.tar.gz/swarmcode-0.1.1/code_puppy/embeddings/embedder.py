"""
Local embedder implementation using Ollama with Qwen2.5 model.

This module provides embeddings generation using the smallest Qwen model
for efficient local processing.
"""

import json
import logging
import time
from typing import List, Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class LocalEmbedder:
    """
    Local embedder using Ollama API with Qwen 2.5 0.5B model.
    
    This uses the smallest available Qwen model (0.5B parameters)
    for efficient unified embeddings suitable for both codebase indexing and chat messages.
    """
    
    def __init__(
        self,
        model: str = 'qwen2.5:0.5b',
        base_url: str = 'http://localhost:11434',
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the local embedder.
        
        Args:
            model: Ollama model name for embeddings
            base_url: Ollama API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        
        # Set up session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Cache for model info
        self._embedding_dimension = None
    
    def create_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:
        """
        Create embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process in parallel
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = []
        total = len(texts)
        
        # Process in batches
        for i in range(0, total, batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self._process_batch(batch)
            embeddings.extend(batch_embeddings)
            
            # Log progress
            processed = min(i + batch_size, total)
            self.logger.debug(f"Processed {processed}/{total} embeddings")
        
        return embeddings
    
    def _process_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Process a batch of texts to generate embeddings.
        
        Args:
            texts: Batch of texts to embed
            
        Returns:
            List of embedding vectors for the batch
        """
        embeddings = []
        
        for text in texts:
            try:
                # Ollama embedding endpoint
                url = f"{self.base_url}/api/embeddings"
                
                # Prepare request
                payload = {
                    "model": self.model,
                    "prompt": text
                }
                
                # Make request with retries
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    embedding = data.get('embedding', [])
                    embeddings.append(embedding)
                    
                    # Cache embedding dimension
                    if self._embedding_dimension is None and embedding:
                        self._embedding_dimension = len(embedding)
                else:
                    self.logger.error(f"Embedding request failed: {response.status_code}")
                    # Return zero vector on failure
                    embeddings.append(self._get_zero_vector())
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error during embedding: {e}")
                embeddings.append(self._get_zero_vector())
            except Exception as e:
                self.logger.error(f"Unexpected error during embedding: {e}")
                embeddings.append(self._get_zero_vector())
        
        return embeddings
    
    def _get_zero_vector(self) -> List[float]:
        """Get a zero vector of the appropriate dimension."""
        dim = self.get_embedding_dimension()
        return [0.0] * dim
    
    def validate_configuration(self) -> bool:
        """
        Validate that Ollama is running and the model is available.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Check if Ollama is running
            health_url = f"{self.base_url}/api/tags"
            response = self.session.get(health_url, timeout=5)
            
            if response.status_code != 200:
                self.logger.error(f"Ollama not responding at {self.base_url}")
                return False
            
            # Check if model is available
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            
            # Check for exact match or partial match
            model_found = any(
                self.model in name or name in self.model 
                for name in model_names
            )
            
            if not model_found:
                self.logger.error(f"Model {self.model} not found. Available: {model_names}")
                return False
            
            # Try a test embedding
            test_text = "test"
            test_embedding = self._process_batch([test_text])
            
            if not test_embedding or not test_embedding[0]:
                self.logger.error("Test embedding failed")
                return False
            
            self.logger.info(f"Embedder validated: {self.model} at {self.base_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return False
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension (defaults to 896 for Qwen2.5 0.5B)
        """
        if self._embedding_dimension is not None:
            return self._embedding_dimension
        
        # Try to get dimension by creating a test embedding
        try:
            test_embedding = self._process_batch(["test"])
            if test_embedding and test_embedding[0]:
                self._embedding_dimension = len(test_embedding[0])
                return self._embedding_dimension
        except Exception as e:
            self.logger.warning(f"Could not determine embedding dimension: {e}")
        
        # Default for Qwen 2.5 0.5B
        # Note: The actual dimension will be determined on first use
        # Qwen models typically output 896-1536 dimensions depending on configuration
        return 896  # Conservative estimate, will be updated on first use
    
    def pull_model(self) -> bool:
        """
        Pull the model from Ollama if not already available.
        
        Returns:
            True if model is available or successfully pulled
        """
        try:
            # Check if model exists
            tags_url = f"{self.base_url}/api/tags"
            response = self.session.get(tags_url, timeout=5)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                
                if any(self.model in name for name in model_names):
                    self.logger.info(f"Model {self.model} already available")
                    return True
            
            # Pull the model
            self.logger.info(f"Pulling model {self.model}...")
            pull_url = f"{self.base_url}/api/pull"
            payload = {"name": self.model}
            
            # This can take a while for large models
            response = self.session.post(
                pull_url,
                json=payload,
                timeout=600,  # 10 minutes timeout for pulling
                stream=True
            )
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        status = data.get('status', '')
                        if 'error' in data:
                            self.logger.error(f"Error pulling model: {data['error']}")
                            return False
                        elif status:
                            self.logger.debug(f"Pull status: {status}")
                    except json.JSONDecodeError:
                        pass
            
            self.logger.info(f"Successfully pulled model {self.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pull model: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        try:
            show_url = f"{self.base_url}/api/show"
            payload = {"name": self.model}
            
            response = self.session.post(show_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get model info: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}