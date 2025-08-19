from .base import BaseLLMClient
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import os
import json
from typing import List, Dict, Any

class FireworksClient(BaseLLMClient):
    def __init__(self, model: str, config: Dict[str, Any]):
        super().__init__(model, {**config, "provider_name": "fireworks"})
        self.api_key = os.getenv(config["api_key_env"])
        self.base_url = config["base_url"]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        try:
            self.validate_messages(messages)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                **kwargs
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.config["timeout"]
            )
            response.raise_for_status()
            
            data = response.json()
            return self.get_unified_response(
                data["choices"][0]["message"]["content"],
                usage=data.get("usage"),
                finish_reason=data["choices"][0].get("finish_reason")
            )
        except Exception as e:
            return self.get_unified_response(f"Error: {str(e)}", error=True)