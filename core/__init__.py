"""
Core game logic for the Victorian Murder Mystery game.

This module contains the game engine, character definitions, clues, and questions.
"""

from .engine import GameEngine, GameState
from .characters import (
    Character, CHARACTERS, get_character, get_all_suspects,
    get_introduction, get_accusation_result, VICTIM
)
from .clues import Clue
from .questions import Question

__all__ = [
    'GameEngine',
    'GameState',
    'Character',
    'CHARACTERS',
    'get_character',
    'get_all_suspects',
    'get_introduction',
    'get_accusation_result',
    'VICTIM',
    'Clue',
    'Question',
]
