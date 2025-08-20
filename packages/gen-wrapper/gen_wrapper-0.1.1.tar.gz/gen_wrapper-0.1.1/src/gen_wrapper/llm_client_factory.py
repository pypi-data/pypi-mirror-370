from .llm_clients.base import BaseLLMClient
from .llm_clients.openai_client import OpenAIClient
from .llm_clients.anthropic_client import AnthropicClient
from .llm_clients.groq_client import GroqClient
from .llm_clients.deepseek_client import DeepSeekClient
from .llm_clients.fireworks_client import FireworksClient
from .llm_clients.llama_qwen_client import LlamaQwenClient
from .llm_clients.gemini_client import GeminiClient
from .llm_clients.azure_openai_client import AzureOpenAIClient
from .providers_config import get_provider_config
from dotenv import load_dotenv
load_dotenv()
def get_llm_client(provider_name, model=None):
    config = get_provider_config(provider_name)
    if not config:
        raise ValueError(f"Provider {provider_name} not found in configuration")
    
    model = model or config["default_model"]
    
    client_map = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "groq": GroqClient,
        # "deepseek": DeepSeekClient,
        "fireworks": FireworksClient,
        "llama_qwen": LlamaQwenClient,
        "gemini": GeminiClient,
        "azure_openai": AzureOpenAIClient
    }
    
    client_class = client_map.get(provider_name)
    if not client_class:
        raise ValueError(f"No client implementation for provider {provider_name}")
    
    return client_class(model, config)