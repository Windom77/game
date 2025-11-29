"""
Terminal-based UI for the Victorian Murder Mystery game.
Uses Rich library for enhanced text formatting when available.
"""

import sys
import time
from typing import Optional

import config


# Try to import Rich for enhanced terminal output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class TerminalUI:
    """Terminal-based user interface for the game."""

    def __init__(self):
        self.width = config.TERMINAL_WIDTH
        self.use_rich = RICH_AVAILABLE and config.USE_COLORS

        if self.use_rich:
            self.console = Console(width=self.width)
        else:
            self.console = None

    def clear_screen(self):
        """Clear the terminal screen."""
        if sys.platform == "win32":
            import os
            os.system("cls")
        else:
            print("\033[H\033[J", end="")

    def print_header(self):
        """Print the game header."""
        if self.use_rich:
            header = Panel(
                "[bold yellow]THE PEMBERTON MANOR MYSTERY[/bold yellow]\n"
                "[dim]A Victorian Murder Mystery[/dim]",
                border_style="yellow",
                padding=(0, 2)
            )
            self.console.print(header)
        else:
            print("=" * self.width)
            print("     THE PEMBERTON MANOR MYSTERY".center(self.width))
            print("       A Victorian Murder Mystery".center(self.width))
            print("=" * self.width)

    def print_scene(self):
        """Print the ASCII art scene of the drawing room."""
        scene = self._get_drawing_room_art()
        if self.use_rich:
            self.console.print(Panel(scene, title="The Drawing Room", border_style="blue"))
        else:
            print("-" * self.width)
            print(scene)
            print("-" * self.width)

    def _get_drawing_room_art(self) -> str:
        """Get ASCII art of the drawing room with characters."""
        return """
             ___________________________
            |   PEMBERTON MANOR         |
            |       LIBRARY             |
            |___________________________|

        [Fireplace]              [Window]
            |||                    ===
            |||                    ===

                    _______
                   |       |
           O   O   | TABLE |   O   O
          /|\ /|\  |_______|  /|\ /|\
          / \ / \             / \ / \

        Major  Lady          Maid  Student
       Blackwood Ashworth    Molly  Thomas

                    YOU
                     O
                    /|\\
                    / \\
                 [Detective]
"""

    def print_text(self, text: str, style: Optional[str] = None):
        """Print text with optional styling."""
        if self.use_rich and style:
            self.console.print(text, style=style)
        else:
            print(text)

    def print_dialogue(self, character_name: str, dialogue: str):
        """Print character dialogue with formatting."""
        if config.TYPING_EFFECT:
            self._type_effect(f"{character_name}: ", bold=True)
            self._type_effect(f'"{dialogue}"')
            print()
        else:
            if self.use_rich:
                self.console.print(f"[bold]{character_name}:[/bold]")
                self.console.print(f'[italic]"{dialogue}"[/italic]')
            else:
                print(f"{character_name}:")
                print(f'"{dialogue}"')

    def _type_effect(self, text: str, bold: bool = False):
        """Simulate typing effect for text output."""
        for char in text:
            if bold and self.use_rich:
                self.console.print(char, end="", style="bold")
            else:
                print(char, end="", flush=True)
            time.sleep(config.TYPING_SPEED)

    def print_character_select(self, characters: list):
        """Print character selection menu."""
        if self.use_rich:
            table = Table(title="Select a Suspect to Question", show_header=True)
            table.add_column("#", style="cyan", width=4)
            table.add_column("Name", style="white")
            table.add_column("Role", style="dim")

            for i, (name, role) in enumerate(characters, 1):
                table.add_row(str(i), name, role)

            self.console.print(table)
        else:
            print("\nSelect a Suspect to Question:")
            print("-" * 40)
            for i, (name, role) in enumerate(characters, 1):
                print(f"  {i}. {name} - {role}")
            print("-" * 40)

    def print_status(self, time_remaining: str, clues_found: int, questions_asked: int):
        """Print game status bar."""
        if self.use_rich:
            status = f"[cyan]Time: {time_remaining}[/cyan] | "
            status += f"[yellow]Clues: {clues_found}[/yellow] | "
            status += f"[green]Questions: {questions_asked}[/green]"
            self.console.print(Panel(status, border_style="dim"))
        else:
            print(f"\n[Time: {time_remaining} | Clues: {clues_found} | Questions: {questions_asked}]")

    def get_input(self, prompt: str = "> ") -> str:
        """Get input from the user."""
        if self.use_rich:
            return self.console.input(f"[bold green]{prompt}[/bold green]")
        else:
            return input(prompt)

    def print_game_output(self, text: str):
        """Print general game output."""
        if self.use_rich:
            # Check for special formatting
            if text.startswith("="):
                self.console.print(Panel(text, border_style="yellow"))
            else:
                self.console.print(text)
        else:
            print(text)

    def print_error(self, message: str):
        """Print an error message."""
        if self.use_rich:
            self.console.print(f"[red]Error: {message}[/red]")
        else:
            print(f"Error: {message}")

    def print_success(self, message: str):
        """Print a success message."""
        if self.use_rich:
            self.console.print(f"[green]{message}[/green]")
        else:
            print(message)

    def print_warning(self, message: str):
        """Print a warning message."""
        if self.use_rich:
            self.console.print(f"[yellow]{message}[/yellow]")
        else:
            print(f"Warning: {message}")

    def print_help(self):
        """Print help information."""
        help_text = """
COMMANDS:
  [1-4]    Select a suspect to question
  back     Return to suspect selection
  status   View game status and clues
  accuse   Make your accusation
  help     Show this help
  quit     Exit the game

TIPS:
  - Pay attention to alibis and times
  - Look for inconsistencies
  - Ask about other suspects
  - Note nervous behavior
"""
        if self.use_rich:
            self.console.print(Panel(help_text, title="Help", border_style="cyan"))
        else:
            print(help_text)


def run_terminal_game():
    """Run the game in terminal mode."""
    from core.engine import GameEngine

    ui = TerminalUI()
    engine = GameEngine()

    ui.clear_screen()
    ui.print_header()

    # Start the game
    intro = engine.start_new_game()
    ui.print_game_output(intro)

    # Show the scene
    ui.print_scene()

    # Main game loop
    while True:
        try:
            user_input = ui.get_input("\n> ").strip()

            if not user_input:
                continue

            if user_input.lower() == "scene":
                ui.print_scene()
                continue

            response = engine.process_input(user_input)
            ui.print_game_output(response)

            # Check for game over
            if engine.session and engine.session.state.value == "game_over":
                ui.print_text("\nThank you for playing The Pemberton Manor Mystery!")
                break

        except KeyboardInterrupt:
            ui.print_text("\n\nGame interrupted. Goodbye!")
            break
        except EOFError:
            break


if __name__ == "__main__":
    run_terminal_game()
