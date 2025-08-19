# gen-wrapper

A unified interface for multiple LLM providers (OpenAI, Anthropic, Groq, DeepSeek, Fireworks, Gemini, local).

## Installation

```bash
pip install gen-wrapper
# or with extras
pip install "gen-wrapper[llm-providers,langchain,async]"
```

## Environment

Set needed API keys, e.g.:

```bash
# PowerShell
$env:OPENAI_API_KEY="your_openai_key"
$env:ANTHROPIC_API_KEY="your_anthropic_key"
$env:GROQ_API_KEY="your_groq_key"
$env:DEEPSEEK_API_KEY="your_deepseek_key"
$env:FIREWORKS_API_KEY="your_fireworks_key"
$env:GOOGLE_API_KEY="your_google_key"
```

## Usage (Python)

```python
from gen_wrapper import LLMWrapper

wrapper = LLMWrapper("openai", "gpt-4o")
print(wrapper.simple_chat("Hello!"))
```

## CLI

```bash
llm-cli --list-providers
llm-cli --list-models openai
llm-cli --provider openai --prompt "Hello world"
```