"""
formatter.py — Converts raw JSONL into the chat template format MLX expects.

What this does:
  Takes your raw {prompt, response} pairs and wraps them in the
  Llama 3.2 chat template format. The model was trained on this exact
  format, so it needs to see it during fine-tuning too.

  Input:
    {"prompt": "My business idea is...", "response": "THE VERDICT\n..."}

  Output:
    {"text": "<|system|>\nYou are Grim...\n<|user|>\nMy business idea is...\n<|assistant|>\nTHE VERDICT\n...<|end|>"}

Run it:
  python src/data/formatter.py \
    --input data/synthetic/grim_train.jsonl \
    --output data/processed/train.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

from tqdm import tqdm

# Add project root to path so we can import from src/prompts
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.prompts.system import SYSTEM_PROMPT


def format_record(record: dict) -> dict | None:
    """
    Takes a raw {prompt, response} dict and returns {text: <full chat string>}.
    Returns None if the record is malformed.
    """
    prompt = record.get("prompt", "").strip()
    response = record.get("response", "").strip()

    if not prompt or not response:
        return None

    # This is the exact format Llama 3.2 was trained on.
    # The model will learn to generate everything after <|assistant|>
    text = (
        f"<|system|>\n{SYSTEM_PROMPT}\n"
        f"<|user|>\n{prompt}\n"
        f"<|assistant|>\n{response}<|end|>"
    )

    return {"text": text}


def main():
    parser = argparse.ArgumentParser(description="Format training data for MLX")
    parser.add_argument("--input", required=True, help="Raw JSONL file")
    parser.add_argument("--output", required=True, help="Formatted JSONL file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"[!] Input not found: {input_path}")
        print(f"    Run gen_synthetic.py first.")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n Formatting: {input_path} -> {output_path}")

    total = formatted = skipped = 0

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
                skipped += 1
                continue

            formatted_record = format_record(record)
            if formatted_record is None:
                skipped += 1
                continue

            fout.write(json.dumps(formatted_record) + "\n")
            formatted += 1

    print(f"\n Done!")
    print(f"   Formatted: {formatted}")
    print(f"   Skipped:   {skipped}")
    print(f"   Output:    {output_path}")
    print(f"\n Check a sample:")
    print(f"   python -c \"import json; d=json.loads(open('{output_path}').readline()); print(d['text'][:500])\"")
    print(f"\n Next step:")
    print(f"   python src/data/loader.py")


if __name__ == "__main__":
    main()
