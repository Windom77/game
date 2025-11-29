#!/usr/bin/env python3
"""
Interaction Test - Main Entry Point

A minimal testing environment for character interaction mechanics.
Tests LLM integration with a single character in a simple 3D scene.
"""
import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Check for Panda3D before importing
try:
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import WindowProperties
except ImportError:
    print("ERROR: Panda3D is not installed.")
    print("Install with: pip install panda3d")
    sys.exit(1)

try:
    from llm import get_provider
    from test_scene import TestScene
    from test_character import get_test_character
    from interaction_controller import InteractionController
    from mouth_animation import MouthAnimator
except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}")
    print("Make sure you're running from the interaction_test directory")
    sys.exit(1)


class InteractionTestApp(ShowBase):
    """Main application for interaction testing."""

    def __init__(self, provider_name: str = "mock", wireframe: bool = False):
        """
        Initialize the interaction test application.

        Args:
            provider_name: LLM provider to use (mock/ollama/openai/groq/anthropic)
            wireframe: Enable wireframe rendering for debugging
        """
        print("=" * 60)
        print("Interaction Test - Character Interaction Testing Environment")
        print("=" * 60)

        # Initialize Panda3D
        ShowBase.__init__(self)

        # Configure window
        self._setup_window()

        # Get model path (relative to parent directory)
        parent_dir = Path(__file__).parent.parent
        model_path = parent_dir / "assets" / "models" / "RPmeAvatar.glb"

        # Check if model exists
        if not model_path.exists():
            print(f"⚠ Warning: Model not found at {model_path}")
            print("  Will use placeholder geometry instead")

        # Initialize LLM provider
        print(f"\nInitializing LLM provider: {provider_name}")
        try:
            self.llm_provider = get_provider(provider_name)
            print(f"✓ LLM provider ready: {type(self.llm_provider).__name__}")
        except Exception as e:
            print(f"ERROR: Failed to initialize LLM provider: {e}")
            print("Falling back to mock provider")
            self.llm_provider = get_provider("mock")

        # Initialize test character
        print("\nInitializing test character...")
        self.character = get_test_character()
        print(f"✓ Character ready: {self.character.name}")

        # Initialize 3D scene
        print("\nInitializing 3D scene...")
        try:
            self.scene = TestScene(self, str(model_path), wireframe=wireframe)
            print("✓ Scene initialized")
        except Exception as e:
            print(f"ERROR: Failed to initialize scene: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        # Initialize mouth animator
        print("\nInitializing mouth animation...")
        try:
            self.mouth_animator = MouthAnimator(
                self.scene.character_node,
                enable_animation=True
            )
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize mouth animation: {e}")
            self.mouth_animator = None

        # Initialize interaction controller
        print("\nInitializing interaction controller...")
        try:
            self.controller = InteractionController(
                self, self.character, self.llm_provider,
                mouth_animator=self.mouth_animator
            )
            print("✓ Controller initialized")
        except Exception as e:
            print(f"ERROR: Failed to initialize controller: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        print("\n" + "=" * 60)
        print("Ready! Type your questions and press Enter.")
        print("Press ESC to quit.")
        print("=" * 60 + "\n")

    def _setup_window(self) -> None:
        """Configure the Panda3D window."""
        props = WindowProperties()
        props.setTitle("Interaction Test - Character Testing Environment")
        props.setSize(800, 600)
        self.win.requestProperties(props)
        print("✓ Window configured (800x600)")


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Interaction Test - Test character interaction mechanics"
    )
    parser.add_argument(
        '--provider',
        type=str,
        default='mock',
        choices=['mock', 'ollama', 'openai', 'groq', 'anthropic'],
        help='LLM provider to use (default: mock)'
    )
    parser.add_argument(
        '--wireframe',
        action='store_true',
        help='Enable wireframe rendering for debugging'
    )
    return parser.parse_args()


def check_dependencies() -> list[str]:
    """
    Check for required dependencies.

    Returns:
        List of missing dependencies
    """
    missing = []

    try:
        import panda3d
    except ImportError:
        missing.append('panda3d')

    try:
        import trimesh
    except ImportError:
        missing.append('trimesh')

    try:
        import numpy
    except ImportError:
        missing.append('numpy')

    return missing


def main():
    """Main entry point."""
    args = parse_arguments()

    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print("ERROR: Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstall with: pip install " + " ".join(missing_deps))
        sys.exit(1)

    # Check for requests library if using API providers
    if args.provider in ['ollama', 'openai', 'groq', 'anthropic']:
        try:
            import requests
        except ImportError:
            print("WARNING: 'requests' library not installed.")
            print("API providers require requests. Install with: pip install requests")
            print("Falling back to mock provider...\n")
            args.provider = 'mock'

    # Run the application
    try:
        app = InteractionTestApp(provider_name=args.provider, wireframe=args.wireframe)
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: Application crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
