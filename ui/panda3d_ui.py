#!/usr/bin/env python3
"""
Panda3D 3D UI for The Pemberton Manor Mystery.
Provides immersive first-person 3D experience with game engine integration.
"""
import sys
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import (
    DirectFrame, DirectLabel, DirectButton, DirectScrolledList,
    DGG
)
from panda3d.core import (
    WindowProperties, TextNode, TransparencyAttrib
)

from graphics.scene_3d import Scene3D, CHARACTER_CONFIG
from core.engine import GameEngine, GameState


# Map character IDs to selection numbers
CHAR_NUM_MAP = {
    '1': 'major',
    '2': 'lady',
    '3': 'maid',
    '4': 'student',
}

CHAR_ID_TO_NUM = {v: k for k, v in CHAR_NUM_MAP.items()}


class PandaMysteryGame(ShowBase):
    """Main Panda3D game application."""

    def __init__(self):
        ShowBase.__init__(self)

        # Set window properties
        props = WindowProperties()
        props.setTitle("The Pemberton Manor Mystery - 3D")
        props.setSize(1024, 768)
        self.win.requestProperties(props)

        # Create 3D scene
        self.scene = Scene3D(self)

        # Create game engine
        self.engine = GameEngine()
        intro = self.engine.start_new_game()
        self.engine.session.state = GameState.INVESTIGATING

        # UI state
        self.current_response = ""
        self.show_notebook = False

        # Setup UI
        self._setup_ui()

        # Setup input
        self._setup_input()

        # Update loop
        self.taskMgr.add(self.update, 'update')

        print("✓ Panda3D Mystery Game initialized")
        print("Controls: [1-4] Select character, [N] Notebook, [A] Accuse, [ESC] Quit")

    def _setup_ui(self):
        """Create 2D UI overlay for questions, responses, etc."""
        # Main UI frame (semi-transparent background)
        self.ui_frame = DirectFrame(
            frameColor=(0.1, 0.08, 0.06, 0.85),
            frameSize=(-0.95, 0.95, -0.95, -0.5),
            pos=(0, 0, 0)
        )

        # Character info label (top-left)
        self.char_label = DirectLabel(
            text="Select a suspect [1-4]",
            text_fg=(0.9, 0.85, 0.7, 1),
            text_scale=0.06,
            text_align=TextNode.ALeft,
            pos=(-0.9, 0, 0.9),
            frameColor=(0, 0, 0, 0),
        )

        # Questions remaining (top-right)
        self.question_counter = DirectLabel(
            text="Questions: 15 remaining",
            text_fg=(0.8, 0.7, 0.5, 1),
            text_scale=0.05,
            text_align=TextNode.ARight,
            pos=(0.9, 0, 0.9),
            frameColor=(0, 0, 0, 0),
        )

        # Response display area
        self.response_label = DirectLabel(
            text="",
            text_fg=(0.9, 0.9, 0.85, 1),
            text_scale=0.045,
            text_align=TextNode.ALeft,
            text_wordwrap=40,
            pos=(-0.9, 0, -0.55),
            frameColor=(0, 0, 0, 0),
        )

        # Instructions
        self.instructions = DirectLabel(
            text="[1-4] Character | [Q] Question | [N] Notebook | [A] Accuse | [ESC] Quit",
            text_fg=(0.6, 0.55, 0.45, 1),
            text_scale=0.035,
            pos=(0, 0, -0.92),
            frameColor=(0, 0, 0, 0),
        )

        # Evidence notebook (hidden by default)
        self.notebook_frame = DirectFrame(
            frameColor=(0.15, 0.12, 0.08, 0.95),
            frameSize=(-0.4, 0.4, -0.4, 0.4),
            pos=(0, 0, 0)
        )
        self.notebook_frame.hide()

        self.notebook_title = DirectLabel(
            text="Evidence Notebook",
            text_fg=(0.9, 0.85, 0.7, 1),
            text_scale=0.06,
            pos=(0, 0, 0.32),
            parent=self.notebook_frame,
            frameColor=(0, 0, 0, 0),
        )

        self.notebook_content = DirectLabel(
            text="No clues discovered yet.",
            text_fg=(0.8, 0.8, 0.75, 1),
            text_scale=0.04,
            text_align=TextNode.ALeft,
            text_wordwrap=18,
            pos=(-0.35, 0, 0.2),
            parent=self.notebook_frame,
            frameColor=(0, 0, 0, 0),
        )

        self.notebook_close = DirectButton(
            text="[Close]",
            text_fg=(0.7, 0.6, 0.5, 1),
            text_scale=0.04,
            pos=(0, 0, -0.35),
            parent=self.notebook_frame,
            frameColor=(0.2, 0.15, 0.1, 1),
            command=self.toggle_notebook,
        )

    def _setup_input(self):
        """Set up keyboard input for character/question selection."""
        # Character selection
        self.accept('1', lambda: self.select_character('1'))
        self.accept('2', lambda: self.select_character('2'))
        self.accept('3', lambda: self.select_character('3'))
        self.accept('4', lambda: self.select_character('4'))

        # Actions
        self.accept('n', self.toggle_notebook)
        self.accept('a', self.start_accusation)
        self.accept('q', self.prompt_question)
        self.accept('b', self.go_back)

        # Quit
        self.accept('escape', sys.exit)

    def select_character(self, num: str):
        """Handle character selection."""
        if self.engine.session.state != GameState.INVESTIGATING:
            return

        char_id = CHAR_NUM_MAP.get(num)
        if not char_id:
            return

        # Focus camera on character
        self.scene.focus_character(char_id)

        # Update game engine
        success, msg = self.engine.select_character(num)

        if success:
            char_name = self.scene.get_character_name(char_id)
            self.char_label['text'] = f"Speaking with: {char_name}"
            self.response_label['text'] = f"{char_name} awaits your question.\nPress [Q] to ask a question, [B] to go back."
        else:
            self.response_label['text'] = msg

        self._update_question_counter()

    def prompt_question(self):
        """Prompt user to type a question (simplified - uses predefined questions)."""
        if self.engine.session.current_character is None:
            self.response_label['text'] = "Select a character first [1-4]"
            return

        # For now, ask a generic investigation question
        # In full implementation, would show question menu or text input
        char_id = self.engine.session.current_character
        char_name = self.scene.get_character_name(char_id)

        # Ask about alibi (common question)
        response = self.engine.ask_question("Where were you at the time of the murder?")
        self.response_label['text'] = response[:500]  # Truncate for display
        self._update_question_counter()
        self._update_notebook()

    def go_back(self):
        """Go back to character selection."""
        if self.engine.session.current_character:
            self.engine.session.current_character = None
            self.scene.reset_camera()
            self.char_label['text'] = "Select a suspect [1-4]"
            self.response_label['text'] = ""

    def toggle_notebook(self):
        """Toggle evidence notebook display."""
        self.show_notebook = not self.show_notebook
        if self.show_notebook:
            self._update_notebook()
            self.notebook_frame.show()
        else:
            self.notebook_frame.hide()

    def _update_notebook(self):
        """Update notebook content with discovered clues."""
        clues = self.engine.session.clues_discovered
        if clues:
            self.notebook_content['text'] = "\n".join(f"- {c}" for c in clues)
        else:
            self.notebook_content['text'] = "No clues discovered yet."

    def _update_question_counter(self):
        """Update the question counter display."""
        total = sum(self.engine.session.questions_asked.values())
        remaining = 15 - total
        self.question_counter['text'] = f"Questions: {remaining} remaining"

    def start_accusation(self):
        """Start the accusation phase."""
        if self.engine.session.state != GameState.INVESTIGATING:
            return

        success, msg = self.engine.select_character("accuse")
        if success:
            self.char_label['text'] = "ACCUSATION PHASE"
            self.response_label['text'] = msg
            self.scene.reset_camera()

    def update(self, task):
        """Main update loop."""
        # Check for game over conditions
        if self.engine.session and self.engine.session.state == GameState.GAME_OVER:
            if self.engine.session.result:
                self.response_label['text'] = self.engine.session.result

        return task.cont


def run_panda3d_game():
    """Entry point for Panda3D game."""
    app = PandaMysteryGame()
    app.run()


if __name__ == '__main__':
    run_panda3d_game()
