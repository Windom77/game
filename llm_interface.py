"""
LLM Interface abstraction for the Murder Mystery game.
Supports multiple LLM providers: Ollama (local), OpenAI, Anthropic, Groq.
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class Message:
    """Represents a conversation message."""
    role: str  # 'system', 'user', or 'assistant'
    content: str


@dataclass
class ConversationHistory:
    """Maintains conversation history for a character."""
    system_prompt: str
    messages: list[Message] = field(default_factory=list)
    max_history: int = 10  # Keep last N exchanges to manage context

    def add_message(self, role: str, content: str):
        """Add a message to the history."""
        self.messages.append(Message(role=role, content=content))
        # Trim history if too long (keep system prompt separate)
        if len(self.messages) > self.max_history * 2:
            self.messages = self.messages[-(self.max_history * 2):]

    def get_messages_for_api(self) -> list[dict]:
        """Format messages for API calls."""
        result = [{"role": "system", "content": self.system_prompt}]
        for msg in self.messages:
            result.append({"role": msg.role, "content": msg.content})
        return result


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_response(self, conversation: ConversationHistory) -> str:
        """Generate a response given the conversation history."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available (API key set, service running, etc.)."""
        pass


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing without an actual LLM."""

    def __init__(self):
        self.response_templates = {
            "major": [
                "I say, that's a rather pointed question, Inspector. *tugs at collar* I was in the smoking room, dash it all.",
                "By Jove, I resent the implication! I am a man of honour, sir. My service record speaks for itself.",
                "The letter opener? Yes, it was mine. A memento from Crimea. But I did not use it for... that.",
            ],
            "lady": [
                "Inspector, I find your line of questioning most improper. A lady of my standing...",
                "Lord Pemberton and I had a business arrangement. Nothing more. These insinuations are beneath you.",
                "I retired to my chambers at a reasonable hour. Surely you don't expect me to account for every moment?",
            ],
            "maid": [
                "Begging your pardon, sir, but I don't rightly know what you mean. I was with her Ladyship, I was.",
                "I... I shouldn't say, sir. It's not my place to speak ill of my betters.",
                "Thomas - Mr. Whitmore, I mean - he's a good man, sir. He wouldn't hurt no one.",
            ],
            "student": [
                "In principle, Inspector, one must consider the facts dispassionately. Though I admit this situation is most distressing.",
                "I am a student of law, sir. I understand the gravity of these proceedings. I have nothing to hide.",
                "Lord Pemberton was not... shall we say... the most honourable of men. But that is hardly evidence of anything.",
            ],
        }
        self.response_index = {"major": 0, "lady": 0, "maid": 0, "student": 0}

    def generate_response(self, conversation: ConversationHistory) -> str:
        """Return a pre-written response based on character."""
        # Detect character from system prompt
        character_id = None
        for cid in self.response_templates.keys():
            if cid in conversation.system_prompt.lower():
                character_id = cid
                break

        if character_id is None:
            return "I... I'm not sure what to say, Inspector."

        responses = self.response_templates[character_id]
        idx = self.response_index[character_id] % len(responses)
        self.response_index[character_id] += 1
        return responses[idx]

    def is_available(self) -> bool:
        return True


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    def __init__(self, model: str = "mistral", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def generate_response(self, conversation: ConversationHistory) -> str:
        """Generate response using Ollama."""
        try:
            import requests

            messages = conversation.get_messages_for_api()

            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"[Ollama error: {response.status_code}]"

        except ImportError:
            return "[Error: 'requests' library not installed]"
        except Exception as e:
            return f"[Error communicating with Ollama: {e}]"

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            import requests
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")

    def generate_response(self, conversation: ConversationHistory) -> str:
        """Generate response using OpenAI API."""
        if not self.api_key:
            return "[Error: OPENAI_API_KEY not set]"

        try:
            import requests

            messages = conversation.get_messages_for_api()

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.8,
                    "max_tokens": 200
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"[OpenAI error: {response.status_code}]"

        except ImportError:
            return "[Error: 'requests' library not installed]"
        except Exception as e:
            return f"[Error communicating with OpenAI: {e}]"

    def is_available(self) -> bool:
        return bool(self.api_key)


class GroqProvider(LLMProvider):
    """Groq API provider (fast inference, free tier available)."""

    def __init__(self, model: str = "llama2-70b-4096"):
        self.model = model
        self.api_key = os.getenv("GROQ_API_KEY")

    def generate_response(self, conversation: ConversationHistory) -> str:
        """Generate response using Groq API."""
        if not self.api_key:
            return "[Error: GROQ_API_KEY not set]"

        try:
            import requests

            messages = conversation.get_messages_for_api()

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.8,
                    "max_tokens": 200
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"[Groq error: {response.status_code}]"

        except ImportError:
            return "[Error: 'requests' library not installed]"
        except Exception as e:
            return f"[Error communicating with Groq: {e}]"

    def is_available(self) -> bool:
        return bool(self.api_key)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

    def generate_response(self, conversation: ConversationHistory) -> str:
        """Generate response using Anthropic API."""
        if not self.api_key:
            return "[Error: ANTHROPIC_API_KEY not set]"

        try:
            import requests

            # Anthropic uses a different message format
            messages = []
            for msg in conversation.messages:
                messages.append({"role": msg.role, "content": msg.content})

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": 200,
                    "system": conversation.system_prompt,
                    "messages": messages
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["content"][0]["text"]
            else:
                return f"[Anthropic error: {response.status_code}]"

        except ImportError:
            return "[Error: 'requests' library not installed]"
        except Exception as e:
            return f"[Error communicating with Anthropic: {e}]"

    def is_available(self) -> bool:
        return bool(self.api_key)


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
