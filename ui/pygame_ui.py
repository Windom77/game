"""
Pygame-based graphical UI for the Victorian Murder Mystery game.
Provides a visual representation of the drawing room with character portraits.
"""

import sys
from typing import Optional, Callable
from dataclasses import dataclass

# Pygame import with fallback
try:
    import pygame
    from pygame import Surface, Rect
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Pygame not installed. Install with: pip install pygame")

import config


class CharacterAnimationState:
    """Tracks character zoom animation state for Phase 1.5 focus effects."""

    def __init__(self):
        self.focused_char = None
        self.animation_progress = 1.0  # 0.0 = starting, 1.0 = complete
        self.animation_duration = 0.6  # seconds
        self.animation_start_time = 0

    def start_focus(self, character_id):
        """Start focusing on a character (or None for neutral)."""
        import time
        if character_id != self.focused_char:
            self.focused_char = character_id
            self.animation_progress = 0.0
            self.animation_start_time = time.time()

    def update(self):
        """Update animation progress. Call each frame."""
        if self.animation_progress >= 1.0:
            return

        import time
        elapsed = time.time() - self.animation_start_time
        self.animation_progress = min(1.0, elapsed / self.animation_duration)

    def get_eased_progress(self):
        """Get eased animation progress (ease-in-out quadratic)."""
        t = self.animation_progress
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - pow(-2 * t + 2, 2) / 2


@dataclass
class CharacterSprite:
    """Represents a character's visual representation."""
    name: str
    position: tuple[int, int]
    color: tuple[int, int, int]
    is_selected: bool = False


class PygameUI:
    """Pygame-based graphical user interface."""

    # Color definitions
    COLORS = {
        'background': (45, 35, 25),      # Dark wood
        'wall': (80, 65, 50),            # Wall color
        'table': (60, 45, 30),           # Table wood
        'text': (255, 248, 220),         # Cream text
        'text_dim': (180, 170, 150),     # Dimmed text
        'highlight': (255, 215, 0),      # Gold highlight
        'input_bg': (30, 25, 20),        # Input background
        'major': (139, 69, 19),          # Brown for Major
        'lady': (128, 0, 128),           # Purple for Lady
        'maid': (100, 149, 237),         # Cornflower blue for Maid
        'student': (46, 139, 87),        # Sea green for Student
        'detective': (70, 70, 70),       # Gray for detective
    }

    def __init__(self, width: int = None, height: int = None):
        if not PYGAME_AVAILABLE:
            raise ImportError("Pygame is not installed")

        self.width = width or config.SCREEN_WIDTH
        self.height = height or config.SCREEN_HEIGHT

        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("The Pemberton Manor Mystery")

        # Load fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Character positions (around the table)
        self.characters = {
            'major': CharacterSprite('Major Blackwood', (200, 280), self.COLORS['major']),
            'lady': CharacterSprite('Lady Ashworth', (350, 250), self.COLORS['lady']),
            'maid': CharacterSprite('Miss Finch', (650, 250), self.COLORS['maid']),
            'student': CharacterSprite('Mr. Whitmore', (800, 280), self.COLORS['student']),
        }

        # UI state
        self.input_text = ""
        self.dialogue_text = ""
        self.current_speaker = None
        self.game_messages: list[str] = []
        self.selected_character: Optional[str] = None
        self.clock = pygame.time.Clock()

        # Phase 1.5: Animation state for focus effects
        self.anim_state = CharacterAnimationState()

    def draw_background(self):
        """Draw the drawing room background."""
        self.screen.fill(self.COLORS['background'])

        # Draw walls
        pygame.draw.rect(self.screen, self.COLORS['wall'], (0, 0, self.width, 200))

        # Draw window
        pygame.draw.rect(self.screen, (50, 50, 80), (self.width - 200, 30, 150, 120))
        pygame.draw.rect(self.screen, (200, 200, 220), (self.width - 195, 35, 140, 110))
        # Window cross
        pygame.draw.line(self.screen, (60, 50, 40), (self.width - 125, 35), (self.width - 125, 145), 3)
        pygame.draw.line(self.screen, (60, 50, 40), (self.width - 195, 90), (self.width - 55, 90), 3)

        # Draw fireplace
        pygame.draw.rect(self.screen, (40, 30, 20), (50, 50, 120, 130))
        pygame.draw.rect(self.screen, (20, 15, 10), (60, 100, 100, 80))
        # Fire
        pygame.draw.polygon(self.screen, (255, 100, 0),
                           [(80, 175), (110, 120), (140, 175)])
        pygame.draw.polygon(self.screen, (255, 200, 0),
                           [(90, 175), (110, 140), (130, 175)])

        # Draw floor
        pygame.draw.rect(self.screen, (60, 50, 40), (0, 200, self.width, self.height - 200))

    def draw_table(self):
        """Draw the central table."""
        table_rect = (350, 300, 300, 150)
        pygame.draw.ellipse(self.screen, self.COLORS['table'], table_rect)
        pygame.draw.ellipse(self.screen, (40, 30, 20), table_rect, 3)

        # Table label
        text = self.font_small.render("Investigation Table", True, self.COLORS['text_dim'])
        self.screen.blit(text, (420, 365))

    def draw_character(self, char_id: str, sprite: CharacterSprite):
        """Draw a character sprite with Phase 1.5 focus animation."""
        base_x, base_y = sprite.position

        # Phase 1.5: Calculate animated position and scale
        progress = self.anim_state.get_eased_progress()
        focused = self.anim_state.focused_char

        if focused == char_id:
            # Focused: move toward center, enlarge
            target_x = self.width // 2
            target_y = 280
            target_scale = 1.4
            opacity = 255
        elif focused is not None:
            # Unfocused: push to sides, shrink, dim
            if base_x < self.width // 2:
                target_x = 100
            else:
                target_x = self.width - 100
            target_y = base_y + 50
            target_scale = 0.7
            opacity = 128
        else:
            # Neutral: base positions
            target_x = base_x
            target_y = base_y
            target_scale = 1.0
            opacity = 255

        # Interpolate between base and target
        x = int(base_x + (target_x - base_x) * progress)
        y = int(base_y + (target_y - base_y) * progress)
        scale = 1.0 + (target_scale - 1.0) * progress
        current_opacity = int(255 + (opacity - 255) * progress)

        # Scale factors for drawing
        head_radius = int(20 * scale)
        body_w = int(40 * scale)
        body_h = int(50 * scale)

        # Draw selection highlight
        if char_id == self.selected_character:
            pygame.draw.circle(self.screen, self.COLORS['highlight'], (x, y - int(20 * scale)), int(55 * scale), 3)

        # Create a surface for the character to apply opacity
        char_surface = pygame.Surface((int(120 * scale), int(150 * scale)), pygame.SRCALPHA)
        cx, cy = char_surface.get_width() // 2, int(60 * scale)

        # Draw body on character surface
        # Head
        head_color = (255, 220, 185, current_opacity)
        pygame.draw.circle(char_surface, head_color, (cx, cy - int(40 * scale)), head_radius)
        # Body
        body_color = (*sprite.color, current_opacity)
        pygame.draw.rect(char_surface, body_color, (cx - body_w // 2, cy - int(20 * scale), body_w, body_h))
        # Arms
        pygame.draw.line(char_surface, body_color, (cx - body_w // 2, cy - int(10 * scale)),
                        (cx - int(35 * scale), cy + int(20 * scale)), max(3, int(5 * scale)))
        pygame.draw.line(char_surface, body_color, (cx + body_w // 2, cy - int(10 * scale)),
                        (cx + int(35 * scale), cy + int(20 * scale)), max(3, int(5 * scale)))

        # Blit character surface
        self.screen.blit(char_surface, (x - char_surface.get_width() // 2, y - int(60 * scale)))

        # Name label
        text = self.font_small.render(sprite.name, True, self.COLORS['text'])
        text_rect = text.get_rect(center=(x, y + int(50 * scale)))
        self.screen.blit(text, text_rect)

        # Number for selection
        char_nums = {'major': '1', 'lady': '2', 'maid': '3', 'student': '4'}
        num_text = self.font_medium.render(f"[{char_nums[char_id]}]", True, self.COLORS['highlight'])
        self.screen.blit(num_text, (x - 15, y + int(70 * scale)))

    def draw_detective(self):
        """Draw the detective (player) figure."""
        x, y = self.width // 2, 550

        # Draw body
        pygame.draw.circle(self.screen, (255, 220, 185), (x, y - 40), 25)
        pygame.draw.rect(self.screen, self.COLORS['detective'], (x - 25, y - 15, 50, 60))

        # Hat
        pygame.draw.rect(self.screen, (30, 30, 30), (x - 20, y - 65, 40, 10))

        # Label
        text = self.font_medium.render("DETECTIVE (You)", True, self.COLORS['highlight'])
        text_rect = text.get_rect(center=(x, y + 55))
        self.screen.blit(text, text_rect)

    def draw_dialogue_box(self):
        """Draw the dialogue/output box."""
        box_rect = (20, self.height - 200, self.width - 40, 120)
        pygame.draw.rect(self.screen, self.COLORS['input_bg'], box_rect)
        pygame.draw.rect(self.screen, self.COLORS['text_dim'], box_rect, 2)

        if self.current_speaker:
            speaker_text = self.font_medium.render(f"{self.current_speaker}:", True, self.COLORS['highlight'])
            self.screen.blit(speaker_text, (30, self.height - 195))

        if self.dialogue_text:
            # Word wrap the dialogue
            words = self.dialogue_text.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if self.font_small.size(test_line)[0] < self.width - 80:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            for i, line in enumerate(lines[:4]):  # Max 4 lines
                text = self.font_small.render(line, True, self.COLORS['text'])
                self.screen.blit(text, (30, self.height - 165 + i * 25))

    def draw_input_box(self):
        """Draw the text input box."""
        box_rect = (20, self.height - 70, self.width - 40, 50)
        pygame.draw.rect(self.screen, self.COLORS['input_bg'], box_rect)
        pygame.draw.rect(self.screen, self.COLORS['highlight'], box_rect, 2)

        # Prompt
        prompt = self.font_small.render("> ", True, self.COLORS['highlight'])
        self.screen.blit(prompt, (30, self.height - 55))

        # Input text
        input_surface = self.font_medium.render(self.input_text + "_", True, self.COLORS['text'])
        self.screen.blit(input_surface, (50, self.height - 58))

    def draw_title(self):
        """Draw the game title."""
        title = self.font_large.render("THE PEMBERTON MANOR MYSTERY", True, self.COLORS['highlight'])
        title_rect = title.get_rect(center=(self.width // 2, 25))
        self.screen.blit(title, title_rect)

    def draw_instructions(self):
        """Draw instruction text."""
        instructions = [
            "Press 1-4 to select a suspect | Type your question | Enter to send | ESC to quit"
        ]
        for i, line in enumerate(instructions):
            text = self.font_small.render(line, True, self.COLORS['text_dim'])
            text_rect = text.get_rect(center=(self.width // 2, 480 + i * 20))
            self.screen.blit(text, text_rect)

    def render(self):
        """Render the complete scene."""
        # Phase 1.5: Update animation state each frame
        self.anim_state.update()

        self.draw_background()
        self.draw_table()

        # Draw characters
        for char_id, sprite in self.characters.items():
            self.draw_character(char_id, sprite)

        self.draw_detective()
        self.draw_title()
        self.draw_instructions()
        self.draw_dialogue_box()
        self.draw_input_box()

        pygame.display.flip()

    def set_dialogue(self, speaker: str, text: str):
        """Set the current dialogue text."""
        self.current_speaker = speaker
        self.dialogue_text = text

    def set_selected_character(self, char_id: Optional[str]):
        """Set which character is currently selected."""
        self.selected_character = char_id
        # Phase 1.5: Start focus animation
        self.anim_state.start_focus(char_id)

    def handle_events(self) -> tuple[bool, Optional[str]]:
        """
        Handle pygame events.
        Returns (running, input_text) where input_text is None unless Enter was pressed.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False, None
                elif event.key == pygame.K_RETURN:
                    result = self.input_text
                    self.input_text = ""
                    return True, result
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    if event.unicode.isprintable():
                        self.input_text += event.unicode

        return True, None

    def run_game_loop(self, process_input: Callable[[str], str]):
        """
        Main game loop for pygame UI.

        Args:
            process_input: Function that takes user input and returns game response
        """
        running = True

        # Initial game setup
        intro_response = process_input("start")
        self.set_dialogue("Game", "Welcome to Pemberton Manor. Select a suspect (1-4) to begin questioning.")

        while running:
            running, user_input = self.handle_events()

            if user_input is not None and user_input.strip():
                response = process_input(user_input)

                # Parse response for speaker/dialogue
                if ":" in response and '"' in response:
                    parts = response.split(":", 1)
                    speaker = parts[0].strip()
                    dialogue = parts[1].strip().strip('"')
                    self.set_dialogue(speaker, dialogue)
                else:
                    self.set_dialogue("System", response[:200])

                # Update selected character based on input
                char_map = {'1': 'major', '2': 'lady', '3': 'maid', '4': 'student'}
                if user_input.strip() in char_map:
                    self.set_selected_character(char_map[user_input.strip()])

            self.render()
            self.clock.tick(config.FPS)

        pygame.quit()


def run_pygame_game():
    """Run the game with Pygame UI."""
    if not PYGAME_AVAILABLE:
        print("Pygame is not installed. Please install with: pip install pygame")
        print("Falling back to terminal UI...")
        from ui.terminal import run_terminal_game
        run_terminal_game()
        return

    from core.engine import GameEngine

    engine = GameEngine()
    ui = PygameUI()

    def process_input(user_input: str) -> str:
        if user_input == "start":
            return engine.start_new_game()
        return engine.process_input(user_input)

    ui.run_game_loop(process_input)


if __name__ == "__main__":
    run_pygame_game()
