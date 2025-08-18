import json
import os
import sys
from typing import Any, Dict
from pathlib import Path

import httpx
from anthropic import AsyncAnthropic
from openai import AsyncAzureOpenAI  # For Azure OpenAI client
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider

# Load system config if it exists
SYSTEM_CONFIG = {}
SYSTEM_CONFIG_PATH = Path.home() / ".code_puppy" / "system_config.json"
if SYSTEM_CONFIG_PATH.exists():
    try:
        with open(SYSTEM_CONFIG_PATH) as f:
            SYSTEM_CONFIG = json.load(f)
            # Apply environment overrides from config
            for key, value in SYSTEM_CONFIG.get("environment_overrides", {}).items():
                if key not in os.environ:
                    os.environ[key] = str(value)
    except Exception as e:
        print(f"Warning: Could not load system config: {e}", file=sys.stderr)

# Environment variables used in this module:
# - GEMINI_API_KEY: API key for Google's Gemini models. Required when using Gemini models.
# - OPENAI_API_KEY: API key for OpenAI models. Required when using OpenAI models or custom_openai endpoints.
# - TOGETHER_AI_KEY: API key for Together AI models. Required when using Together AI models.
#
# When using custom endpoints (type: "custom_openai" in models.json):
# - Environment variables can be referenced in header values by prefixing with $ in models.json.
#   Example: "X-Api-Key": "$OPENAI_API_KEY" will use the value from os.environ.get("OPENAI_API_KEY")


def get_custom_config(model_config):
    custom_config = model_config.get("custom_endpoint", {})
    if not custom_config:
        raise ValueError("Custom model requires 'custom_endpoint' configuration")

    url = custom_config.get("url")
    if not url:
        raise ValueError("Custom endpoint requires 'url' field")

    headers = {}
    for key, value in custom_config.get("headers", {}).items():
        if value.startswith("$"):
            value = os.environ.get(value[1:])
        headers[key] = value

    ca_certs_path = None
    if "ca_certs_path" in custom_config:
        ca_certs_path = custom_config.get("ca_certs_path")
        if ca_certs_path.lower() == "false":
            ca_certs_path = False

    api_key = None
    if "api_key" in custom_config:
        if custom_config["api_key"].startswith("$"):
            env_var_name = custom_config["api_key"][1:]
            api_key = os.environ.get(env_var_name)
        else:
            api_key = custom_config["api_key"]
    return url, headers, ca_certs_path, api_key


class ModelFactory:
    """A factory for creating and managing different AI models."""

    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """Loads model configurations from a JSON file."""
        with open(config_path, "r") as f:
            return json.load(f)

    @staticmethod
    def get_model(model_name: str, config: Dict[str, Any]) -> Any:
        """Returns a configured model instance based on the provided name and config."""
        model_config = config.get(model_name)
        if not model_config:
            raise ValueError(f"Model '{model_name}' not found in configuration.")

        model_type = model_config.get("type")

        if model_type == "gemini":
            provider = GoogleGLAProvider(api_key=os.environ.get("GEMINI_API_KEY", ""))

            model = GeminiModel(model_name=model_config["name"], provider=provider)
            setattr(model, "provider", provider)
            return model

        elif model_type == "openai":
            provider = OpenAIProvider(api_key=os.environ.get("OPENAI_API_KEY", ""))

            model = OpenAIModel(model_name=model_config["name"], provider=provider)
            setattr(model, "provider", provider)
            return model

        elif model_type == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY", None)
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY environment variable must be set for Anthropic models."
                )
            anthropic_client = AsyncAnthropic(api_key=api_key)
            provider = AnthropicProvider(anthropic_client=anthropic_client)
            return AnthropicModel(model_name=model_config["name"], provider=provider)

        elif model_type == "custom_anthropic":
            url, headers, ca_certs_path, api_key = get_custom_config(model_config)
            client = httpx.AsyncClient(headers=headers, verify=ca_certs_path)
            anthropic_client = AsyncAnthropic(
                base_url=url,
                http_client=client,
                api_key=api_key,
            )
            provider = AnthropicProvider(anthropic_client=anthropic_client)
            return AnthropicModel(model_name=model_config["name"], provider=provider)

        elif model_type == "azure_openai":
            azure_endpoint_config = model_config.get("azure_endpoint")
            if not azure_endpoint_config:
                raise ValueError(
                    "Azure OpenAI model type requires 'azure_endpoint' in its configuration."
                )
            azure_endpoint = azure_endpoint_config
            if azure_endpoint_config.startswith("$"):
                azure_endpoint = os.environ.get(azure_endpoint_config[1:])
            if not azure_endpoint:
                raise ValueError(
                    f"Azure OpenAI endpoint environment variable '{azure_endpoint_config[1:] if azure_endpoint_config.startswith('$') else ''}' not found or is empty."
                )

            api_version_config = model_config.get("api_version")
            if not api_version_config:
                raise ValueError(
                    "Azure OpenAI model type requires 'api_version' in its configuration."
                )
            api_version = api_version_config
            if api_version_config.startswith("$"):
                api_version = os.environ.get(api_version_config[1:])
            if not api_version:
                raise ValueError(
                    f"Azure OpenAI API version environment variable '{api_version_config[1:] if api_version_config.startswith('$') else ''}' not found or is empty."
                )

            api_key_config = model_config.get("api_key")
            if not api_key_config:
                raise ValueError(
                    "Azure OpenAI model type requires 'api_key' in its configuration."
                )
            api_key = api_key_config
            if api_key_config.startswith("$"):
                api_key = os.environ.get(api_key_config[1:])
            if not api_key:
                raise ValueError(
                    f"Azure OpenAI API key environment variable '{api_key_config[1:] if api_key_config.startswith('$') else ''}' not found or is empty."
                )

            # Configure max_retries for the Azure client, defaulting if not specified in config
            azure_max_retries = model_config.get("max_retries", 2)

            azure_client = AsyncAzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                api_key=api_key,
                max_retries=azure_max_retries,
            )
            provider = OpenAIProvider(openai_client=azure_client)
            model = OpenAIModel(model_name=model_config["name"], provider=provider)
            setattr(model, "provider", provider)
            return model

        elif model_type == "custom_openai":
            url, headers, ca_certs_path, api_key = get_custom_config(model_config)
            
            # Log model creation
            from code_puppy.tools.tool_logger import log_tool
            log_tool(
                tool_name="model_factory_custom_openai",
                input_data={"model_name": model_name, "url": url},
                output_data={"api_key_present": bool(api_key), "api_key_start": api_key[:20] if api_key else "NONE"},
                metadata={"headers": headers}
            )
            
            client = httpx.AsyncClient(headers=headers, verify=ca_certs_path)
            provider_args = dict(
                base_url=url,
                http_client=client,
            )
            if api_key:
                provider_args["api_key"] = api_key
            provider = OpenAIProvider(**provider_args)

            model = OpenAIModel(model_name=model_config["name"], provider=provider)
            setattr(model, "provider", provider)
            return model
        elif model_type == "openrouter":
            api_key = None
            if "api_key" in model_config:
                if model_config["api_key"].startswith("$"):
                    api_key = os.environ.get(model_config["api_key"][1:])
                else:
                    api_key = model_config["api_key"]
            provider = OpenRouterProvider(api_key=api_key)
            model_name = model_config.get("name")
            model = OpenAIModel(model_name, provider=provider)
            return model
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
