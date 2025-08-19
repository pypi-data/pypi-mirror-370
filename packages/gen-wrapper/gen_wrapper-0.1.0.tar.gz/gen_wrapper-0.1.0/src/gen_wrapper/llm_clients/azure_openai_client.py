from .base import BaseLLMClient
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import os
import json
from typing import List, Dict, Any

class AzureOpenAIClient(BaseLLMClient):
    def __init__(self, model: str, config: Dict[str, Any]):
        super().__init__(model, {**config, "provider_name": "azure_openai"})
        self.api_key = os.getenv(config["api_key_env"])
        self.endpoint = os.getenv(config["endpoint_env"])
        self.deployment = os.getenv(config["deployment_env"], model)
        self.api_version = os.getenv(config["api_version_env"], "2024-02-15-preview")
        
        if not self.endpoint:
            raise ValueError("Azure OpenAI endpoint is required. Set AZURE_OPENAI_ENDPOINT environment variable.")
        
        # Construct base URL
        self.base_url = f"{self.endpoint.rstrip('/')}/openai/deployments/{self.deployment}"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        try:
            self.validate_messages(messages)
            
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": messages,
                **kwargs
            }
            
            url = f"{self.base_url}/chat/completions"
            params = {"api-version": self.api_version}
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                params=params,
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