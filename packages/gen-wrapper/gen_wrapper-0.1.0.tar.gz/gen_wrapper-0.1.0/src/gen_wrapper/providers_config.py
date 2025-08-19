import os
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class RetryConfig(BaseModel):
    """Configuration for retry mechanisms"""
    max_attempts: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    initial_delay: float = Field(default=1.0, ge=0.1, le=60.0, description="Initial delay in seconds")
    max_delay: float = Field(default=60.0, ge=1.0, le=300.0, description="Maximum delay in seconds")
    exponential_base: float = Field(default=2.0, ge=1.1, le=5.0, description="Exponential backoff base")
    jitter: bool = Field(default=True, description="Add random jitter to delays")
    backoff_factor: float = Field(default=1.0, ge=0.1, le=5.0, description="Backoff multiplier")

    @field_validator('max_delay')
    @classmethod
    def max_delay_greater_than_initial(cls, v, info):
        if info.data and 'initial_delay' in info.data and v <= info.data['initial_delay']:
            raise ValueError('max_delay must be greater than initial_delay')
        return v

class RateLimitConfig(BaseModel):
    """Configuration for rate limiting"""
    requests_per_minute: Optional[int] = Field(default=None, ge=1, description="Requests per minute limit")
    requests_per_hour: Optional[int] = Field(default=None, ge=1, description="Requests per hour limit")
    requests_per_day: Optional[int] = Field(default=None, ge=1, description="Requests per day limit")
    burst_limit: Optional[int] = Field(default=None, ge=1, description="Burst request limit")

    @model_validator(mode='after')
    def validate_rate_limits(self):
        rpm = self.requests_per_minute
        rph = self.requests_per_hour
        rpd = self.requests_per_day
        
        if rpm and rph and rpm * 60 > rph:
            raise ValueError('requests_per_minute * 60 cannot exceed requests_per_hour')
        if rph and rpd and rph * 24 > rpd:
            raise ValueError('requests_per_hour * 24 cannot exceed requests_per_day')
        
        return self

class CacheConfig(BaseModel):
    """Configuration for caching"""
    enabled: bool = Field(default=True, description="Enable caching")
    ttl_seconds: int = Field(default=300, ge=1, le=86400, description="Cache TTL in seconds")
    max_entries: int = Field(default=1000, ge=1, le=100000, description="Maximum cache entries")

class CircuitBreakerConfig(BaseModel):
    """Configuration for circuit breaker"""
    enabled: bool = Field(default=True, description="Enable circuit breaker")
    failure_threshold: int = Field(default=5, ge=1, le=100, description="Failure threshold")
    recovery_timeout: int = Field(default=60, ge=1, le=3600, description="Recovery timeout in seconds")
    half_open_max_calls: int = Field(default=3, ge=1, le=10, description="Max calls in half-open state")

class HealthCheckConfig(BaseModel):
    """Configuration for health checks"""
    enabled: bool = Field(default=True, description="Enable health checks")
    interval_seconds: int = Field(default=300, ge=10, le=3600, description="Health check interval")
    timeout_seconds: int = Field(default=10, ge=1, le=60, description="Health check timeout")
    endpoint: Optional[str] = Field(default=None, description="Health check endpoint")

class ModelOverride(BaseModel):
    """Model-specific configuration overrides"""
    timeout: Optional[int] = Field(default=None, ge=1, le=600)
    rate_limit: Optional[RateLimitConfig] = None
    retry: Optional[RetryConfig] = None

class ProviderConfig(BaseModel):
    """Configuration for a single provider"""
    # Basic Configuration
    api_key_env: Optional[str] = Field(description="Environment variable for API key")
    default_model: str = Field(description="Default model name")
    models: str = Field(default="dynamic", description="Model discovery method")
    models_endpoint: Optional[str] = Field(default=None, description="Models API endpoint")
    fallback_models: Optional[List[str]] = Field(default=None, description="Fallback model list")
    base_url: Optional[str] = Field(description="API base URL")
    langchain_support: bool = Field(default=True, description="LangChain integration support")
    
    # Azure-specific fields
    endpoint_env: Optional[str] = Field(default=None, description="Azure endpoint environment variable")
    deployment_env: Optional[str] = Field(default=None, description="Azure deployment environment variable")
    api_version_env: Optional[str] = Field(default=None, description="Azure API version environment variable")
    
    # Timeout Configuration
    timeout: int = Field(default=30, ge=1, le=600, description="Request timeout in seconds")
    connect_timeout: int = Field(default=10, ge=1, le=60, description="Connection timeout in seconds")
    read_timeout: int = Field(default=60, ge=1, le=600, description="Read timeout in seconds")
    
    # Advanced Configuration
    retry: RetryConfig = Field(default_factory=RetryConfig, description="Retry configuration")
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig, description="Rate limiting configuration")
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig, description="Circuit breaker configuration")
    cache: CacheConfig = Field(default_factory=CacheConfig, description="Cache configuration")
    health_check: HealthCheckConfig = Field(default_factory=HealthCheckConfig, description="Health check configuration")
    
    # Error Handling
    retry_on_status: List[int] = Field(default_factory=lambda: [429, 500, 502, 503, 504], description="HTTP status codes to retry on")
    retry_on_exceptions: List[str] = Field(default_factory=lambda: ["ConnectionError", "Timeout", "RequestException"], description="Exception types to retry on")
    max_concurrent_requests: int = Field(default=10, ge=1, le=1000, description="Maximum concurrent requests")
    
    # Monitoring
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    logging_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_requests: bool = Field(default=False, description="Log request details")
    log_responses: bool = Field(default=False, description="Log response details")
    
    # Model Specific Settings
    model_overrides: Dict[str, ModelOverride] = Field(default_factory=dict, description="Model-specific overrides")

    @field_validator('retry_on_status')
    @classmethod
    def validate_status_codes(cls, v):
        for status in v:
            if not (100 <= status <= 599):
                raise ValueError(f'Invalid HTTP status code: {status}')
        return v

    @model_validator(mode='after')
    def timeout_validation(self):
        if self.timeout <= self.connect_timeout:
            raise ValueError('timeout must be greater than connect_timeout')
        return self

class GlobalConfig(BaseSettings):
    """Global configuration settings"""
    # Global settings
    enable_telemetry: bool = Field(default=True, description="Enable telemetry")
    telemetry_endpoint: Optional[str] = Field(default=None, description="Telemetry endpoint URL")
    environment: str = Field(default="development", description="Environment name")
    service_name: str = Field(default="llm-wrapper", description="Service name")
    version: str = Field(default="1.0.0", description="Service version")
    
    # Security
    api_key_rotation_enabled: bool = Field(default=True, description="Enable API key rotation")
    api_key_rotation_interval: int = Field(default=86400, ge=3600, description="API key rotation interval in seconds")
    request_signing_enabled: bool = Field(default=False, description="Enable request signing")
    
    # Monitoring
    prometheus_enabled: bool = Field(default=True, description="Enable Prometheus metrics")
    prometheus_port: int = Field(default=8000, ge=1024, le=65535, description="Prometheus metrics port")
    health_check_port: int = Field(default=8001, ge=1024, le=65535, description="Health check port")
    
    # Performance
    connection_pool_size: int = Field(default=100, ge=1, le=1000, description="Connection pool size")
    connection_pool_maxsize: int = Field(default=200, ge=1, le=2000, description="Maximum connection pool size")
    dns_cache_ttl: int = Field(default=300, ge=0, le=3600, description="DNS cache TTL in seconds")
    
    # Feature flags
    enable_caching: bool = Field(default=True, description="Enable caching globally")
    enable_circuit_breaker: bool = Field(default=True, description="Enable circuit breaker globally")
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting globally")
    enable_health_checks: bool = Field(default=True, description="Enable health checks globally")
    enable_request_tracing: bool = Field(default=False, description="Enable request tracing")
    enable_response_compression: bool = Field(default=True, description="Enable response compression")

    model_config = {
        "env_prefix": "LLM_WRAPPER_",
        "case_sensitive": False
    }

# Provider configurations with ALL rate limits FIXED
PROVIDERS_CONFIG = {
    "openai": ProviderConfig(
        api_key_env="OPENAI_API_KEY",
        default_model="gpt-4o-mini",
        models_endpoint="/models",
        base_url="https://api.openai.com/v1",
        langchain_support=True,
        timeout=30,
        connect_timeout=10,
        read_timeout=60,
        retry=RetryConfig(max_attempts=3, initial_delay=1.0, max_delay=60.0),
        rate_limit=RateLimitConfig(requests_per_minute=50, requests_per_hour=3000, burst_limit=10),  # 50*60=3000 ✓
        circuit_breaker=CircuitBreakerConfig(failure_threshold=5, recovery_timeout=60),
        cache=CacheConfig(ttl_seconds=300, max_entries=1000),
        health_check=HealthCheckConfig(interval_seconds=300, endpoint="/models"),
        max_concurrent_requests=10,
        model_overrides={
            "gpt-4": ModelOverride(
                timeout=120,
                rate_limit=RateLimitConfig(requests_per_minute=20, requests_per_hour=1200)  # 20*60=1200 ✓
            ),
            "gpt-4o": ModelOverride(
                timeout=90,
                rate_limit=RateLimitConfig(requests_per_minute=30, requests_per_hour=1800)  # 30*60=1800 ✓
            )
        }
    ),
    
    "anthropic": ProviderConfig(
        api_key_env="ANTHROPIC_API_KEY",
        default_model="claude-3-sonnet-20240229",
        models_endpoint=None,
        fallback_models=["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        base_url="https://api.anthropic.com/v1",
        langchain_support=True,
        timeout=60,
        connect_timeout=15,
        read_timeout=120,
        retry=RetryConfig(max_attempts=3, initial_delay=2.0, max_delay=120.0),
        rate_limit=RateLimitConfig(requests_per_minute=16, requests_per_hour=1000, burst_limit=5),  # 16*60=960 < 1000 ✓
        circuit_breaker=CircuitBreakerConfig(failure_threshold=3, recovery_timeout=120),
        cache=CacheConfig(ttl_seconds=600, max_entries=500),
        health_check=HealthCheckConfig(enabled=False, interval_seconds=600),
        max_concurrent_requests=5
    ),
    
    "groq": ProviderConfig(
        api_key_env="GROQ_API_KEY",
        default_model="llama3-8b-8192",
        models_endpoint="/models",
        base_url="https://api.groq.com/openai/v1",
        langchain_support=False,
        timeout=30,
        connect_timeout=5,
        read_timeout=60,
        retry=RetryConfig(max_attempts=2, initial_delay=0.5, max_delay=30.0, exponential_base=1.5),
        rate_limit=RateLimitConfig(requests_per_minute=240, requests_per_hour=14400, burst_limit=15),  # 240*60=14400 ✓
        circuit_breaker=CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30),
        cache=CacheConfig(ttl_seconds=180, max_entries=1000),
        health_check=HealthCheckConfig(interval_seconds=180, endpoint="/models"),
        max_concurrent_requests=15
    ),
    
    "fireworks": ProviderConfig(
        api_key_env="FIREWORKS_API_KEY",
        default_model="accounts/fireworks/models/llama-v3p1-8b-instruct",
        models_endpoint="/models",
        base_url="https://api.fireworks.ai/inference/v1",
        langchain_support=True,
        timeout=45,
        connect_timeout=10,
        read_timeout=90,
        retry=RetryConfig(max_attempts=3, initial_delay=1.0, max_delay=60.0),
        rate_limit=RateLimitConfig(requests_per_minute=33, requests_per_hour=2000, burst_limit=10),  # 33*60=1980 < 2000 ✓
        circuit_breaker=CircuitBreakerConfig(failure_threshold=4, recovery_timeout=45),
        cache=CacheConfig(ttl_seconds=300, max_entries=800),
        health_check=HealthCheckConfig(interval_seconds=300, endpoint="/models"),
        max_concurrent_requests=12
    ),
    
    "gemini": ProviderConfig(
        api_key_env="GOOGLE_API_KEY",
        default_model="gemini-1.5-flash",
        models_endpoint="/models",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        langchain_support=True,
        timeout=90,
        connect_timeout=15,
        read_timeout=180,
        retry=RetryConfig(max_attempts=2, initial_delay=5.0, max_delay=180.0, exponential_base=3.0),
        rate_limit=RateLimitConfig(requests_per_minute=8, requests_per_hour=480, requests_per_day=11520, burst_limit=3),  # 8*60=480, 480*24=11520 ✓
        circuit_breaker=CircuitBreakerConfig(failure_threshold=2, recovery_timeout=300),
        cache=CacheConfig(ttl_seconds=1800, max_entries=200),
        health_check=HealthCheckConfig(interval_seconds=600, endpoint="/models"),
        max_concurrent_requests=2
    ),
    
    "azure_openai": ProviderConfig(
        api_key_env="AZURE_OPENAI_API_KEY",
        endpoint_env="AZURE_OPENAI_ENDPOINT",
        deployment_env="AZURE_OPENAI_DEPLOYMENT",
        api_version_env="AZURE_OPENAI_API_VERSION",
        default_model="gpt-4o",
        models_endpoint="/models",
        base_url=None,
        langchain_support=True,
        timeout=60,
        connect_timeout=15,
        read_timeout=120,
        retry=RetryConfig(max_attempts=3, initial_delay=2.0, max_delay=120.0),
        rate_limit=RateLimitConfig(requests_per_minute=100, requests_per_hour=6000, burst_limit=20),  # 100*60=6000 ✓
        circuit_breaker=CircuitBreakerConfig(failure_threshold=5, recovery_timeout=90),
        cache=CacheConfig(ttl_seconds=600, max_entries=1000),
        health_check=HealthCheckConfig(interval_seconds=300, endpoint="/models"),
        max_concurrent_requests=20
    ),
    
    "llama_qwen": ProviderConfig(
        api_key_env=None,
        default_model="deepseek-r1-distill-llama-70b",
        models_endpoint="/api/tags",
        fallback_models=["deepseek-r1-distill-llama-70b", "deepseek-r1-distill-qwen-32b"],
        base_url="http://localhost:11434",
        langchain_support=False,
        timeout=120,
        connect_timeout=5,
        read_timeout=300,
        retry=RetryConfig(max_attempts=2, initial_delay=1.0, max_delay=10.0, jitter=False),
        rate_limit=RateLimitConfig(requests_per_minute=None, burst_limit=5),  # No rate limits for local
        circuit_breaker=CircuitBreakerConfig(failure_threshold=3, recovery_timeout=30),
        cache=CacheConfig(ttl_seconds=60, max_entries=100),
        health_check=HealthCheckConfig(interval_seconds=60, endpoint="/api/tags"),
        retry_on_status=[500, 502, 503, 504],
        retry_on_exceptions=["ConnectionError", "Timeout"],
        max_concurrent_requests=2,
        logging_level=LogLevel.DEBUG,
        log_requests=True
    )
}

# Global configuration instance
global_config = GlobalConfig()

class ConfigDict(dict):
    """Dictionary that also allows attribute access for backward compatibility"""
    def __init__(self, data):
        super().__init__()
        for key, value in data.items():
            if isinstance(value, dict):
                self[key] = ConfigDict(value)
            else:
                self[key] = value
    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'ConfigDict' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        self[name] = value

def get_provider_config(provider_name: str) -> Optional[ConfigDict]:
    """Get validated provider configuration as dictionary with attribute access"""
    config = PROVIDERS_CONFIG.get(provider_name)
    if config:
        return ConfigDict(config.model_dump())
    return None

def get_model_specific_config(provider_name: str, model_name: str) -> Optional[ConfigDict]:
    """Get model-specific configuration with overrides applied as dictionary"""
    config = PROVIDERS_CONFIG.get(provider_name)
    if not config:
        return None
    
    if model_name in config.model_overrides:
        # Create a copy and apply overrides
        config_dict = config.model_dump()
        override = config.model_overrides[model_name]
        
        # Apply overrides
        for field, value in override.model_dump(exclude_unset=True).items():
            if value is not None:
                config_dict[field] = value
        
        return ConfigDict(config_dict)
    
    return ConfigDict(config.model_dump())
def validate_all_configs() -> Dict[str, bool]:
    """Validate all provider configurations"""
    results = {}
    for provider_name, config in PROVIDERS_CONFIG.items():
        try:
            # Pydantic automatically validates during instantiation
            results[provider_name] = True
        except Exception as e:
            results[provider_name] = False
            print(f"Validation failed for {provider_name}: {e}")
    
    return results

# Export for backward compatibility
PROVIDERS = {name: config.model_dump() for name, config in PROVIDERS_CONFIG.items()}