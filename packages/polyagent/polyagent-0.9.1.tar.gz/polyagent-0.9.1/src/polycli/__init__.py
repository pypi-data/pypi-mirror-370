import json
from pathlib import Path

# Initialize Qwen settings on package import
def _init_qwen_settings():
    qwen_settings_path = Path.home() / ".qwen" / "settings.json"
    qwen_settings_path.parent.mkdir(parents=True, exist_ok=True)
    
    settings = {}
    if qwen_settings_path.exists():
        try:
            with open(qwen_settings_path, 'r') as f:
                settings = json.load(f)
        except:
            settings = {}
    
    current_limit = settings.get("sessionTokenLimit")
    if current_limit != 80000:
        settings["sessionTokenLimit"] = 80000  # @@@qwen-session-limit: Global Qwen token limit
        with open(qwen_settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        # Print notification when changed
        if current_limit is None:
            print(f"✅ Initialized Qwen session token limit to 80,000 tokens")
        else:
            print(f"📝 Updated Qwen session token limit from {current_limit:,} to 80,000 tokens")

# Run initialization
_init_qwen_settings()

# Import the unified PolyAgent class
from .polyagent import PolyAgent

__all__ = ['PolyAgent']