from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any

class BaseLLMClient(ABC):
    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.config = config
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Abstract method to handle chat interactions.
        Args:
            messages: List of dictionaries with 'role' and 'content' keys
            **kwargs: Additional parameters specific to each provider
        Returns:
            Dictionary with unified response format
        """
        pass
    
    def get_unified_response(self, message: str, **extra_data) -> Dict[str, Any]:
        """Create unified response format"""
        response = {
            "message": message,
            "provider": self.config.get("provider_name", "unknown"),
            "model": self.model,
            "timestamp": datetime.utcnow().isoformat()
        }
        response.update(extra_data)
        return response
    
    def validate_messages(self, messages: List[Dict[str, str]]) -> None:
        """Validate message format"""
        if not isinstance(messages, list):
            raise ValueError("Messages must be a list")
        
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                raise ValueError(f"Message {i} must be a dictionary")
            
            if "role" not in message or "content" not in message:
                raise ValueError(f"Message {i} must have 'role' and 'content' keys")
            
            if message["role"] not in ["system", "user", "assistant"]:
                raise ValueError(f"Message {i} role must be 'system', 'user', or 'assistant'")
            
