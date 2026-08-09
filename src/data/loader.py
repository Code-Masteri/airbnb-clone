"""
loader.py — Downloads the base model from Hugging Face.

What this does:
  Downloads Llama 3.2 3B Instruct to your local HuggingFace cache (~6GB).
  You only need to run this once.

Requirements:
  - Free HuggingFace account at huggingface.co
  - Accept the Llama 3.2 license at: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
  - Run: huggingface-cli login (paste your token)

Run it:
  python src/data/loader.py
"""

from huggingface_hub import snapshot_download
from pathlib import Path
import sys

MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"


def main():
    print(f"\n Downloading: {MODEL_ID}")
    print( " This is about 6GB. It goes to ~/.cache/huggingface/")
    print( " You only need to do this once.\n")
    print( " If this fails with a 401 error:")
    print( "   1. Go to https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct")
    print( "   2. Click 'Agree and access repository'")
    print( "   3. Run: huggingface-cli login")
    print( "   4. Run this script again\n")

    try:
        path = snapshot_download(
            repo_id=MODEL_ID,
            ignore_patterns=["*.msgpack", "flax_model*", "tf_model*"],
        )
        print(f"\n Model downloaded to: {path}")
        print(f"\n Next step:")
        print(f"   python src/data/formatter.py \\")
        print(f"     --input data/synthetic/grim_train.jsonl \\")
        print(f"     --output data/processed/train.jsonl")

    except Exception as e:
        print(f"\n[!] Download failed: {e}")
        print("\n Make sure you:")
        print("   1. Accepted the license on HuggingFace")
        print("   2. Ran: huggingface-cli login")
        sys.exit(1)


if __name__ == "__main__":
    main()
