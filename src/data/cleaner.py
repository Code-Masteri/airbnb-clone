"""
cleaner.py — Filters out bad training examples.

What makes a bad example:
  - Too short (the model gave up or errored)
  - Missing required sections (THE VERDICT, WHAT'S BROKEN, etc.)
  - Duplicate prompts
  - Examples where the model broke character (said "Great idea!" etc.)

Run it:
  python src/data/cleaner.py \
    --input data/synthetic/grim_train.jsonl \
    --output data/synthetic/grim_train_clean.jsonl
"""

import argparse
import json
from pathlib import Path
from tqdm import tqdm

# These phrases mean the model broke character — Grim would never say these
BAD_PHRASES = [
    "great idea",
    "excellent idea",
    "i love this",
    "this is amazing",
    "you're on the right track",
    "sounds good",
    "absolutely",
    "wonderful",
]

# All Grim responses must contain these sections
REQUIRED_SECTIONS = [
    "THE VERDICT",
    "WHAT'S BROKEN",
    "THE FIX",
    "THE ONE THING",
]

MIN_RESPONSE_LENGTH = 150
MAX_RESPONSE_LENGTH = 1500


def is_valid(record: dict) -> tuple[bool, str]:
    """
    Returns (True, "") if valid, (False, reason) if not.
    """
    prompt = record.get("prompt", "")
    response = record.get("response", "")

    if not prompt or not response:
        return False, "missing prompt or response"

    if len(response) < MIN_RESPONSE_LENGTH:
        return False, f"response too short ({len(response)} chars)"

    if len(response) > MAX_RESPONSE_LENGTH:
        return False, f"response too long ({len(response)} chars)"

    response_lower = response.lower()
    for phrase in BAD_PHRASES:
        if phrase in response_lower:
            return False, f"model broke character: '{phrase}'"

    for section in REQUIRED_SECTIONS:
        if section not in response:
            return False, f"missing section: {section}"

    return True, ""


def main():
    parser = argparse.ArgumentParser(description="Clean Grim training data")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"[!] Input file not found: {input_path}")
        return

    print(f"\n Cleaning: {input_path}")

    total = kept = 0
    skip_reasons: dict[str, int] = {}
    seen_prompts: set[str] = set()

    with open(input_path) as fin, open(output_path, "w") as fout:
        lines = fin.readlines()
        for line in tqdm(lines, unit="example"):
            line = line.strip()
            if not line:
                continue

            total += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                skip_reasons["invalid json"] = skip_reasons.get("invalid json", 0) + 1
                continue

            # Deduplicate
            prompt = record.get("prompt", "").strip()
            if prompt in seen_prompts:
                skip_reasons["duplicate"] = skip_reasons.get("duplicate", 0) + 1
                continue
            seen_prompts.add(prompt)

            valid, reason = is_valid(record)
            if not valid:
                skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                continue

            fout.write(json.dumps(record) + "\n")
            kept += 1

    print(f"\n Results:")
    print(f"   Total:   {total}")
    print(f"   Kept:    {kept}")
    print(f"   Removed: {total - kept}")

    if skip_reasons:
        print(f"\n Removal reasons:")
        for reason, count in sorted(skip_reasons.items(), key=lambda x: -x[1]):
            print(f"   {count:4d}x  {reason}")

    print(f"\n Clean data saved to: {output_path}")


if __name__ == "__main__":
    main()
