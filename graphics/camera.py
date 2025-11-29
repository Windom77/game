"""
Graphics module for the Victorian Murder Mystery game.
Phase 1.5: Camera/POV system with character portrait display.

Handles:
- Character portrait loading and display
- Camera transitions between wide view and focus view
- Scene composition and layering
- Stylized Victorian silhouette placeholders when images unavailable
"""

import os
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

try:
    import pygame
    from pygame import Surface
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    # Define Surface as a placeholder type for type hints when pygame isn't available
    Surface = object

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import speaking effects module
try:
    from speaking_effects import SpeakingEffects, create_effects
    SPEAKING_EFFECTS_AVAILABLE = True
except ImportError:
    SPEAKING_EFFECTS_AVAILABLE = False


def check_for_custom_assets(base_path: str) -> dict[str, bool]:
    """
    Check if custom portrait images exist.
    Returns dict of character_id -> exists status.

    To use custom portraits, place images in:
      assets/portraits/major.jpg
      assets/portraits/lady.jpg
      assets/portraits/clara.jpg
      assets/portraits/thomas.jpg
      assets/backgrounds/drawing_room.jpg
    """
    results = {}
    portraits_dir = os.path.join(base_path, "assets", "portraits")
    backgrounds_dir = os.path.join(base_path, "assets", "backgrounds")

    # Check portraits
    for char_id in ["major", "lady", "clara", "thomas"]:
        filepath = os.path.join(portraits_dir, f"{char_id}.jpg")
        results[char_id] = os.path.exists(filepath)

    # Check background
    bg_filepath = os.path.join(backgrounds_dir, "drawing_room.jpg")
    results["background"] = os.path.exists(bg_filepath)

    return results


class CameraView(Enum):
    """Camera view states."""
    WIDE = "wide"           # All characters visible at table
    FOCUS = "focus"         # Single character portrait fills frame
    TRANSITION = "transition"  # Animating between views


@dataclass
class PortraitConfig:
    """Configuration for a character portrait."""
    character_id: str
    name: str
    image_path: str
    # Position in wide view (x, y as percentages of screen)
    wide_pos: Tuple[float, float]
    # Size in wide view (width, height as percentages)
    wide_size: Tuple[float, float]
    # Color for placeholder if image not found
    placeholder_color: Tuple[int, int, int]


# Portrait configurations for each character
PORTRAIT_CONFIGS = {
    "major": PortraitConfig(
        character_id="major",
        name="Major Thornton",
        image_path="assets/portraits/major.jpg",
        wide_pos=(0.12, 0.25),
        wide_size=(0.18, 0.35),
        placeholder_color=(139, 90, 43)
    ),
    "lady": PortraitConfig(
        character_id="lady",
        name="Lady Ashworth",
        image_path="assets/portraits/lady.jpg",
        wide_pos=(0.32, 0.22),
        wide_size=(0.18, 0.35),
        placeholder_color=(148, 87, 166)
    ),
    "maid": PortraitConfig(
        character_id="maid",
        name="Clara Finch",
        image_path="assets/portraits/clara.jpg",
        wide_pos=(0.52, 0.22),
        wide_size=(0.18, 0.35),
        placeholder_color=(100, 149, 200)
    ),
    "student": PortraitConfig(
        character_id="student",
        name="Thomas Whitmore",
        image_path="assets/portraits/thomas.jpg",
        wide_pos=(0.72, 0.25),
        wide_size=(0.18, 0.35),
        placeholder_color=(76, 153, 100)
    ),
}


class CameraSystem:
    """Manages camera views and transitions for the game."""

    def __init__(self, screen_width: int, screen_height: int,
                 speaking_effect_style: str = "default"):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_view = CameraView.WIDE
        self.focused_character: Optional[str] = None
        self.transition_progress = 0.0
        self.transition_speed = 0.08  # Per frame
        self.previous_focused: Optional[str] = None

        # Loaded portrait surfaces
        self.portraits: dict[str, Surface] = {}
        self.background: Optional[Surface] = None

        # Speaking animation effects
        self.speaking_effects: Optional[SpeakingEffects] = None
        self.speaking_character: Optional[str] = None
        if SPEAKING_EFFECTS_AVAILABLE:
            self.speaking_effects = create_effects(speaking_effect_style)

        # Load assets
        self._load_assets()

    def _load_assets(self):
        """Load all portrait images and background."""
        if not PYGAME_AVAILABLE:
            return

        base_path = os.path.dirname(os.path.abspath(__file__))

        # Check what custom assets are available
        available = check_for_custom_assets(base_path)

        # Load background
        bg_path = os.path.join(base_path, "assets/backgrounds/drawing_room.jpg")
        if os.path.exists(bg_path):
            try:
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(
                    self.background, (self.screen_width, self.screen_height)
                )
            except Exception:
                self.background = None

        # Load character portraits
        for char_id, config in PORTRAIT_CONFIGS.items():
            img_path = os.path.join(base_path, config.image_path)
            if os.path.exists(img_path):
                try:
                    portrait = pygame.image.load(img_path)
                    self.portraits[char_id] = portrait
                except Exception:
                    self.portraits[char_id] = self._create_placeholder(config)
            else:
                self.portraits[char_id] = self._create_placeholder(config)

    def _create_placeholder(self, config: PortraitConfig) -> Surface:
        """Create a stylized Victorian portrait placeholder."""
        width = int(self.screen_width * 0.25)
        height = int(self.screen_height * 0.45)

        surface = pygame.Surface((width, height))

        # Victorian sepia-toned background gradient (darker at edges)
        base_r, base_g, base_b = config.placeholder_color
        for y in range(height):
            # Vignette effect - darker at top and bottom
            vignette = 1.0 - (abs(y - height/2) / (height/2)) * 0.3
            for x in range(width):
                # Horizontal vignette
                h_vignette = 1.0 - (abs(x - width/2) / (width/2)) * 0.2
                factor = vignette * h_vignette
                r = int(base_r * factor)
                g = int(base_g * factor)
                b = int(base_b * factor)
                surface.set_at((x, y), (r, g, b))

        # Draw ornate Victorian frame
        frame_color = (218, 165, 32)  # Gold
        frame_dark = (139, 90, 43)    # Dark gold

        # Outer frame
        pygame.draw.rect(surface, frame_dark, (0, 0, width, height), 8)
        pygame.draw.rect(surface, frame_color, (4, 4, width-8, height-8), 4)

        # Inner decorative border
        pygame.draw.rect(surface, frame_dark, (15, 15, width-30, height-30), 2)

        # Corner decorations (Victorian ornaments)
        corner_size = 20
        for cx, cy in [(20, 20), (width-20, 20), (20, height-20), (width-20, height-20)]:
            pygame.draw.circle(surface, frame_color, (cx, cy), 8)
            pygame.draw.circle(surface, frame_dark, (cx, cy), 5)

        # Draw stylized silhouette based on character
        center_x, center_y = width // 2, height // 2 - 20
        silhouette_color = (40, 30, 25)  # Dark brown silhouette

        if config.character_id == "major":
            # Military officer - broad shoulders, mustache hint
            self._draw_male_silhouette(surface, center_x, center_y, silhouette_color, military=True)
        elif config.character_id == "lady":
            # Elegant lady - updo hair, high collar
            self._draw_female_silhouette(surface, center_x, center_y, silhouette_color, elegant=True)
        elif config.character_id == "maid":
            # Young woman - simpler style
            self._draw_female_silhouette(surface, center_x, center_y, silhouette_color, elegant=False)
        elif config.character_id == "student":
            # Young man - scholarly look
            self._draw_male_silhouette(surface, center_x, center_y, silhouette_color, military=False)
        else:
            # Generic silhouette
            pygame.draw.ellipse(surface, silhouette_color,
                              (center_x - 35, center_y - 50, 70, 90))

        # Add character name on brass nameplate
        plate_y = height - 50
        pygame.draw.rect(surface, frame_dark, (30, plate_y, width-60, 35))
        pygame.draw.rect(surface, frame_color, (32, plate_y+2, width-64, 31))

        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(config.name, True, (40, 30, 25))
        name_rect = name_text.get_rect(center=(width // 2, plate_y + 17))
        surface.blit(name_text, name_rect)

        return surface

    def _draw_male_silhouette(self, surface: Surface, cx: int, cy: int,
                               color: Tuple[int, int, int], military: bool = False):
        """Draw a male Victorian silhouette."""
        # Head
        pygame.draw.ellipse(surface, color, (cx - 30, cy - 60, 60, 75))

        # Hair (short, parted)
        pygame.draw.ellipse(surface, color, (cx - 32, cy - 65, 64, 35))

        # Neck and collar
        pygame.draw.rect(surface, color, (cx - 15, cy + 10, 30, 25))

        # Shoulders (broader for military)
        shoulder_width = 90 if military else 75
        pygame.draw.ellipse(surface, color,
                          (cx - shoulder_width//2, cy + 20, shoulder_width, 60))

        # Jacket lapels
        pygame.draw.polygon(surface, color, [
            (cx - 35, cy + 35), (cx - 10, cy + 80), (cx - 25, cy + 80)
        ])
        pygame.draw.polygon(surface, color, [
            (cx + 35, cy + 35), (cx + 10, cy + 80), (cx + 25, cy + 80)
        ])

        if military:
            # Epaulettes hint
            pygame.draw.ellipse(surface, color, (cx - 50, cy + 20, 20, 12))
            pygame.draw.ellipse(surface, color, (cx + 30, cy + 20, 20, 12))

    def _draw_female_silhouette(self, surface: Surface, cx: int, cy: int,
                                 color: Tuple[int, int, int], elegant: bool = True):
        """Draw a female Victorian silhouette."""
        # Head
        pygame.draw.ellipse(surface, color, (cx - 28, cy - 55, 56, 70))

        if elegant:
            # Elaborate updo hairstyle
            pygame.draw.ellipse(surface, color, (cx - 35, cy - 75, 70, 45))
            pygame.draw.ellipse(surface, color, (cx - 25, cy - 85, 50, 30))
            # Hair bun
            pygame.draw.circle(surface, color, (cx, cy - 70), 18)
        else:
            # Simpler pulled-back hair with cap
            pygame.draw.ellipse(surface, color, (cx - 32, cy - 65, 64, 35))
            pygame.draw.ellipse(surface, color, (cx - 28, cy - 70, 56, 25))

        # Neck (slender)
        pygame.draw.rect(surface, color, (cx - 10, cy + 10, 20, 20))

        # Shoulders and dress bodice
        pygame.draw.ellipse(surface, color, (cx - 45, cy + 15, 90, 50))

        if elegant:
            # High collar / jewelry hint
            pygame.draw.ellipse(surface, color, (cx - 20, cy + 8, 40, 15))
        else:
            # Simple collar
            pygame.draw.rect(surface, color, (cx - 25, cy + 20, 50, 20))

    def set_focus(self, character_id: Optional[str]):
        """Set which character to focus on (None for wide view)."""
        if character_id == self.focused_character:
            return

        self.previous_focused = self.focused_character
        self.focused_character = character_id
        self.current_view = CameraView.TRANSITION
        self.transition_progress = 0.0

    def update(self):
        """Update camera transition state and speaking effects."""
        if self.current_view == CameraView.TRANSITION:
            self.transition_progress += self.transition_speed
            if self.transition_progress >= 1.0:
                self.transition_progress = 1.0
                self.current_view = CameraView.FOCUS if self.focused_character else CameraView.WIDE

        # Update speaking animation effects
        if self.speaking_effects:
            self.speaking_effects.update()

    def set_speaking(self, character_id: Optional[str]):
        """
        Set which character is currently speaking.

        Args:
            character_id: The ID of the speaking character, or None to stop all speaking
        """
        if self.speaking_effects is None:
            return

        # Stop previous speaker
        if self.speaking_character and self.speaking_character != character_id:
            self.speaking_effects.set_speaking(self.speaking_character, False)

        # Start new speaker
        self.speaking_character = character_id
        if character_id:
            self.speaking_effects.set_speaking(character_id, True)

    def stop_speaking(self):
        """Stop all speaking animations."""
        if self.speaking_effects:
            self.speaking_effects.stop_all_speaking()
        self.speaking_character = None

    def draw_background(self, screen: Surface):
        """Draw the background scene."""
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            # Draw a simple Victorian drawing room background
            self._draw_default_background(screen)

    def _draw_default_background(self, screen: Surface):
        """Draw default background if no image loaded."""
        # Wall
        wall_color = (70, 55, 45)
        pygame.draw.rect(screen, wall_color, (0, 0, self.screen_width, int(self.screen_height * 0.65)))

        # Wainscoting
        wains_color = (50, 40, 35)
        pygame.draw.rect(screen, wains_color,
                        (0, int(self.screen_height * 0.5), self.screen_width, int(self.screen_height * 0.15)))

        # Floor
        floor_color = (45, 35, 30)
        pygame.draw.rect(screen, floor_color,
                        (0, int(self.screen_height * 0.65), self.screen_width, int(self.screen_height * 0.35)))

        # Window (left side)
        window_x = int(self.screen_width * 0.02)
        window_y = int(self.screen_height * 0.05)
        window_w = int(self.screen_width * 0.12)
        window_h = int(self.screen_height * 0.35)
        pygame.draw.rect(screen, (30, 30, 50), (window_x, window_y, window_w, window_h))
        pygame.draw.rect(screen, (60, 70, 90), (window_x + 5, window_y + 5, window_w - 10, window_h - 10))
        # Moon
        pygame.draw.circle(screen, (200, 200, 220),
                          (window_x + window_w // 2, window_y + window_h // 3), 20)

        # Fireplace (right side)
        fp_x = int(self.screen_width * 0.85)
        fp_y = int(self.screen_height * 0.15)
        fp_w = int(self.screen_width * 0.12)
        fp_h = int(self.screen_height * 0.35)
        pygame.draw.rect(screen, (40, 30, 25), (fp_x, fp_y, fp_w, fp_h))
        pygame.draw.rect(screen, (20, 15, 10), (fp_x + 10, fp_y + fp_h // 2, fp_w - 20, fp_h // 2 - 10))
        # Fire glow
        pygame.draw.polygon(screen, (255, 100, 0), [
            (fp_x + fp_w // 2 - 20, fp_y + fp_h - 15),
            (fp_x + fp_w // 2, fp_y + fp_h // 2 + 20),
            (fp_x + fp_w // 2 + 20, fp_y + fp_h - 15)
        ])

        # Table in center (perspective view)
        table_color = (60, 45, 35)
        table_points = [
            (int(self.screen_width * 0.25), int(self.screen_height * 0.75)),
            (int(self.screen_width * 0.75), int(self.screen_height * 0.75)),
            (int(self.screen_width * 0.65), int(self.screen_height * 0.62)),
            (int(self.screen_width * 0.35), int(self.screen_height * 0.62)),
        ]
        pygame.draw.polygon(screen, table_color, table_points)
        pygame.draw.polygon(screen, (80, 65, 55), table_points, 2)

    def draw_portraits(self, screen: Surface, selected_id: Optional[str] = None):
        """Draw character portraits based on current camera view."""
        if self.current_view == CameraView.WIDE or (
            self.current_view == CameraView.TRANSITION and not self.focused_character
        ):
            self._draw_wide_view(screen, selected_id)
        elif self.current_view == CameraView.FOCUS:
            self._draw_focus_view(screen)
        elif self.current_view == CameraView.TRANSITION:
            self._draw_transition(screen)

    def _draw_wide_view(self, screen: Surface, selected_id: Optional[str] = None):
        """Draw all portraits in wide table view."""
        for char_id, config in PORTRAIT_CONFIGS.items():
            portrait = self.portraits.get(char_id)
            if not portrait:
                continue

            # Calculate position and size
            x = int(config.wide_pos[0] * self.screen_width)
            y = int(config.wide_pos[1] * self.screen_height)
            w = int(config.wide_size[0] * self.screen_width)
            h = int(config.wide_size[1] * self.screen_height)

            # Apply speaking effects if this character is speaking
            if self.speaking_effects and char_id == self.speaking_character:
                scaled, x_offset, y_offset = self.speaking_effects.apply_effects(
                    portrait, char_id, w, h
                )
                # Adjust position for glow padding
                glow_pad = self.speaking_effects.get_glow_padding()
                draw_x = x + x_offset - glow_pad // 2
                draw_y = y + y_offset - glow_pad // 2
            else:
                # Scale portrait normally
                scaled = pygame.transform.scale(portrait, (w, h))
                draw_x, draw_y = x, y

            # Draw selection highlight
            if char_id == selected_id:
                pygame.draw.rect(screen, (255, 215, 0), (x - 4, y - 4, w + 8, h + 8), 4)

            # Draw portrait with frame (behind the portrait)
            pygame.draw.rect(screen, (40, 30, 25), (x - 3, y - 3, w + 6, h + 6))

            # Draw the portrait (with or without effects)
            screen.blit(scaled, (draw_x, draw_y))

            # Draw selection number
            num_map = {"major": "1", "lady": "2", "maid": "3", "student": "4"}
            font = pygame.font.Font(None, 36)
            num_text = font.render(f"[{num_map.get(char_id, '?')}]", True, (255, 215, 0))
            screen.blit(num_text, (x + w // 2 - 15, y + h + 10))

    def _draw_focus_view(self, screen: Surface):
        """Draw focused character portrait large and centered."""
        if not self.focused_character:
            return

        portrait = self.portraits.get(self.focused_character)
        if not portrait:
            return

        config = PORTRAIT_CONFIGS.get(self.focused_character)
        if not config:
            return

        # Large centered portrait
        w = int(self.screen_width * 0.4)
        h = int(self.screen_height * 0.65)
        x = (self.screen_width - w) // 2
        y = int(self.screen_height * 0.05)

        # Apply speaking effects if this character is speaking
        char_id = self.focused_character
        if self.speaking_effects and char_id == self.speaking_character:
            scaled, x_offset, y_offset = self.speaking_effects.apply_effects(
                portrait, char_id, w, h
            )
            # Adjust position for glow padding
            glow_pad = self.speaking_effects.get_glow_padding()
            draw_x = x + x_offset - glow_pad // 2
            draw_y = y + y_offset - glow_pad // 2
        else:
            # Scale portrait normally
            scaled = pygame.transform.scale(portrait, (w, h))
            draw_x, draw_y = x, y

        # Draw frame (behind the portrait)
        pygame.draw.rect(screen, (60, 45, 35), (x - 8, y - 8, w + 16, h + 16))
        pygame.draw.rect(screen, (100, 80, 60), (x - 8, y - 8, w + 16, h + 16), 3)

        # Draw portrait with effects
        screen.blit(scaled, (draw_x, draw_y))

        # Draw name plate
        font = pygame.font.Font(None, 42)
        name_text = font.render(config.name, True, (255, 248, 220))
        name_rect = name_text.get_rect(center=(self.screen_width // 2, y + h + 30))
        pygame.draw.rect(screen, (40, 30, 25),
                        (name_rect.x - 20, name_rect.y - 5, name_rect.width + 40, name_rect.height + 10))
        screen.blit(name_text, name_rect)

        # Draw small portraits of others on the sides (dimmed)
        self._draw_side_portraits(screen)

    def _draw_side_portraits(self, screen: Surface):
        """Draw small dimmed portraits of non-focused characters."""
        other_chars = [c for c in PORTRAIT_CONFIGS.keys() if c != self.focused_character]

        positions = [
            (0.02, 0.15),  # Top left
            (0.02, 0.50),  # Bottom left
            (0.85, 0.15),  # Top right
        ]

        for i, char_id in enumerate(other_chars[:3]):
            portrait = self.portraits.get(char_id)
            if not portrait:
                continue

            pos = positions[i]
            x = int(pos[0] * self.screen_width)
            y = int(pos[1] * self.screen_height)
            w = int(self.screen_width * 0.12)
            h = int(self.screen_height * 0.25)

            # Scale and dim
            scaled = pygame.transform.scale(portrait, (w, h))
            # Apply darkening
            dark_overlay = pygame.Surface((w, h))
            dark_overlay.fill((0, 0, 0))
            dark_overlay.set_alpha(100)

            pygame.draw.rect(screen, (30, 25, 20), (x - 2, y - 2, w + 4, h + 4))
            screen.blit(scaled, (x, y))
            screen.blit(dark_overlay, (x, y))

    def _draw_transition(self, screen: Surface):
        """Draw transition animation between views."""
        # Simple crossfade - draw both states with alpha based on progress
        if self.transition_progress < 0.5:
            # First half: fade out previous
            alpha = int(255 * (1 - self.transition_progress * 2))
            if self.previous_focused:
                self._draw_focus_view(screen)
            else:
                self._draw_wide_view(screen, None)
        else:
            # Second half: fade in new
            if self.focused_character:
                self._draw_focus_view(screen)
            else:
                self._draw_wide_view(screen, None)


def get_portrait_download_urls() -> dict[str, str]:
    """
    Returns suggested URLs for downloading character portraits.
    These are public domain / free-to-use Victorian era portraits.
    """
    return {
        "major": "Search: 'Victorian military officer portrait public domain'",
        "lady": "Search: 'Victorian aristocrat woman portrait 1880s public domain'",
        "clara": "Search: 'Victorian servant woman portrait young public domain'",
        "thomas": "Search: 'Victorian young man portrait 1880s public domain'",
        "background": "Search: 'Victorian drawing room interior public domain'",
    }
