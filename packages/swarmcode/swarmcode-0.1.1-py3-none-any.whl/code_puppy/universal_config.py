"""
Universal configuration management for SwarmCode.
Handles cross-platform config storage and environment variables.
"""

import os
import json
import platform
from pathlib import Path
from typing import Dict, Any, Optional

class UniversalConfig:
    """Cross-platform configuration manager."""
    
    @staticmethod
    def get_config_dir() -> Path:
        """Get the appropriate config directory for the current OS."""
        system = platform.system()
        
        if system == "Windows":
            # Use APPDATA on Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / 'SwarmCode'
        elif system == "Darwin":
            # macOS uses ~/Library/Application Support
            config_dir = Path.home() / 'Library' / 'Application Support' / 'SwarmCode'
        else:
            # Linux and others use XDG_CONFIG_HOME or ~/.config
            xdg_config = os.environ.get('XDG_CONFIG_HOME')
            if xdg_config:
                config_dir = Path(xdg_config) / 'swarmcode'
            else:
                config_dir = Path.home() / '.config' / 'swarmcode'
        
        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    @staticmethod
    def get_cache_dir() -> Path:
        """Get the appropriate cache directory for the current OS."""
        system = platform.system()
        
        if system == "Windows":
            cache_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'SwarmCode' / 'Cache'
        elif system == "Darwin":
            cache_dir = Path.home() / 'Library' / 'Caches' / 'SwarmCode'
        else:
            # Linux uses XDG_CACHE_HOME or ~/.cache
            xdg_cache = os.environ.get('XDG_CACHE_HOME')
            if xdg_cache:
                cache_dir = Path(xdg_cache) / 'swarmcode'
            else:
                cache_dir = Path.home() / '.cache' / 'swarmcode'
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    @staticmethod
    def get_data_dir() -> Path:
        """Get the appropriate data directory for the current OS."""
        system = platform.system()
        
        if system == "Windows":
            data_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'SwarmCode' / 'Data'
        elif system == "Darwin":
            data_dir = Path.home() / 'Library' / 'SwarmCode'
        else:
            # Linux uses XDG_DATA_HOME or ~/.local/share
            xdg_data = os.environ.get('XDG_DATA_HOME')
            if xdg_data:
                data_dir = Path(xdg_data) / 'swarmcode'
            else:
                data_dir = Path.home() / '.local' / 'share' / 'swarmcode'
        
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load configuration from the appropriate location."""
        config_file = cls.get_config_dir() / 'config.json'
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Check legacy locations for backwards compatibility
        legacy_locations = [
            Path.home() / '.code_puppy' / 'system_config.json',
            Path.cwd() / 'code_puppy_config.json',
        ]
        
        for legacy_path in legacy_locations:
            if legacy_path.exists():
                with open(legacy_path, 'r') as f:
                    config = json.load(f)
                    # Save to new location
                    cls.save_config(config)
                    return config
        
        return {}
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]) -> None:
        """Save configuration to the appropriate location."""
        config_file = cls.get_config_dir() / 'config.json'
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def get_env_value(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with fallback to config file."""
        # First check actual environment
        value = os.environ.get(key)
        if value:
            return value
        
        # Then check config file
        config = cls.load_config()
        env_overrides = config.get('environment_overrides', {})
        
        return env_overrides.get(key, default)
    
    @classmethod
    def set_env_value(cls, key: str, value: str) -> None:
        """Set environment variable in config file."""
        config = cls.load_config()
        
        if 'environment_overrides' not in config:
            config['environment_overrides'] = {}
        
        config['environment_overrides'][key] = value
        cls.save_config(config)
    
    @classmethod
    def ensure_api_key(cls) -> str:
        """Ensure we have a Cerebras API key configured."""
        api_key = cls.get_env_value('CEREBRAS_API_KEY')
        
        if not api_key:
            print("🔑 Cerebras API key not found.")
            print("Get your API key from: https://cerebras.ai")
            api_key = input("Enter your Cerebras API key: ").strip()
            
            if api_key:
                cls.set_env_value('CEREBRAS_API_KEY', api_key)
                print("✅ API key saved!")
            else:
                raise ValueError("API key is required to use SwarmCode")
        
        return api_key
    
    @classmethod
    def get_models_json_path(cls) -> Path:
        """Get the path to the models.json file."""
        # First check if there's a custom path set
        custom_path = cls.get_env_value('MODELS_JSON_PATH')
        if custom_path:
            return Path(custom_path)
        
        # Otherwise use the data directory
        models_file = cls.get_data_dir() / 'cerebras_models.json'
        
        # If it doesn't exist, create a default one
        if not models_file.exists():
            default_models = {
                "Cerebras-Qwen3-Coder-480b": {
                    "type": "custom_openai",
                    "name": "qwen-3-coder-480b",
                    "max_requests_per_minute": 100,
                    "max_retries": 3,
                    "retry_base_delay": 10,
                    "custom_endpoint": {
                        "url": "https://api.cerebras.ai/v1",
                        "api_key": "$CEREBRAS_API_KEY"
                    }
                },
                "Cerebras-Llama-3.3-70b": {
                    "type": "custom_openai",
                    "name": "llama-3.3-70b",
                    "max_requests_per_minute": 100,
                    "max_retries": 3,
                    "retry_base_delay": 10,
                    "custom_endpoint": {
                        "url": "https://api.cerebras.ai/v1",
                        "api_key": "$CEREBRAS_API_KEY"
                    }
                }
            }
            
            with open(models_file, 'w') as f:
                json.dump(default_models, f, indent=2)
        
        return models_file