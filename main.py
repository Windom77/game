#!/usr/bin/env python3
"""
Main entry point for the Victorian Murder Mystery game.

A prototype interactive RPG game featuring an LLM-powered murder mystery
set in Victorian England. The player takes the role of a detective
questioning four suspects to uncover the murderer.

Usage:
    python main.py                    # Terminal UI with auto-detected LLM
    python main.py --ui terminal      # Force terminal UI
    python main.py --ui pygame        # Use pygame graphical UI
    python main.py --ui 3d            # Use Panda3D 3D immersive UI
    python main.py --llm mock         # Use mock responses (no LLM)
    python main.py --llm ollama       # Use local Ollama LLM
    python main.py --llm openai       # Use OpenAI API
    python main.py --llm groq         # Use Groq API (free tier)
"""

import argparse
import sys


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Victorian Murder Mystery - An LLM-powered detective game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                    # Quick start with defaults
    python main.py --ui pygame        # Graphical mode
    python main.py --llm ollama       # Use local LLM
    python main.py --llm openai       # Use OpenAI (needs OPENAI_API_KEY)

Environment Variables:
    OPENAI_API_KEY     - Required for --llm openai
    ANTHROPIC_API_KEY  - Required for --llm anthropic
    GROQ_API_KEY       - Required for --llm groq
        """
    )

    parser.add_argument(
        "--ui",
        choices=["terminal", "pygame", "3d"],
        default="terminal",
        help="User interface mode (default: terminal, 3d=Panda3D)"
    )

    parser.add_argument(
        "--llm",
        choices=["mock", "ollama", "openai", "groq", "anthropic", "auto"],
        default="auto",
        help="LLM provider to use (default: auto-detect best available)"
    )

    parser.add_argument(
        "--model",
        type=str,
        help="Specific model to use (overrides default for provider)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    return parser.parse_args()


def check_dependencies():
    """Check and report on available dependencies."""
    dependencies = {
        "rich": "Enhanced terminal UI",
        "pygame": "Graphical UI",
        "requests": "API communication (required for cloud LLMs)",
    }

    missing = []
    available = []

    for package, description in dependencies.items():
        try:
            __import__(package)
            available.append(f"  [OK] {package} - {description}")
        except ImportError:
            missing.append(f"  [--] {package} - {description}")

    if available or missing:
        print("\nDependency Status:")
        for line in available:
            print(line)
        for line in missing:
            print(line)
        print()


def main():
    """Main entry point."""
    args = parse_args()

    # Set debug mode in config
    if args.debug:
        import config
        config.DEBUG_MODE = True
        check_dependencies()

    # Select LLM provider
    from llm import get_provider, detect_best_provider

    if args.llm == "auto":
        llm_provider = detect_best_provider()
    else:
        llm_provider = get_provider(args.llm)

    # Print startup info
    print("\n" + "=" * 50)
    print("   THE PEMBERTON MANOR MYSTERY")
    print("   A Victorian Murder Mystery Game")
    print("=" * 50)
    print(f"\nLLM Provider: {type(llm_provider).__name__}")
    print(f"UI Mode: {args.ui}")
    print("\nStarting game...\n")

    # Launch appropriate UI
    if args.ui == "3d":
        try:
            from ui.panda3d_ui import run_panda3d_game
            run_panda3d_game()
        except ImportError as e:
            print(f"Panda3D not available: {e}")
            print("Install with: pip install panda3d")
            print("Falling back to pygame...")
            try:
                from ui.pygame_ui import run_pygame_game
                run_pygame_game()
            except ImportError:
                print("Pygame also not available, using terminal...")
                from ui.terminal import run_terminal_game
                run_terminal_game()
    elif args.ui == "pygame":
        try:
            from ui.pygame_ui import run_pygame_game
            run_pygame_game()
        except ImportError as e:
            print(f"Pygame not available: {e}")
            print("Falling back to terminal UI...")
            from ui.terminal import run_terminal_game
            run_terminal_game()
    else:
        from ui.terminal import run_terminal_game
        run_terminal_game()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
        sys.exit(0)
