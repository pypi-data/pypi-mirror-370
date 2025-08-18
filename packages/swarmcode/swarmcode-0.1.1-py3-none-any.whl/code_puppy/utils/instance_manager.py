#!/usr/bin/env python3
"""
Instance Manager for Code Puppy
Ensures each Code Puppy instance has unique resources (ports, configs, etc.)
"""

import os
import uuid
import json
import socket
import atexit
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class InstanceManager:
    """Manages unique instance resources for Code Puppy."""
    
    _instance: Optional['InstanceManager'] = None
    
    def __init__(self):
        """Initialize instance manager."""
        # Generate unique instance ID
        self.instance_id = str(uuid.uuid4())[:8]
        
        # Create instance-specific directory
        self.instance_dir = Path(tempfile.gettempdir()) / f"code_puppy_{self.instance_id}"
        self.instance_dir.mkdir(parents=True, exist_ok=True)
        
        # Instance config file
        self.config_file = self.instance_dir / "instance.json"
        
        # Store allocated resources
        self.resources: Dict[str, Any] = {
            "instance_id": self.instance_id,
            "pid": os.getpid(),
            "ports": {},
            "working_dir": os.getcwd()
        }
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
        
        # Save initial config
        self._save_config()
        
        logger.info(f"Created instance {self.instance_id} with dir: {self.instance_dir}")
    
    @classmethod
    def get_instance(cls) -> 'InstanceManager':
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def find_free_port(self, start_port: int = 8000, max_port: int = 9000) -> int:
        """Find an available port in the given range."""
        for port in range(start_port, max_port):
            try:
                # Try to bind to the port
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                # Port is in use, try next one
                continue
        raise RuntimeError(f"No free ports found between {start_port} and {max_port}")
    
    def allocate_port(self, service_name: str, preferred_port: Optional[int] = None) -> int:
        """
        Allocate a port for a service.
        
        Args:
            service_name: Name of the service (e.g., 'embeddings', 'qdrant')
            preferred_port: Preferred port to try first
            
        Returns:
            Allocated port number
        """
        # Check if we already allocated a port for this service
        if service_name in self.resources["ports"]:
            return self.resources["ports"][service_name]
        
        # Try preferred port first if provided
        if preferred_port:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', preferred_port))
                    port = preferred_port
            except OSError:
                # Preferred port is in use, find another
                port = self.find_free_port(preferred_port + 1)
        else:
            # Find any free port
            port = self.find_free_port()
        
        # Store allocated port
        self.resources["ports"][service_name] = port
        self._save_config()
        
        logger.info(f"Allocated port {port} for service '{service_name}'")
        return port
    
    def get_port(self, service_name: str) -> Optional[int]:
        """Get allocated port for a service."""
        return self.resources["ports"].get(service_name)
    
    def get_instance_config_dir(self) -> Path:
        """Get instance-specific config directory."""
        config_dir = self.instance_dir / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def get_instance_cache_dir(self) -> Path:
        """Get instance-specific cache directory."""
        cache_dir = self.instance_dir / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def get_rag_config_path(self) -> Path:
        """Get instance-specific RAG config path."""
        return self.get_instance_config_dir() / "rag_config.json"
    
    def get_embeddings_cache_dir(self) -> Path:
        """Get instance-specific embeddings cache directory."""
        cache_dir = self.get_instance_cache_dir() / "embeddings"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def _save_config(self):
        """Save instance configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.resources, f, indent=2)
    
    def cleanup(self):
        """Clean up instance resources on exit."""
        logger.info(f"Cleaning up instance {self.instance_id}")
        
        # Clean up temporary directory
        if self.instance_dir.exists():
            import shutil
            try:
                shutil.rmtree(self.instance_dir)
                logger.debug(f"Removed instance directory: {self.instance_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up instance directory: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get instance information."""
        return {
            "instance_id": self.instance_id,
            "pid": self.resources["pid"],
            "working_dir": self.resources["working_dir"],
            "instance_dir": str(self.instance_dir),
            "ports": self.resources["ports"],
            "config_dir": str(self.get_instance_config_dir()),
            "cache_dir": str(self.get_instance_cache_dir())
        }

# Convenience functions
def get_instance_manager() -> InstanceManager:
    """Get the instance manager."""
    return InstanceManager.get_instance()

def get_instance_id() -> str:
    """Get current instance ID."""
    return get_instance_manager().instance_id

def allocate_port(service_name: str, preferred_port: Optional[int] = None) -> int:
    """Allocate a port for a service."""
    return get_instance_manager().allocate_port(service_name, preferred_port)

def get_port(service_name: str) -> Optional[int]:
    """Get allocated port for a service."""
    return get_instance_manager().get_port(service_name)

def get_rag_config_path() -> Path:
    """Get instance-specific RAG config path."""
    return get_instance_manager().get_rag_config_path()

def get_embeddings_cache_dir() -> Path:
    """Get instance-specific embeddings cache directory."""
    return get_instance_manager().get_embeddings_cache_dir()