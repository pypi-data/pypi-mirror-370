"""
gen_wrapper: A lightweight wrapper for multiple LLM providers.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gen-wrapper")
except PackageNotFoundError:
    __version__ = "0.0.0"

# Public API
from .llm_wrapper import LLMWrapper  # noqa: E402

__all__ = ["__version__", "LLMWrapper"]