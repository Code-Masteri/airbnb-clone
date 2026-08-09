"""
chat.py — Terminal chat interface for Grim.

Run it:
  python src/infer/chat.py --adapter models/adapters/grim-v1

Or with a one-shot prompt:
  python src/infer/chat.py \
    --adapter models/adapters/grim-v1 \
    --prompt "I want to start a dropshipping business"
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.infer.engine import GrimEngine

BANNER = """
╔═══════════════════════════════════════╗
║  G R I M  —  the honest advisor      ║
║  Type your idea, plan, or decision.  ║
║  Type 'exit' or Ctrl+C to quit.      ║
╚═══════════════════════════════════════╝
"""


def run_chat(engine: GrimEngine):
    print(BANNER)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGrim out.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            print("\nGrim out.")
            break

        print("\nGrim: ", end="", flush=True)

        # Stream response token by token
        for token in engine.stream(user_input):
            print(token, end="", flush=True)

        print()  # newline after response


def main():
    parser = argparse.ArgumentParser(description="Chat with Grim in the terminal")
    parser.add_argument("--adapter", required=True, help="Path to LoRA adapter folder")
    parser.add_argument("--prompt", help="Single prompt (non-interactive mode)")
    parser.add_argument("--config", default="configs/inference.yaml")
    args = parser.parse_args()

    engine = GrimEngine(adapter_path=args.adapter, config_path=args.config)
    engine.load()

    if args.prompt:
        # One-shot mode
        print(f"\nYou: {args.prompt}")
        print("\nGrim: ", end="", flush=True)
        for token in engine.stream(args.prompt):
            print(token, end="", flush=True)
        print()
    else:
        # Interactive chat mode
        run_chat(engine)


if __name__ == "__main__":
    main()
