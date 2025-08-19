#!/usr/bin/env python3
"""
Adapters for unified agent response handling
"""

from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
import json


@dataclass
class RunResult:
    """Unified result wrapper for all agent responses"""
    
    content: str
    is_success: bool
    raw_result: Dict[str, Any]
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, raw_result: Union[Dict[str, Any], str]):
        """Create RunResult from raw agent response"""
        
        if isinstance(raw_result, str):
            self.content = raw_result
            self.is_success = True
            self.raw_result = {"content": raw_result}
            return
        
        if not isinstance(raw_result, dict):
            self.content = str(raw_result)
            self.is_success = False
            self.raw_result = {"raw": raw_result}
            self.error_message = "Non-dict result"
            return
        
        # Store raw result and initialize defaults
        self.raw_result = raw_result
        self.data = None
        self.error_message = None
        self.metadata = None
        
        # ClaudeAgent with Claude Code format (has _claude_metadata)
        if "result" in raw_result and "_claude_metadata" in raw_result:
            metadata = raw_result.get("_claude_metadata", {})
            is_error = metadata.get("is_error", False)
            
            self.content = raw_result["result"]
            self.is_success = not is_error
            if is_error:
                self.error_message = raw_result["result"]
            self.metadata = {
                "session_id": raw_result.get("session_id"),
                "model": raw_result.get("model"),
                "ephemeral": raw_result.get("ephemeral"),
                "claude_metadata": metadata
            }
            return
        
        # ClaudeAgent with non-Claude model format (has result, session_id, model but no _claude_metadata)
        if "result" in raw_result and "session_id" in raw_result and "model" in raw_result:
            result_data = raw_result["result"]
            
            # Handle structured response (when result is a dict)
            if isinstance(result_data, dict):
                self.content = json.dumps(result_data, indent=2)
                self.data = result_data
                self.is_success = True
            # Handle text response (when result is a string)
            elif isinstance(result_data, str):
                self.content = result_data
                self.is_success = True
            else:
                self.content = str(result_data)
                self.is_success = False
                self.error_message = "Unexpected result type"
            
            self.metadata = {
                "session_id": raw_result.get("session_id"),
                "model": raw_result.get("model"),
                "ephemeral": raw_result.get("ephemeral", False)
            }
            return
        
        # ClaudeAgent with non-Claude model error format
        if "error" in raw_result:
            self.content = raw_result["error"]
            self.is_success = False
            self.error_message = raw_result["error"]
            return
        
        # OpenSourceAgent structured response (no message key)
        if "result" in raw_result and "type" in raw_result and raw_result.get("type") == "structured":
            status = raw_result.get("status", "unknown")
            self.is_success = status in ("success", "Submitted")
            result_data = raw_result["result"]
            self.data = result_data if isinstance(result_data, dict) else None
            self.content = json.dumps(result_data, indent=2) if isinstance(result_data, dict) else str(result_data)
            self.error_message = None if self.is_success else str(result_data)
            self.metadata = {
                "type": raw_result.get("type"),
                "schema": raw_result.get("schema"),
                "status": status
            }
            return
        
        # OpenSourceAgent format (including no-tools mode)
        if "message" in raw_result:
            status = raw_result.get("status", "unknown")
            self.is_success = status in ("success", "Submitted")
            
            message = raw_result["message"]
            if isinstance(message, str):
                # Error case
                self.content = message
                self.error_message = message
            elif isinstance(message, dict) and "content" in message:
                # Success case
                self.content = message["content"]
                if not self.is_success:
                    self.error_message = message["content"]
                self.metadata = {
                    "role": message.get("role"),
                    "type": raw_result.get("type"),
                    "status": status
                }
            else:
                # Fallback for unexpected message format
                self.content = str(message)
                self.is_success = False
                self.error_message = "Unexpected message format"
            return
        
        # Direct error format
        if "status" in raw_result and raw_result["status"] == "error":
            error_msg = raw_result.get("message", "Unknown error")
            self.content = error_msg
            self.is_success = False
            self.error_message = error_msg
            return
        
        # Fallback for unknown format
        self.content = str(raw_result)
        self.is_success = False
        self.error_message = "Unknown result format"
    
    def __bool__(self) -> bool:
        """Allow boolean checks: if result: ..."""
        return self.is_success
    
    def __str__(self) -> str:
        """String representation returns the content"""
        return self.content
    
    def __repr__(self) -> str:
        """Debug representation - show full content"""
        status = "SUCCESS" if self.is_success else "ERROR"
        return f"RunResult({status}: {self.content})"
    
    def has_data(self) -> bool:
        """Check if structured data is available"""
        return self.data is not None
    
    def get_claude_cost(self) -> Optional[float]:
        """Get cost information if available from Claude metadata"""
        if self.metadata and "claude_metadata" in self.metadata:
            return self.metadata["claude_metadata"].get("total_cost_usd")
        return None
    
    def get_claude_tokens(self) -> Optional[Dict[str, int]]:
        """Get token usage if available from Claude metadata"""
        if self.metadata and "claude_metadata" in self.metadata:
            usage = self.metadata["claude_metadata"].get("usage", {})
            if usage:
                return {
                    "input": usage.get("input_tokens", 0),
                    "output": usage.get("output_tokens", 0),
                    "cache_creation": usage.get("cache_creation_input_tokens", 0),
                    "cache_read": usage.get("cache_read_input_tokens", 0)
                }
        return None
    
    def get_session_id(self) -> Optional[str]:
        """Get session ID if available"""
        if self.metadata:
            return self.metadata.get("session_id")
        return None