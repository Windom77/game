"""
Base classes and data structures for LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


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
