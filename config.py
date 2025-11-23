"""
Configuration settings for the Victorian Murder Mystery game.
"""

# LLM Settings
DEFAULT_LLM_PROVIDER = "mock"  # Options: mock, ollama, openai, groq, anthropic
OLLAMA_MODEL = "mistral"  # For local LLM
OPENAI_MODEL = "gpt-3.5-turbo"  # For OpenAI
GROQ_MODEL = "llama2-70b-4096"  # For Groq
ANTHROPIC_MODEL = "claude-3-haiku-20240307"  # For Anthropic

# Game Settings
GAME_DURATION_MINUTES = 5
MAX_CONVERSATION_HISTORY = 10  # Exchanges to remember per character
ALLOW_MULTIPLE_ACCUSATIONS = False  # Allow retry after wrong accusation

# UI Settings
DEFAULT_UI = "terminal"  # Options: terminal, pygame
TERMINAL_WIDTH = 70
USE_COLORS = True
TYPING_EFFECT = True  # Simulate typing for NPC responses
TYPING_SPEED = 0.02  # Seconds per character

# Pygame Settings (if using graphical UI)
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 30

# Debug Settings
DEBUG_MODE = False
SHOW_CHARACTER_SECRETS = False  # Reveal secrets in debug mode
