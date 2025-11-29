"""
LLM provider abstraction for the Victorian Murder Mystery game.

This module provides a unified interface for multiple LLM providers including
Ollama (local), OpenAI, Anthropic Claude, Groq, and a mock provider for testing.
"""

from .base import LLMProvider, ConversationHistory, Message
from .mock import MockLLMProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .groq import GroqProvider
from .anthropic import AnthropicProvider

__all__ = [
    'LLMProvider',
    'ConversationHistory',
    'Message',
    'MockLLMProvider',
    'OllamaProvider',
    'OpenAIProvider',
    'GroqProvider',
    'AnthropicProvider',
    'get_provider',
    'detect_best_provider',
]


def get_provider(provider_name: str = "mock") -> LLMProvider:
    """Factory function to get an LLM provider by name."""
    providers = {
        "mock": MockLLMProvider,
        "ollama": OllamaProvider,
        "openai": OpenAIProvider,
        "groq": GroqProvider,
        "anthropic": AnthropicProvider,
    }

    if provider_name not in providers:
        print(f"Unknown provider '{provider_name}', falling back to mock")
        provider_name = "mock"

    provider = providers[provider_name]()

    if not provider.is_available():
        print(f"Provider '{provider_name}' not available, falling back to mock")
        return MockLLMProvider()

    return provider


def detect_best_provider() -> LLMProvider:
    """Automatically detect and return the best available provider."""
    # Priority: Ollama (free, local) > Groq (free tier) > OpenAI > Anthropic > Mock
    providers_to_try = [
        ("ollama", OllamaProvider),
        ("groq", GroqProvider),
        ("openai", OpenAIProvider),
        ("anthropic", AnthropicProvider),
    ]

    for name, provider_class in providers_to_try:
        provider = provider_class()
        if provider.is_available():
            print(f"Using LLM provider: {name}")
            return provider

    print("No LLM providers available, using mock responses")
    return MockLLMProvider()
