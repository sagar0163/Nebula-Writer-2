"""
Nebula-Writer Configuration
Environment and settings management
"""
import os
from pathlib import Path
from typing import Optional
import json


class Config:
    """Nebula-Writer configuration"""
    
    DEFAULT_CONFIG = {
        "gemini_api_key": None,
        "database_path": "data/codex.db",
        "memory_path": "data/memory",
        "default_word_count": 500,
        "default_style": "literary",
    }
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = Path.home() / ".nebula-writer"
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.config = self._load()
    
    def _load(self) -> dict:
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return {**self.DEFAULT_CONFIG, **json.load(f)}
        return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        """Save configuration"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default=None):
        """Get config value"""
        # Check environment variable first
        env_key = f"NEBULA_{key.upper()}"
        if env_key in os.environ:
            return os.environ[env_key]
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set config value"""
        self.config[key] = value
        self.save()
    
    @property
    def gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key"""
        return self.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
    
    @gemini_api_key.setter
    def gemini_api_key(self, value: str):
        self.set("gemini_api_key", value)


# Global config instance
config = Config()


def get_config() -> Config:
    """Get global config"""
    return config
