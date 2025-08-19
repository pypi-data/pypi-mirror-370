import argparse
import json
from .llm_wrapper import LLMWrapper, LLMWrapperError
from dotenv import load_dotenv
load_dotenv()
def main():
    parser = argparse.ArgumentParser(description="CLI tool to test LLM providers")
    parser.add_argument("--provider", help="Provider name")
    parser.add_argument("--model", help="Model name (optional)")
    parser.add_argument("--prompt", help="Prompt to send to the model")
    parser.add_argument("--list-providers", action="store_true", help="List available providers")
    parser.add_argument("--list-models", help="List models for a provider")
    parser.add_argument("--info", action="store_true", help="Show provider info")
    parser.add_argument("--temperature", type=float, help="Temperature for generation")
    parser.add_argument("--max-tokens", type=int, help="Maximum tokens")
    
    args = parser.parse_args()
    
    # Handle operations that don't require provider
    if args.list_providers:
        providers = LLMWrapper.list_providers()
        print("Available providers:")
        for provider in providers:
            print(f"  - {provider}")
        return
    
    if args.list_models:
        try:
            models = LLMWrapper.list_models(args.list_models)
            print(f"Models for {args.list_models}:")
            for model in models:
                print(f"  - {model}")
        except LLMWrapperError as e:
            print(f"Error: {e}")
        return
    
    # For all other operations, provider is required
    if not args.provider:
        print("Error: --provider is required unless using --list-providers or --list-models")
        parser.print_help()
        return
    
    if not args.prompt and not args.info:
        print("Error: --prompt is required unless using --info")
        return
    
    try:
        wrapper = LLMWrapper(args.provider, args.model)
        
        if args.info:
            info = wrapper.get_provider_info()
            print("Provider Information:")
            print(json.dumps(info, indent=2))
            return
        
        # Prepare kwargs
        kwargs = {}
        if args.temperature is not None:
            kwargs["temperature"] = args.temperature
        if args.max_tokens is not None:
            kwargs["max_tokens"] = args.max_tokens
        
        response = wrapper.simple_chat(args.prompt, **kwargs)
        print(response)
        
    except LLMWrapperError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()