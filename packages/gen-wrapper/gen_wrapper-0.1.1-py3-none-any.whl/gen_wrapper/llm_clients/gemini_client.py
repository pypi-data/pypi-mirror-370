from .base import BaseLLMClient
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import os
import json
from typing import List, Dict, Any

class GeminiClient(BaseLLMClient):
    def __init__(self, model: str, config: Dict[str, Any]):
        super().__init__(model, {**config, "provider_name": "gemini"})
        self.api_key = os.getenv(config["api_key_env"])
        self.base_url = config["base_url"]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        try:
            self.validate_messages(messages)
            
            # Convert OpenAI format to Gemini format
            gemini_contents = self._convert_messages_to_gemini_format(messages)
            
            url = f"{self.base_url}/models/{self.model}:generateContent"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Gemini API parameters
            generation_config = {
                "temperature": kwargs.get("temperature", 0.9),
                "maxOutputTokens": kwargs.get("max_tokens", 2048),
                "topP": kwargs.get("top_p", 1.0),
                "topK": kwargs.get("top_k", 1)
            }
            
            payload = {
                "contents": gemini_contents,
                "generationConfig": generation_config
            }
            
            # Add safety settings if provided
            if "safety_settings" in kwargs:
                payload["safetySettings"] = kwargs["safety_settings"]
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                params={"key": self.api_key},
                timeout=self.config["timeout"]
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "candidates" in data and data["candidates"]:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return self.get_unified_response(
                    content,
                    usage=data.get("usageMetadata"),
                    finish_reason=data["candidates"][0].get("finishReason")
                )
            else:
                return self.get_unified_response("No response generated", error=True)
                
        except Exception as e:
            return self.get_unified_response(f"Error: {str(e)}", error=True)
    
    def _convert_messages_to_gemini_format(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Convert OpenAI message format to Gemini format"""
        gemini_contents = []
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            # Map roles: system -> user, user -> user, assistant -> model
            if role == "system":
                # Gemini doesn't have system role, convert to user message
                gemini_role = "user"
                content = f"Instructions: {content}"
            elif role == "user":
                gemini_role = "user"
            elif role == "assistant":
                gemini_role = "model"
            else:
                continue  # Skip unknown roles
            
            gemini_contents.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })
        
        return gemini_contents