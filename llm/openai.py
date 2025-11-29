"""
OpenAI API provider.
"""

import os
from .base import LLMProvider, ConversationHistory


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
