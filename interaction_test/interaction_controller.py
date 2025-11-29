"""
Interaction controller for testing character conversations.
Handles user input, LLM communication, and UI display.
"""
import sys
import os
from typing import Optional

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectEntry, DirectLabel, DirectFrame
from panda3d.core import TextNode

# Add parent directory to path to import llm module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llm import LLMProvider, ConversationHistory
from test_character import Character
from mouth_animation import MouthAnimator


class InteractionController:
    """Handles user input, LLM communication, and dialogue UI."""

    def __init__(self, base: ShowBase, character: Character, llm_provider: LLMProvider,
                 mouth_animator: Optional[MouthAnimator] = None):
        """
        Initialize the interaction controller.

        Args:
            base: The ShowBase instance (Panda3D application)
            character: The character to interact with
            llm_provider: The LLM provider for generating responses
            mouth_animator: Optional mouth animator for character speech animation
        """
        self.base = base
        self.character = character
        self.llm_provider = llm_provider
        self.mouth_animator = mouth_animator

        # Initialize conversation history
        self.conversation = ConversationHistory(
            system_prompt=character.system_prompt,
            max_history=10
        )

        self.is_waiting_for_response = False

        self._setup_ui()
        self._setup_input_handlers()

        print("✓ Interaction controller initialized")
        print(f"  Character: {character.name}")
        print(f"  LLM Provider: {type(llm_provider).__name__}")
        if self.mouth_animator:
            print(f"  Mouth Animation: Enabled ({self.mouth_animator.animation_mode})")

    def _setup_ui(self) -> None:
        """Set up the user interface elements."""
        # Response display area (top portion of screen)
        self.response_label = DirectLabel(
            text=f"Welcome! Ask {self.character.name} anything.\nPress ESC to quit.",
            text_align=TextNode.ALeft,
            text_scale=0.05,
            text_fg=(0.1, 0.1, 0.1, 1.0),
            text_bg=(1.0, 1.0, 1.0, 0.8),
            text_wordwrap=25,
            frameColor=(0.95, 0.95, 0.95, 0.9),
            frameSize=(-1.3, 1.3, -0.5, 0.5),
            pos=(-0.95, 0, 0.3),
        )

        # Status indicator (for "Thinking..." message)
        self.status_label = DirectLabel(
            text="",
            text_scale=0.04,
            text_fg=(0.3, 0.3, 0.7, 1.0),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, -0.6),
        )

        # Input box background frame
        self.input_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.9),
            frameSize=(-1.3, 1.3, -0.08, 0.08),
            pos=(0, 0, -0.85),
        )

        # Text input box (bottom of screen)
        self.input_entry = DirectEntry(
            text="",
            scale=0.05,
            width=50,
            numLines=1,
            focus=1,
            frameColor=(1.0, 1.0, 1.0, 1.0),
            text_fg=(0.0, 0.0, 0.0, 1.0),
            pos=(-1.25, 0, -0.85),
            command=self._on_input_submit,
            focusInCommand=self._on_focus_in,
            focusOutCommand=self._on_focus_out,
        )

        # Prompt label
        self.prompt_label = DirectLabel(
            text="You:",
            text_scale=0.05,
            text_fg=(0.9, 0.9, 0.9, 1.0),
            frameColor=(0, 0, 0, 0),
            pos=(-1.4, 0, -0.85),
        )

        print("✓ UI elements created")

    def _setup_input_handlers(self) -> None:
        """Set up keyboard input handlers."""
        # ESC to quit
        self.base.accept('escape', self._quit_application)

        print("✓ Input handlers configured (ESC to quit)")

    def _on_focus_in(self) -> None:
        """Called when input box gains focus."""
        pass

    def _on_focus_out(self) -> None:
        """Called when input box loses focus."""
        pass

    def _on_input_submit(self, text: str) -> None:
        """
        Called when user submits input (presses Enter).

        Args:
            text: The user's input text
        """
        # Ignore empty input or if already waiting for response
        if not text.strip() or self.is_waiting_for_response:
            return

        user_message = text.strip()

        # Clear input box
        self.input_entry.set("")

        # Update UI to show user message
        self._display_message(f"You: {user_message}\n\nThinking...")

        # Show thinking indicator
        self.status_label['text'] = "Thinking..."

        # Add user message to conversation history
        self.conversation.add_message('user', user_message)

        # Mark as waiting
        self.is_waiting_for_response = True

        # Schedule LLM response generation
        self.base.taskMgr.doMethodLater(
            0.1,
            self._generate_response,
            'generate_llm_response'
        )

    def _generate_response(self, task) -> int:
        """
        Generate LLM response (called asynchronously).

        Args:
            task: Panda3D task object

        Returns:
            Task done status
        """
        try:
            # Generate response from LLM
            response = self.llm_provider.generate_response(self.conversation)

            # Add assistant response to conversation history
            self.conversation.add_message('assistant', response)

            # Start mouth animation when character "speaks"
            if self.mouth_animator:
                self.mouth_animator.start_talking()

            # Display the conversation
            self._display_conversation()

            # Clear status
            self.status_label['text'] = ""

            # Schedule stopping mouth animation after speech duration
            # Estimate based on response length (~0.05s per character)
            if self.mouth_animator:
                speech_duration = max(2.0, len(response) * 0.05)
                self.base.taskMgr.doMethodLater(
                    speech_duration,
                    self._stop_talking,
                    'stop_mouth_animation'
                )

        except Exception as e:
            error_msg = f"[Error: {str(e)}]"
            print(f"Error generating response: {e}")
            self._display_message(error_msg)
            self.status_label['text'] = ""

        finally:
            self.is_waiting_for_response = False

        return task.done

    def _stop_talking(self, task) -> int:
        """
        Stop the mouth animation (called after speech duration).

        Args:
            task: Panda3D task object

        Returns:
            Task done status
        """
        if self.mouth_animator:
            self.mouth_animator.stop_talking()
        return task.done

    def _display_message(self, message: str) -> None:
        """
        Display a message in the response area.

        Args:
            message: The message to display
        """
        self.response_label['text'] = message

    def _display_conversation(self) -> None:
        """Display the recent conversation history."""
        # Get last few exchanges
        messages_to_show = self.conversation.messages[-4:]  # Last 2 exchanges (4 messages)

        display_text = []
        for msg in messages_to_show:
            if msg.role == 'user':
                display_text.append(f"You: {msg.content}")
            elif msg.role == 'assistant':
                display_text.append(f"{self.character.name}: {msg.content}")

        if not display_text:
            display_text = [f"Ask {self.character.name} anything!"]

        self.response_label['text'] = "\n\n".join(display_text)

    def _quit_application(self) -> None:
        """Quit the application."""
        print("\nQuitting...")
        sys.exit(0)
