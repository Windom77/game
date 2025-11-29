"""
Anthropic Claude API provider.
"""

import os
from .base import LLMProvider, ConversationHistory


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
