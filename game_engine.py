"""
Core game engine for the Victorian Murder Mystery game.
Manages game state, character interactions, and game flow.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from characters import (
    Character, CHARACTERS, get_character, get_all_suspects,
    get_introduction, get_accusation_result, VICTIM
)
from llm_interface import (
    LLMProvider, ConversationHistory, get_provider, detect_best_provider
)
import config


class GameState(Enum):
    """Possible states of the game."""
    NOT_STARTED = "not_started"
    INTRODUCTION = "introduction"
    INVESTIGATING = "investigating"
    ACCUSATION = "accusation"
    GAME_OVER = "game_over"


@dataclass
class GameSession:
    """Represents a single game session."""
    state: GameState = GameState.NOT_STARTED
    start_time: Optional[float] = None
    current_character: Optional[str] = None
    conversations: dict[str, ConversationHistory] = field(default_factory=dict)
    questions_asked: dict[str, int] = field(default_factory=dict)
    clues_discovered: list[str] = field(default_factory=list)
    accusation_made: bool = False
    result: Optional[str] = None

    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds since game start."""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def get_remaining_time(self) -> float:
        """Get remaining time in seconds."""
        elapsed = self.get_elapsed_time()
        total = config.GAME_DURATION_MINUTES * 60
        return max(0, total - elapsed)

    def is_time_up(self) -> bool:
        """Check if game time has expired."""
        return self.get_remaining_time() <= 0


class GameEngine:
    """Main game engine that coordinates all game logic."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """Initialize the game engine."""
        self.session: Optional[GameSession] = None
        self.llm = llm_provider or detect_best_provider()

    def start_new_game(self) -> str:
        """Start a new game session."""
        self.session = GameSession()
        self.session.state = GameState.INTRODUCTION
        self.session.start_time = time.time()

        # Initialize conversation histories for each character
        for char_id, character in CHARACTERS.items():
            self.session.conversations[char_id] = ConversationHistory(
                system_prompt=character.get_system_prompt(),
                max_history=config.MAX_CONVERSATION_HISTORY
            )
            self.session.questions_asked[char_id] = 0

        return get_introduction()

    def get_character_list(self) -> str:
        """Get formatted list of characters for selection."""
        lines = ["\nSUSPECTS:"]
        for i, char in enumerate(get_all_suspects(), 1):
            lines.append(f"  {i}. {char.title} {char.name} - {char.occupation}")
        lines.append("\n  Type a number to select, or 'accuse' to make accusation")
        return "\n".join(lines)

    def select_character(self, selection: str) -> tuple[bool, str]:
        """Select a character to question."""
        if self.session is None or self.session.state != GameState.INVESTIGATING:
            return False, "Game is not in investigation phase."

        selection = selection.strip().lower()

        # Handle accusation command
        if selection == "accuse":
            self.session.state = GameState.ACCUSATION
            return True, self._get_accusation_prompt()

        # Handle number selection
        try:
            idx = int(selection) - 1
            suspects = get_all_suspects()
            if 0 <= idx < len(suspects):
                char = suspects[idx]
                self.session.current_character = char.id
                return True, f"\n{char.title} {char.name} regards you with {'suspicion' if char.is_guilty else 'interest'}.\n\nWhat would you like to ask?"
        except ValueError:
            pass

        # Handle name-based selection
        char_mapping = {
            "major": "major", "blackwood": "major", "1": "major",
            "lady": "lady", "cordelia": "lady", "ashworth": "lady", "2": "lady",
            "maid": "maid", "molly": "maid", "finch": "maid", "3": "maid",
            "student": "student", "thomas": "student", "whitmore": "student", "4": "student",
        }

        for key, char_id in char_mapping.items():
            if key in selection:
                char = get_character(char_id)
                if char:
                    self.session.current_character = char_id
                    return True, f"\n{char.title} {char.name} regards you with {'suspicion' if char.is_guilty else 'interest'}.\n\nWhat would you like to ask?"

        return False, "Invalid selection. Please choose a suspect by number or name."

    def ask_question(self, question: str) -> str:
        """Ask the current character a question."""
        if self.session is None:
            return "No game in progress."

        if self.session.state == GameState.ACCUSATION:
            return self._handle_accusation(question)

        if self.session.current_character is None:
            return "No character selected. Use the character list to select someone to question."

        char_id = self.session.current_character
        character = get_character(char_id)

        if character is None:
            return "Invalid character."

        # Check for back/exit commands
        if question.strip().lower() in ["back", "exit", "done", "leave"]:
            self.session.current_character = None
            return self.get_character_list()

        # Add the question to conversation history
        conversation = self.session.conversations[char_id]
        conversation.add_message("user", f"Detective: {question}")

        # Generate response from LLM
        response = self.llm.generate_response(conversation)

        # Add response to history
        conversation.add_message("assistant", response)
        self.session.questions_asked[char_id] += 1

        # Check for potential clues in response (basic keyword detection)
        self._detect_clues(char_id, question, response)

        return f"\n{character.title} {character.name}:\n\"{response}\"\n"

    def _detect_clues(self, char_id: str, question: str, response: str):
        """Detect and record potential clues from conversation."""
        # This is a simplified clue detection - could be enhanced with NLP
        clue_keywords = {
            "major": ["letter opener", "argument", "debt", "crimea"],
            "lady": ["10:45", "after", "corridor", "shiny", "desperate"],
            "maid": ["saw", "corridor", "10:50", "distressed", "mistress"],
            "student": ["advances", "improper", "confronted", "threatened"],
        }

        combined_text = (question + response).lower()
        for keyword in clue_keywords.get(char_id, []):
            if keyword in combined_text:
                clue = f"{char_id}: mentioned '{keyword}'"
                if clue not in self.session.clues_discovered:
                    self.session.clues_discovered.append(clue)

    def _get_accusation_prompt(self) -> str:
        """Get the accusation selection prompt."""
        lines = [
            "\n" + "="*50,
            "           TIME TO MAKE YOUR ACCUSATION",
            "="*50,
            "\nYou have gathered your evidence. Who committed the murder?",
            ""
        ]
        for i, char in enumerate(get_all_suspects(), 1):
            lines.append(f"  {i}. {char.title} {char.name}")
        lines.append("\nType the number or name of your suspect:")
        return "\n".join(lines)

    def _handle_accusation(self, selection: str) -> str:
        """Handle the player's accusation."""
        if self.session is None:
            return "No game in progress."

        selection = selection.strip().lower()

        # Map selection to character ID
        char_mapping = {
            "1": "major", "major": "major", "blackwood": "major",
            "2": "lady", "lady": "lady", "cordelia": "lady", "ashworth": "lady",
            "3": "maid", "maid": "maid", "molly": "maid", "finch": "maid",
            "4": "student", "student": "student", "thomas": "student", "whitmore": "student",
        }

        accused_id = None
        for key, char_id in char_mapping.items():
            if key in selection:
                accused_id = char_id
                break

        if accused_id is None:
            return "Invalid accusation. Please choose a suspect by number or name."

        self.session.accusation_made = True
        self.session.state = GameState.GAME_OVER
        self.session.result = get_accusation_result(accused_id)

        return self.session.result

    def get_status(self) -> str:
        """Get current game status."""
        if self.session is None:
            return "No game in progress."

        remaining = self.session.get_remaining_time()
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)

        lines = [
            f"\n--- STATUS ---",
            f"Time remaining: {minutes}:{seconds:02d}",
            f"Clues found: {len(self.session.clues_discovered)}",
        ]

        total_questions = sum(self.session.questions_asked.values())
        lines.append(f"Questions asked: {total_questions}")

        if self.session.current_character:
            char = get_character(self.session.current_character)
            if char:
                lines.append(f"Speaking with: {char.title} {char.name}")

        return "\n".join(lines)

    def get_help(self) -> str:
        """Get help text for the player."""
        return """
COMMANDS:
  [1-4]     - Select a suspect to question
  back      - Return to suspect selection
  status    - View game status and clues
  accuse    - Make your accusation (ends the game)
  help      - Show this help text
  quit      - Exit the game

TIPS:
  - Pay attention to alibis and times
  - Look for inconsistencies in stories
  - Ask about other suspects
  - Note who seems nervous or evasive
"""

    def process_input(self, user_input: str) -> str:
        """Process any user input and return appropriate response."""
        if self.session is None:
            return self.start_new_game() + self.get_character_list()

        user_input = user_input.strip().lower()

        # Handle global commands
        if user_input == "help":
            return self.get_help()
        elif user_input == "status":
            return self.get_status()
        elif user_input in ["quit", "exit game", "end"]:
            self.session.state = GameState.GAME_OVER
            return "Thank you for playing! The mystery remains unsolved..."

        # Handle state-specific input
        if self.session.state == GameState.INTRODUCTION:
            self.session.state = GameState.INVESTIGATING
            return self.get_character_list()

        elif self.session.state == GameState.INVESTIGATING:
            if self.session.current_character is None:
                success, message = self.select_character(user_input)
                return message
            else:
                return self.ask_question(user_input)

        elif self.session.state == GameState.ACCUSATION:
            return self._handle_accusation(user_input)

        elif self.session.state == GameState.GAME_OVER:
            return "Game over. Start a new game to play again."

        return "Unknown game state."
