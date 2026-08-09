"""
test_model.py — Quick test suite to see if Grim is working.

Run after training:
  python scripts/test_model.py \
    --adapter models/adapters/grim-v1 \
    --prompt "My startup idea is an app that connects dog owners"

Or run all built-in tests:
  python scripts/test_model.py --adapter models/adapters/grim-v1 --all
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.infer.engine import GrimEngine

TEST_PROMPTS = [
    "My plan is to quit my job tomorrow and start a YouTube channel",
    "I keep skipping the gym but I want abs by next month",
    "I want to build an app that does everything — calendar, notes, tasks, finance, fitness",
    "My startup idea: Uber but for lawn mowing",
    "I've been meaning to learn Python for two years now",
]

# What a good Grim response must contain
REQUIRED_IN_RESPONSE = [
    "THE VERDICT",
    "WHAT'S BROKEN",
    "THE FIX",
    "THE ONE THING",
]


def check_response(response: str) -> tuple[bool, list[str]]:
    """Returns (passed, list of issues)"""
    issues = []
    for section in REQUIRED_IN_RESPONSE:
        if section not in response:
            issues.append(f"Missing section: {section}")
    if len(response) < 100:
        issues.append(f"Too short ({len(response)} chars)")
    return len(issues) == 0, issues


def run_test(engine: GrimEngine, prompt: str, index: int = 0) -> bool:
    print(f"\n Test {index + 1}: {prompt[:60]}...")
    print("-" * 60)

    start = time.time()
    response = engine.generate(prompt)
    elapsed = time.time() - start

    print(response)
    print("-" * 60)

    passed, issues = check_response(response)
    status = "PASS" if passed else "FAIL"
    print(f" {status} | {elapsed:.1f}s | {len(response)} chars")

    if issues:
        for issue in issues:
            print(f"   [!] {issue}")

    return passed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--prompt", help="Single custom prompt to test")
    parser.add_argument("--all", action="store_true", help="Run all built-in tests")
    parser.add_argument("--config", default="configs/inference.yaml")
    args = parser.parse_args()

    engine = GrimEngine(adapter_path=args.adapter, config_path=args.config)
    engine.load()

    if args.prompt:
        # Test one custom prompt
        run_test(engine, args.prompt, 0)
    elif args.all:
        # Run all built-in tests
        passed = 0
        for i, prompt in enumerate(TEST_PROMPTS):
            if run_test(engine, prompt, i):
                passed += 1

        print(f"\n Results: {passed}/{len(TEST_PROMPTS)} passed")
        if passed == len(TEST_PROMPTS):
            print(" Grim is working perfectly.")
        elif passed >= len(TEST_PROMPTS) * 0.7:
            print(" Grim is mostly working. A bit more training data might help.")
        else:
            print(" Grim needs more training. Generate more data and retrain.")
    else:
        # Default: run the first built-in test
        run_test(engine, TEST_PROMPTS[0], 0)
        print("\n Tip: run with --all to test all prompts, or --prompt 'your text'")


if __name__ == "__main__":
    main()
