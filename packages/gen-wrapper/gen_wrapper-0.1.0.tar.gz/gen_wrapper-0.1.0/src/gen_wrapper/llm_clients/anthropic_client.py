from .base import BaseLLMClient
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import os
import json
from typing import List, Dict, Any

class AnthropicClient(BaseLLMClient):
    def __init__(self, model: str, config: Dict[str, Any]):
        super().__init__(model, {**config, "provider_name": "anthropic"})
        self.api_key = os.getenv(config["api_key_env"])
        self.base_url = config["base_url"]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        try:
            self.validate_messages(messages)
            
            # Convert OpenAI format to Anthropic format
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.model,
                "messages": user_messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                **{k: v for k, v in kwargs.items() if k != "max_tokens"}
            }
            
            if system_message:
                payload["system"] = system_message
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=self.config["timeout"]
            )
            response.raise_for_status()
            
            data = response.json()
            return self.get_unified_response(
                data["content"][0]["text"],
                usage=data.get("usage"),
                stop_reason=data.get("stop_reason")
            )
        except Exception as e:
            return self.get_unified_response(f"Error: {str(e)}", error=True)