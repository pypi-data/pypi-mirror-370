import os
import requests
from typing import List, Dict, Any, Optional
from .llm_client_factory import get_llm_client
from .providers_config import get_provider_config, PROVIDERS_CONFIG

class LLMWrapperError(Exception):
    """Custom exception for LLM wrapper errors"""
    pass

class LLMWrapper:
    def __init__(self, provider_name: str, model: Optional[str] = None):
        """
        Initialize LLM wrapper
        
        Args:
            provider_name: Name of the provider (e.g., 'openai', 'anthropic')
            model: Model name (if None, uses default model)
        """
        if provider_name not in PROVIDERS_CONFIG:
            available = list(PROVIDERS_CONFIG.keys())
            raise LLMWrapperError(f"Provider '{provider_name}' not supported. Available: {available}")
        
        config = get_provider_config(provider_name)
        self.provider_name = provider_name
        self.model = model or config.default_model
        
        # Only validate API keys, not model names - let the API handle model validation
        self._validate_api_credentials(config)
        
        try:
            self.client = get_llm_client(provider_name, self.model)
        except Exception as e:
            raise LLMWrapperError(f"Failed to initialize {provider_name} client: {str(e)}")
    
    def _validate_api_credentials(self, config) -> None:
        """Validate API credentials without validating model names"""
        if config.api_key_env:
            api_key = os.getenv(config.api_key_env)
            if not api_key:
                raise LLMWrapperError(f"API key not found. Please set environment variable: {config.api_key_env}")
        
        # Additional validation for Azure OpenAI
        if self.provider_name == "azure_openai":
            endpoint = os.getenv(config.endpoint_env)
            if not endpoint:
                raise LLMWrapperError(f"Azure endpoint not found. Please set environment variable: {config.endpoint_env}")
    
    @staticmethod
    def list_providers() -> List[str]:
        """Get list of available providers"""
        return list(PROVIDERS_CONFIG.keys())
    
    @staticmethod
    def list_models(provider_name: str) -> List[str]:
        """
        Get list of available models for a provider
        Now fetches dynamically from API when possible
        """
        if provider_name not in PROVIDERS_CONFIG:
            available = list(PROVIDERS_CONFIG.keys())
            raise LLMWrapperError(f"Provider '{provider_name}' not supported. Available: {available}")
        
        config = get_provider_config(provider_name)
        
        # Try to fetch models dynamically from API
        try:
            models = LLMWrapper._fetch_models_from_api(provider_name, config)
            if models:
                return models
        except Exception as e:
            print(f"Warning: Could not fetch models from {provider_name} API: {e}")
        
        # Fallback to static list if available
        if config.fallback_models:
            return config.fallback_models
        
        # Return empty list - any model name will be allowed
        return []
    
    @staticmethod
    def _fetch_models_from_api(provider_name: str, config) -> Optional[List[str]]:
        """Fetch available models from provider API"""
        if not config.models_endpoint:
            return None
        
        # Skip API call if no credentials
        if config.api_key_env:
            api_key = os.getenv(config.api_key_env)
            if not api_key:
                return None
        
        try:
            if provider_name == "openai":
                return LLMWrapper._fetch_openai_models(config, api_key)
            elif provider_name == "groq":
                return LLMWrapper._fetch_groq_models(config, api_key)
            elif provider_name == "fireworks":
                return LLMWrapper._fetch_fireworks_models(config, api_key)
            elif provider_name == "gemini":
                return LLMWrapper._fetch_gemini_models(config, api_key)
            elif provider_name == "azure_openai":
                return LLMWrapper._fetch_azure_models(config)
            elif provider_name == "llama_qwen":
                return LLMWrapper._fetch_local_models(config)
        except Exception:
            return None
        
        return None
    
    @staticmethod
    def _fetch_openai_models(config, api_key: str) -> List[str]:
        """Fetch OpenAI models"""
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{config.base_url}/models", 
            headers=headers, 
            timeout=10
        )
        response.raise_for_status()
        
        models_data = response.json()
        return [model["id"] for model in models_data.get("data", [])]
    
    @staticmethod
    def _fetch_groq_models(config, api_key: str) -> List[str]:
        """Fetch Groq models"""
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{config.base_url}/models", 
            headers=headers, 
            timeout=10
        )
        response.raise_for_status()
        
        models_data = response.json()
        return [model["id"] for model in models_data.get("data", [])]
    
    @staticmethod
    def _fetch_fireworks_models(config, api_key: str) -> List[str]:
        """Fetch Fireworks models"""
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{config.base_url}/models", 
            headers=headers, 
            timeout=10
        )
        response.raise_for_status()
        
        models_data = response.json()
        return [model["id"] for model in models_data.get("data", [])]
    
    @staticmethod
    def _fetch_gemini_models(config, api_key: str) -> List[str]:
        """Fetch Gemini models"""
        response = requests.get(
            f"{config.base_url}/models?key={api_key}", 
            timeout=10
        )
        response.raise_for_status()
        
        models_data = response.json()
        models = []
        for model in models_data.get("models", []):
            model_name = model.get("name", "").replace("models/", "")
            if model_name:
                models.append(model_name)
        return models
    
    @staticmethod
    def _fetch_azure_models(config) -> List[str]:
        """Fetch Azure OpenAI models"""
        api_key = os.getenv(config.api_key_env)
        endpoint = os.getenv(config.endpoint_env)
        api_version = os.getenv(config.api_version_env) or "2024-02-15-preview"
        
        if not api_key or not endpoint:
            return []
        
        headers = {"api-key": api_key}
        response = requests.get(
            f"{endpoint}/openai/models?api-version={api_version}", 
            headers=headers, 
            timeout=10
        )
        response.raise_for_status()
        
        models_data = response.json()
        return [model["id"] for model in models_data.get("data", [])]
    
    @staticmethod
    def _fetch_local_models(config) -> List[str]:
        """Fetch local models (Ollama/LlamaQwen)"""
        try:
            response = requests.get(
                f"{config.base_url}/api/tags",  # Ollama uses /api/tags endpoint
                timeout=5
            )
            response.raise_for_status()
            
            models_data = response.json()
            return [model.get("name", "").split(":")[0] for model in models_data.get("models", [])]
        except Exception:
            return []
    
    def simple_chat(self, message: str, **kwargs) -> str:
        """
        Simple chat interface
        
        Args:
            message: User message
            **kwargs: Additional parameters for the model
            
        Returns:
            Model response as string
        """
        messages = [{"role": "user", "content": message}]
        response = self.client.chat(messages, **kwargs)
        
        if response.get("error"):
            raise LLMWrapperError(f"Chat failed: {response['message']}")
        
        return response["message"]
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Advanced chat interface with message history
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters for the model
            
        Returns:
            Full response dictionary
        """
        response = self.client.chat(messages, **kwargs)
        
        if response.get("error"):
            raise LLMWrapperError(f"Chat failed: {response['message']}")
        
        return response
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider and model"""
        config = get_provider_config(self.provider_name)
        
        return {
            "provider": self.provider_name,
            "model": self.model,
            "base_url": config.base_url,
            "langchain_support": config.langchain_support,
            "timeout": config.timeout,
            "max_retries": config.retry.max_attempts
        }