"""
User interface implementations for the Victorian Murder Mystery game.

This module provides three UI options:
- Terminal: Rich text-based terminal UI
- Pygame: 2D graphical UI with portraits
- Panda3D: Full 3D interactive UI
"""

from .terminal import TerminalUI, run_terminal_game
from .pygame_ui import PygameUI, run_pygame_game
from .panda3d_ui import PandaMysteryGame, run_panda3d_game

__all__ = [
    'TerminalUI',
    'PygameUI',
    'PandaMysteryGame',
    'run_terminal_game',
    'run_pygame_game',
    'run_panda3d_game',
]
