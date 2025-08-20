"""
Simple model configuration loader
"""
import json
from pathlib import Path
from typing import Dict, Optional

class ModelConfig:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Look for models.json in the current working directory
            config_path = Path("models.json")
        
        self.config_path = Path(config_path)
        self.models = {}
        self.default_retry = {}
        self.load_config()
    
    def load_config(self):
        """Load model configurations from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self.models = data.get('models', {})
                self.default_retry = data.get('default_retry', {
                    'max_retries': 3,
                    'timeout': 90
                })
        else:
            self.models = {}
            self.default_retry = {
                'max_retries': 3,
                'timeout': 90
            }
        
        # Model configuration loaded successfully
    
    def get_model(self, model_name: str) -> Optional[Dict]:
        """Get configuration for a specific model"""
        return self.models.get(model_name)
    
    def get_retry_config(self, model_name: str) -> Dict:
        """Get retry configuration for a specific model"""
        model_cfg = self.models.get(model_name, {})
        return {
            'max_retries': model_cfg.get('max_retries', self.default_retry.get('max_retries', 3)),
            'timeout': model_cfg.get('timeout', self.default_retry.get('timeout', 90))
        }
    
    def add_model(self, model_name: str, endpoint: str, api_key: str, model: str):
        """Add or update a model configuration"""
        self.models[model_name] = {
            "endpoint": endpoint,
            "api_key": api_key,
            "model": model
        }
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({"models": self.models}, f, indent=2)

# Global instance
_model_config = None

def get_model_config() -> ModelConfig:
    """Get the global model configuration instance"""
    global _model_config
    if _model_config is None:
        _model_config = ModelConfig()
    return _model_config
