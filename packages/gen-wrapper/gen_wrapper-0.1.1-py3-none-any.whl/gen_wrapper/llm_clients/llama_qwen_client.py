from .base import BaseLLMClient
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import json
from typing import List, Dict, Any

class LlamaQwenClient(BaseLLMClient):
    def __init__(self, model: str, config: Dict[str, Any]):
        super().__init__(model, {**config, "provider_name": "llama_qwen"})
        self.base_url = config["base_url"]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        try:
            self.validate_messages(messages)
            
            # Convert OpenAI format to local server format if needed
            prompt = self._convert_messages_to_prompt(messages)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": kwargs.get("temperature", 0.6),
                "max_tokens": kwargs.get("max_tokens", 32768),
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens"]}
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=self.config["timeout"]
            )
            response.raise_for_status()
            
            data = response.json()
            return self.get_unified_response(data.get("response", data.get("message", "")))
        except Exception as e:
            return self.get_unified_response(f"Error: {str(e)}", error=True)
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to a single prompt string"""
        prompt_parts = []
        for message in messages:
            role = message["role"]
            content = message["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n".join(prompt_parts) + "\nAssistant:"