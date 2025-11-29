"""
Ollama local LLM provider.
"""

from .base import LLMProvider, ConversationHistory


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
