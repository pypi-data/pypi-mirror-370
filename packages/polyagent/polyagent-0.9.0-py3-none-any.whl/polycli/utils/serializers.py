from typing import Any, Union
from pydantic import BaseModel
import json

def default_json_serializer(obj: Union[BaseModel, dict, Any]) -> str:
    """
    Serialise a Pydantic model *or* a plain dict to pretty-printed JSON.
    Falls back to json.dumps(obj) for any other JSON-serialisable value.
    """
    if isinstance(obj, BaseModel):
        # Pydantic v2 uses .model_dump(); v1 uses .dict()
        data = obj.model_dump() if hasattr(obj, "model_dump") else obj.dict()
    elif isinstance(obj, dict):
        data = obj
    else:
        data = obj  # hope it's already JSON-serialisable

    return json.dumps(data, ensure_ascii=False, indent=2)

def json_list_serializer(json_list) -> str:
    """One pretty-printed JSON blob per line (newline-delimited JSON)."""
    return "\n".join(default_json_serializer(item) for item in json_list)

