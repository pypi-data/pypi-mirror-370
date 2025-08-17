from typing import Optional

from .base import BaseLLMClient
from .llamacpp import LLMClient as LlamaCppLLMClient
from .ollama import LLMClient as OllamaLLMClient
from .openai import LLMClient as OpenAILLMClient
from .openrouter import LLMClient as OpenRouterLLMClient
from .token_tracker import TokenUsage, TokenUsageTracker, get_token_tracker, record_token_usage

__all__ = [
    "BaseLLMClient",
    "LlamaCppLLMClient",
    "OpenRouterLLMClient",
    "OllamaLLMClient",
    "OpenAILLMClient",
    "get_llm_client",
    "get_llm_client_instructor",
    "get_token_tracker",
    "record_token_usage",
    "TokenUsage",
    "TokenUsageTracker",
]

#############################
# Common LLM helper functions
#############################


def get_llm_client(
    provider: str = "openai",
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    instructor: bool = False,
    chat_model: Optional[str] = None,
    vision_model: Optional[str] = None,
    **kwargs,
):
    """
    Get an LLM client instance based on the specified provider.

    Args:
        provider: LLM provider to use ("openrouter", "openai", "ollama", "llamacpp")
        base_url: Base URL for API (used by openai and ollama providers)
        api_key: API key for authentication (used by openai and openrouter providers)
        instructor: Whether to enable instructor for structured output
        chat_model: Model to use for chat completions
        vision_model: Model to use for vision tasks
        **kwargs: Additional provider-specific arguments:
            - llamacpp: model_path, n_ctx, n_gpu_layers, etc.
            - others: depends on provider

    Returns:
        LLMClient instance for the specified provider

    Raises:
        ValueError: If provider is not supported
    """
    if provider == "openrouter":
        return OpenRouterLLMClient(
            base_url=base_url,
            api_key=api_key,
            instructor=instructor,
            chat_model=chat_model,
            vision_model=vision_model,
            **kwargs,
        )
    elif provider == "openai":
        return OpenAILLMClient(
            base_url=base_url,
            api_key=api_key,
            instructor=instructor,
            chat_model=chat_model,
            vision_model=vision_model,
            **kwargs,
        )
    elif provider == "ollama":
        return OllamaLLMClient(
            base_url=base_url,
            api_key=api_key,
            instructor=instructor,
            chat_model=chat_model,
            vision_model=vision_model,
            **kwargs,
        )
    elif provider == "llamacpp":
        return LlamaCppLLMClient(
            instructor=instructor,
            chat_model=chat_model,
            vision_model=vision_model,
            **kwargs,
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported providers: openrouter, openai, ollama, llamacpp")


def get_llm_client_instructor(
    provider: str = "openai",
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    chat_model: Optional[str] = None,
    vision_model: Optional[str] = None,
    **kwargs,
):
    """
    Get an LLM client instance with instructor support based on the specified provider.

    Args:
        provider: LLM provider to use ("openrouter", "openai", "ollama", "llamacpp")
        base_url: Base URL for API (used by openai and ollama providers)
        api_key: API key for authentication (used by openai and openrouter providers)
        chat_model: Model to use for chat completions
        vision_model: Model to use for vision tasks
        **kwargs: Additional provider-specific arguments:
            - llamacpp: model_path, n_ctx, n_gpu_layers, etc.
            - others: depends on provider

    Returns:
        LLMClient instance with instructor enabled for the specified provider

    Raises:
        ValueError: If provider is not supported
    """
    return get_llm_client(
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        instructor=True,
        chat_model=chat_model,
        vision_model=vision_model,
        **kwargs,
    )
