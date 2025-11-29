"""
Mouth animation system for character talking animation.

Provides procedural jaw/mouth animation for characters during speech.
Falls back to subtle head bobbing if no jaw bone is found in the model.
"""
import random
from typing import Optional

from panda3d.core import NodePath
from direct.interval.IntervalGlobal import Sequence, LerpHprInterval, Wait


class MouthAnimator:
    """Handles procedural mouth/jaw animation for speaking characters."""

    # Common jaw bone names in character rigs
    JAW_BONE_NAMES = [
        "jaw", "Jaw", "JAW",
        "jawbone", "JawBone", "jaw_bone",
        "mouth", "Mouth", "mouth_bone",
        "lower_jaw", "lowerJaw",
    ]

    # Common head bone names (fallback)
    HEAD_BONE_NAMES = [
        "head", "Head", "HEAD",
        "head_bone", "HeadBone",
        "neck", "Neck",
    ]

    def __init__(self, character_node: NodePath, enable_animation: bool = True):
        """
        Initialize the mouth animator.

        Args:
            character_node: The character's NodePath
            enable_animation: Whether to enable mouth animation
        """
        self.character_node = character_node
        self.enable_animation = enable_animation
        self.is_talking = False
        self.animation_sequence: Optional[Sequence] = None

        # Find jaw or head bone for animation
        self.jaw_bone: Optional[NodePath] = None
        self.head_bone: Optional[NodePath] = None
        self.animation_mode = "none"  # "jaw", "head", or "none"

        if self.enable_animation:
            self._find_animation_bones()

    def _find_animation_bones(self) -> None:
        """Search for jaw bone or head bone in the character model."""
        # Try to find jaw bone first
        for bone_name in self.JAW_BONE_NAMES:
            bone = self.character_node.find(f"**/{bone_name}")
            if not bone.isEmpty():
                self.jaw_bone = bone
                self.animation_mode = "jaw"
                print(f"✓ Found jaw bone for animation: {bone_name}")
                return

        # Fallback: try to find head bone for subtle bobbing
        for bone_name in self.HEAD_BONE_NAMES:
            bone = self.character_node.find(f"**/{bone_name}")
            if not bone.isEmpty():
                self.head_bone = bone
                self.animation_mode = "head"
                print(f"⚠ No jaw bone found, using head bobbing: {bone_name}")
                return

        # No bones found - animation disabled
        print("⚠ No animation bones found - mouth animation disabled")
        self.animation_mode = "none"
        self.enable_animation = False

    def start_talking(self) -> None:
        """Start the talking animation."""
        if not self.enable_animation or self.is_talking:
            return

        self.is_talking = True

        if self.animation_mode == "jaw":
            self._animate_jaw()
        elif self.animation_mode == "head":
            self._animate_head()

    def stop_talking(self) -> None:
        """Stop the talking animation and return to neutral position."""
        if not self.is_talking:
            return

        self.is_talking = False

        # Stop current animation
        if self.animation_sequence:
            self.animation_sequence.finish()
            self.animation_sequence = None

        # Return to neutral position
        if self.animation_mode == "jaw" and self.jaw_bone:
            self.jaw_bone.setHpr(0, 0, 0)
        elif self.animation_mode == "head" and self.head_bone:
            self.head_bone.setHpr(0, 0, 0)

    def _animate_jaw(self) -> None:
        """Animate jaw opening and closing."""
        if not self.jaw_bone or not self.is_talking:
            return

        # Random jaw rotation amount (5-15 degrees downward)
        jaw_rotation = random.uniform(5, 15)

        # Random timing (0.1-0.2 seconds per movement)
        open_duration = random.uniform(0.1, 0.2)
        close_duration = random.uniform(0.08, 0.15)
        pause_duration = random.uniform(0.05, 0.15)

        # Create animation sequence: open -> close -> pause -> repeat
        self.animation_sequence = Sequence(
            LerpHprInterval(
                self.jaw_bone,
                duration=open_duration,
                hpr=(0, -jaw_rotation, 0),  # Pitch down to open jaw
                blendType='easeInOut'
            ),
            LerpHprInterval(
                self.jaw_bone,
                duration=close_duration,
                hpr=(0, 0, 0),  # Return to closed
                blendType='easeInOut'
            ),
            Wait(pause_duration),
        )

        # Loop the animation while talking
        self.animation_sequence.loop()

    def _animate_head(self) -> None:
        """Animate subtle head bobbing as fallback."""
        if not self.head_bone or not self.is_talking:
            return

        # Subtle head bobbing (2-5 degrees)
        bob_amount = random.uniform(2, 5)

        # Random timing
        bob_duration = random.uniform(0.15, 0.25)
        pause_duration = random.uniform(0.1, 0.2)

        # Create subtle bobbing animation
        self.animation_sequence = Sequence(
            LerpHprInterval(
                self.head_bone,
                duration=bob_duration,
                hpr=(random.uniform(-2, 2), bob_amount, 0),  # Slight nod
                blendType='easeInOut'
            ),
            LerpHprInterval(
                self.head_bone,
                duration=bob_duration,
                hpr=(0, 0, 0),  # Return to neutral
                blendType='easeInOut'
            ),
            Wait(pause_duration),
        )

        # Loop the animation while talking
        self.animation_sequence.loop()

    def cleanup(self) -> None:
        """Clean up animation resources."""
        self.stop_talking()
        if self.animation_sequence:
            self.animation_sequence.finish()
            self.animation_sequence = None
