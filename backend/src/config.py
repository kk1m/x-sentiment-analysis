"""
Configuration Loader
Centralized configuration management for the application
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any, List


class Config:
    """Centralized configuration loader"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
    
    @property
    def sentiment_algorithm(self) -> str:
        """Get sentiment analysis algorithm"""
        return self._config.get('sentiment', {}).get('algorithm', 'keyword')
    
    @property
    def sentiment_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI sentiment config"""
        return self._config.get('sentiment', {}).get('openai', {})
    
    @property
    def sentiment_keyword_config(self) -> Dict[str, List[str]]:
        """Get keyword sentiment config"""
        return self._config.get('sentiment', {}).get('keyword', {})
    
    @property
    def sentiment_vader_config(self) -> Dict[str, float]:
        """Get VADER sentiment config"""
        return self._config.get('sentiment', {}).get('vader', {})
    
    @property
    def bot_detection_algorithm(self) -> str:
        """Get bot detection algorithm"""
        return self._config.get('bot_detection', {}).get('algorithm', 'heuristic')
    
    @property
    def bot_detection_heuristic_config(self) -> Dict[str, Any]:
        """Get heuristic bot detection config"""
        return self._config.get('bot_detection', {}).get('heuristic', {})
    
    @property
    def bot_detection_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI bot detection config"""
        return self._config.get('bot_detection', {}).get('openai', {})
    
    @property
    def collection_config(self) -> Dict[str, Any]:
        """Get data collection config"""
        return self._config.get('collection', {})
    
    @property
    def dashboard_config(self) -> Dict[str, Any]:
        """Get dashboard config"""
        return self._config.get('dashboard', {})
    
    @property
    def api_config(self) -> Dict[str, Any]:
        """Get API config"""
        return self._config.get('api', {})
    
    def reload(self):
        """Reload configuration from file"""
        self._load_config()


# Singleton instance
config = Config()
