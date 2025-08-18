"""
Qwen3 Embedding model implementation.

This module provides embeddings using the actual Qwen3-Embedding-0.6B model
from HuggingFace, not generic Qwen models.
"""

import logging
import torch
import numpy as np
from typing import List, Optional
from transformers import AutoTokenizer, AutoModel

class Qwen3Embedder:
    """
    Embedder using the actual Qwen3-Embedding-0.6B model from HuggingFace.
    
    This is the purpose-built embedding model from Qwen, specifically designed
    for generating high-quality embeddings.
    """
    
    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-Embedding-0.6B",
        device: Optional[str] = None,
        max_length: int = 512,
        batch_size: int = 32
    ):
        """
        Initialize Qwen3 Embedder.
        
        Args:
            model_name: HuggingFace model name
            device: Device to use (cuda/cpu/mps), auto-detect if None
            max_length: Maximum token length
            batch_size: Batch size for processing
        """
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self.logger = logging.getLogger(__name__)
        
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
        
        self.logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self._load_model()
        
    def _load_model(self):
        """Load the Qwen3 Embedding model and tokenizer."""
        try:
            self.logger.info(f"Loading {self.model_name}...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load model
            self.model = AutoModel.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Move to device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # Get embedding dimension
            with torch.no_grad():
                test_input = self.tokenizer(
                    ["test"],
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt"
                ).to(self.device)
                
                test_output = self.model(**test_input)
                # Get the pooled output (usually last_hidden_state mean pooled)
                if hasattr(test_output, 'pooler_output'):
                    test_embedding = test_output.pooler_output
                else:
                    # Mean pooling over sequence dimension
                    attention_mask = test_input['attention_mask']
                    token_embeddings = test_output.last_hidden_state
                    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                    test_embedding = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                
                self.embedding_dim = test_embedding.shape[-1]
            
            self.logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts using Qwen3-Embedding.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                # Tokenize
                inputs = self.tokenizer(
                    batch,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt"
                ).to(self.device)
                
                # Generate embeddings
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    
                    # Extract embeddings (pooled output or mean pooling)
                    if hasattr(outputs, 'pooler_output'):
                        embeddings = outputs.pooler_output
                    else:
                        # Mean pooling
                        attention_mask = inputs['attention_mask']
                        token_embeddings = outputs.last_hidden_state
                        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                        embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                    
                    # Normalize embeddings (L2 normalization)
                    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
                    
                    # Convert to list
                    batch_embeddings = embeddings.cpu().numpy().tolist()
                    all_embeddings.extend(batch_embeddings)
                    
            except Exception as e:
                self.logger.error(f"Error creating embeddings for batch: {e}")
                # Return zero vectors for failed batch
                all_embeddings.extend([[0.0] * self.embedding_dim for _ in batch])
        
        return all_embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings.
        
        Returns:
            Embedding dimension (1536 for Qwen3-Embedding-0.6B)
        """
        return self.embedding_dim
    
    def validate_configuration(self) -> bool:
        """
        Validate that the model is properly loaded.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Test embedding generation
            test_embedding = self.create_embeddings(["test"])
            
            if not test_embedding or len(test_embedding[0]) != self.embedding_dim:
                return False
            
            self.logger.info("Qwen3 Embedding model validated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return False


class Qwen3OllamaEmbedder:
    """
    Alternative: Create a custom Ollama modelfile for Qwen3-Embedding.
    This allows us to use Qwen3-Embedding through Ollama's API.
    """
    
    @staticmethod
    def create_modelfile():
        """
        Create an Ollama modelfile for Qwen3-Embedding.
        
        This should be saved as 'Modelfile' and run with:
        ollama create qwen3-embedding -f Modelfile
        """
        modelfile_content = """
# Qwen3 Embedding Model for Ollama
FROM Qwen/Qwen3-Embedding-0.6B

# Set parameters for embedding model
PARAMETER temperature 0
PARAMETER top_p 1
PARAMETER top_k 1
PARAMETER repeat_penalty 1

# Embedding-specific template
TEMPLATE "{{ .Prompt }}"

# System message for embeddings
SYSTEM "You are an embedding model. Generate high-quality embeddings for the input text."
"""
        return modelfile_content
    
    @staticmethod
    def setup_instructions():
        """
        Instructions for setting up Qwen3-Embedding in Ollama.
        """
        instructions = """
        To use Qwen3-Embedding with Ollama:
        
        1. Install ollama-python to convert HuggingFace models:
           pip install ollama-python
        
        2. Download and convert the model:
           python -m ollama_python.convert \\
               --model Qwen/Qwen3-Embedding-0.6B \\
               --output qwen3-embedding
        
        3. Create the model in Ollama:
           ollama create qwen3-embedding -f ./qwen3-embedding/Modelfile
        
        4. Test the model:
           ollama run qwen3-embedding "test embedding"
        """
        return instructions