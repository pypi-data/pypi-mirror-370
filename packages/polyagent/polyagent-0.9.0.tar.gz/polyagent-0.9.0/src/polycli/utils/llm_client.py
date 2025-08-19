"""
LLM client creation utility
"""
import instructor
from openai import OpenAI
from instructor import Mode
from .model_config import get_model_config
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from dataclasses import dataclass, field, asdict

class ConfiguredClient:
    """A thin wrapper around instructor client that injects retry configuration.
    
    Preserves the exact same API as instructor client while automatically
    applying retry configuration from models.json.
    """
    
    def __init__(self, client: Any, retry_config: Dict[str, Any]):
        """Initialize with an instructor client and retry configuration.
        
        Args:
            client: The instructor client instance
            retry_config: Dict with 'max_retries' and 'timeout' settings
        """
        self._client = client
        self._retry_config = retry_config
        
        # Preserve the nested API structure of instructor client
        self.chat = self
        self.completions = self
        
        # Expose other client attributes/methods directly
        # This allows access to client.mode, client.provider, etc.
        self.mode = client.mode
        self.provider = getattr(client, 'provider', None)
    
    def create(self, **kwargs) -> Any:
        """Create a completion with injected retry configuration.
        
        Injects default retry settings but allows per-call overrides.
        """
        # Inject retry defaults but allow overrides
        for key, value in self._retry_config.items():
            kwargs.setdefault(key, value)
        
        # Delegate to the actual instructor client
        return self._client.chat.completions.create(**kwargs)
    
    def __getattr__(self, name):
        """Forward any other attribute access to the underlying client."""
        return getattr(self._client, name)

def get_llm_client(model_name: str):
    """Create an LLM client for the specified model using its configuration.
    
    Args:
        model_name: Name of the model as defined in models.json
        
    Returns:
        tuple: (client, actual_model_name) where client is the configured instructor client
               with retry settings and actual_model_name is the model name to use in API calls
        
    Raises:
        ValueError: If model not found in configuration or client creation fails
    """
    # Get model configuration
    config = get_model_config()
    model_cfg = config.get_model(model_name)
    if not model_cfg:
        raise ValueError(f"Model '{model_name}' not found in configuration. Please add it to models.json")
    
    # Get retry configuration for this model
    retry_config = config.get_retry_config(model_name)
    
    # Create client for this model
    try:
        instructor_client = instructor.from_openai(
            OpenAI(
                api_key=model_cfg['api_key'],
                base_url=model_cfg['endpoint']
            ),
            mode=Mode.JSON
        )
        
        # Wrap with retry configuration
        configured_client = ConfiguredClient(instructor_client, retry_config)
        
        actual_model_name = model_cfg['model']
        return configured_client, actual_model_name
    except Exception as e:
        raise ValueError(f"Failed to initialize client for model '{model_name}': {e}")

@dataclass
class CustomMiniSweModelConfig:
    """Configuration for CustomMiniSweModel"""
    model_name: str
    api_key: str = ""
    api_base: str = ""
    model_kwargs: Dict = field(default_factory=dict)

class CustomMiniSweModel:
    """Custom model for mini-swe-agent using direct OpenAI API"""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.model_kwargs = kwargs
        self.n_calls = 0
        self.cost = 0.0
        
        # Get client using our existing utility
        self.client, self.actual_model = get_llm_client(model_name)
        
        # Create config object for mini-swe compatibility
        model_cfg = get_model_config().get_model(model_name)
        self.config = CustomMiniSweModelConfig(
            model_name=self.actual_model,
            api_key=model_cfg['api_key'] if model_cfg else "",
            api_base=model_cfg['endpoint'] if model_cfg else "",
            model_kwargs=kwargs
        )
    
    def query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, str]:
        """Query the model and return response in mini-swe expected format"""
        # Merge kwargs
        final_kwargs = {**self.model_kwargs, **kwargs}
        
        # For mini-swe, we need raw text response, not structured output
        # Create a plain OpenAI client instead of instructor
        from openai import OpenAI
        model_cfg = get_model_config().get_model(self.model_name)
        plain_client = OpenAI(
            api_key=model_cfg['api_key'],
            base_url=model_cfg['endpoint']
        )
        
        # Make the API call
        response = plain_client.chat.completions.create(
            model=self.actual_model,
            messages=messages,
            **final_kwargs
        )
        
        self.n_calls += 1
        
        # Return in the format mini-swe expects
        content = response.choices[0].message.content or ""
        return {"content": content}