# gen-wrapper

[![PyPI](https://img.shields.io/pypi/v/gen-wrapper.svg)](https://pypi.org/project/gen-wrapper/)
[![Python](https://img.shields.io/pypi/pyversions/gen-wrapper.svg)](https://pypi.org/project/gen-wrapper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A unified interface for multiple LLM providers (OpenAI, Anthropic, Groq, DeepSeek, Fireworks, Gemini, local).

## Installation

```bash
pip install gen-wrapper
# or with extras
pip install "gen-wrapper[llm-providers,langchain,async]"
```

## Environment

Set needed API keys, e.g. (PowerShell):

```powershell
$env:OPENAI_API_KEY="your_openai_key"
$env:ANTHROPIC_API_KEY="your_anthropic_key"
$env:GROQ_API_KEY="your_groq_key"
$env:DEEPSEEK_API_KEY="your_deepseek_key"
$env:FIREWORKS_API_KEY="your_fireworks_key"
$env:GOOGLE_API_KEY="your_google_key"

# Azure OpenAI (optional)
$env:AZURE_OPENAI_API_KEY="..."
$env:AZURE_OPENAI_ENDPOINT="..."
$env:AZURE_OPENAI_DEPLOYMENT="..."
$env:AZURE_OPENAI_API_VERSION="..."
```

## Quickstart (Python)

```python
from gen_wrapper import LLMWrapper

wrapper = LLMWrapper(provider="openai", model="gpt-4o")
print(wrapper.simple_chat("Hello!"))
```

## CLI

```bash
llm-cli --list-providers
llm-cli --list-models openai
llm-cli --provider openai --prompt "Hello world"
```

## Extras

- llm-providers: OpenAI, Anthropic, Google Generative AI SDKs
- langchain: LangChain core + provider adapters
- async: aiohttp, httpx
- monitoring: prometheus-client

## Links

- Source, docs, and issues: https://github.com/lakshya811/gen_wrapper
- PyPI: https://pypi.org/project/gen-wrapper/

## License

MIT
