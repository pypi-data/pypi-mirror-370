"""
Embedding configuration management for Code Puppy.

This module handles all configuration related to the embeddings system,
including toggles for codebase and chat indexing.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field

@dataclass
class EmbeddingConfig:
    """Configuration for the embedding system."""
    
    # Feature toggles
    codebase_enabled: bool = False
    chat_enabled: bool = False
    
    # Provider settings
    provider: str = 'qwen3'  # Use Qwen3-Embedding-0.6B
    model: str = 'Qwen/Qwen3-Embedding-0.6B'
    
    # Service URLs
    qdrant_url: str = 'http://localhost:6333'
    ollama_base_url: str = 'http://localhost:11434'
    
    # Storage paths
    cache_dir: str = '~/.code_puppy/embeddings'
    qdrant_storage: str = '~/.code_puppy/qdrant_storage'
    
    # Model parameters
    vector_size: int = 1536  # Qwen3-Embedding-0.6B outputs 1536 dimensions
    max_tokens_per_chunk: int = 2048
    chunk_overlap: int = 128
    batch_size: int = 32
    
    # Search parameters
    search_limit: int = 10
    score_threshold: float = 0.7
    max_context_tokens: int = 8000
    
    # Indexing parameters
    file_extensions: list = field(default_factory=lambda: [
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
        '.go', '.rs', '.swift', '.kt', '.rb', '.php', '.cs', '.scala',
        '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'
    ])
    
    ignore_patterns: list = field(default_factory=lambda: [
        '.git', '__pycache__', 'node_modules', '.venv', 'venv',
        'dist', 'build', 'target', '.pytest_cache', '.mypy_cache',
        '*.pyc', '*.pyo', '*.pyd', '.DS_Store', 'Thumbs.db'
    ])
    
    # Background indexing
    watch_enabled: bool = True
    debounce_seconds: float = 1.5
    
    # Memory management
    conversation_memory_limit: int = 1000
    memory_prune_age_days: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmbeddingConfig':
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def save(self, path: Optional[str] = None):
        """Save configuration to file."""
        if path is None:
            path = os.path.expanduser('~/.code_puppy/embedding_config.json')
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: Optional[str] = None) -> 'EmbeddingConfig':
        """Load configuration from file."""
        if path is None:
            path = os.path.expanduser('~/.code_puppy/embedding_config.json')
        
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                return cls.from_dict(data)
        return cls()

# Global configuration instance
_config: Optional[EmbeddingConfig] = None

def get_embedding_config() -> EmbeddingConfig:
    """Get the global embedding configuration."""
    global _config
    if _config is None:
        _config = EmbeddingConfig.load()
    return _config

def set_embedding_config(config: EmbeddingConfig):
    """Set the global embedding configuration."""
    global _config
    _config = config
    _config.save()

def update_embedding_config(**kwargs):
    """Update specific configuration values."""
    config = get_embedding_config()
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    config.save()
    return config

def toggle_codebase_indexing(enabled: bool) -> EmbeddingConfig:
    """Toggle codebase indexing on/off."""
    return update_embedding_config(codebase_enabled=enabled)

def toggle_chat_embeddings(enabled: bool) -> EmbeddingConfig:
    """Toggle chat message embeddings on/off."""
    return update_embedding_config(chat_enabled=enabled)