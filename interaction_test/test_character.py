"""
Simple test character definition for interaction testing.
"""
from dataclasses import dataclass


@dataclass
class Character:
    """Simple character for testing LLM interactions."""
    name: str
    system_prompt: str


def get_test_character() -> Character:
    """
    Returns a simple test character with a friendly teacher persona.

    Returns:
        Character instance configured for testing
    """
    return Character(
        name="Teacher",
        system_prompt=(
            "You are a friendly teacher who answers questions clearly and helpfully. "
            "Keep responses concise (2-3 sentences maximum). "
            "Be warm, encouraging, and educational in your tone."
        )
    )
