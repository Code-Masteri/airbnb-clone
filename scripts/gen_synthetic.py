"""
gen_synthetic.py — Generate training data using Ollama locally.

What this does:
  1. Takes a list of topic prompts (ideas, habits, plans, decisions)
  2. Sends each one to Ollama running on your Mac
  3. Gets back a "Grim-style" brutally honest response
  4. Saves each pair as a JSONL line (one JSON object per line)

Run it:
  python scripts/gen_synthetic.py --count 500 --output data/synthetic/grim_train.jsonl
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path

import requests
from tqdm import tqdm

# --- Seed topics ---
# These are the raw inputs we'll send to the model.
# We combine them with different framings to get variety.
SEED_TOPICS = [
    "I want to start a dropshipping business",
    "I keep procrastinating on my side project",
    "I want to quit my job and freelance full time",
    "I haven't exercised in 6 months",
    "My startup idea is an app that connects dog owners",
    "I want to learn machine learning in 3 months",
    "I'm thinking about moving to a new city with no job lined up",
    "I want to become a content creator on YouTube",
    "I've been spending more than I earn for the past year",
    "I want to build a SaaS product in my spare time",
    "I skip the gym whenever I feel tired",
    "I want to launch a newsletter and charge $10/month",
    "I keep starting projects and never finishing them",
    "My plan is to raise VC funding before building an MVP",
    "I want to learn to code from scratch at age 35",
    "I've been working the same job for 7 years and hate it",
    "I want to write a book but haven't started",
    "I'm thinking about going back to school for an MBA",
    "I want to build a mobile app with no tech background",
    "I plan to save money starting next month",
    "I want to launch a coffee brand online",
    "I keep scrolling social media instead of working",
    "My business idea is an AI tool for HR departments",
    "I want to do a 30-day challenge to change my life",
    "I'm considering crypto trading as my main income",
    "I haven't talked to my clients in weeks",
    "I want to pivot my career into UX design",
    "I'm thinking about launching a course on what I know",
    "I want to cold email 100 companies this week",
    "My plan is to work on my startup on weekends only",
]

FRAMINGS = [
    "{}",
    "My plan: {}",
    "I've been thinking — {}",
    "Here's what I want to do: {}",
    "Tell me what you think: {}",
    "Be real with me. {}",
    "I need feedback on this: {}",
]

GENERATOR_SYSTEM = """You are a brutally honest advisor named Grim. A user will tell you an idea, habit, plan, or decision.

Respond in this EXACT structure — do not deviate:

THE VERDICT
One or two sentences. The honest bottom line. No softening.

WHAT'S BROKEN
- Bullet point 1
- Bullet point 2  
- Bullet point 3

IF YOU DO NOTHING
- 1 week: [what happens]
- 1 month: [what happens]
- 6 months: [what happens]

THE FIX
- Step 1
- Step 2
- Step 3

THE ONE THING
One sentence. The single most important action to take right now.

*Closing italic line — punchy and memorable.*

Rules: No empty praise. No "that could work though!". Keep it under 350 words. Be direct."""


def call_ollama(prompt: str, model: str = "llama3.2:3b", retries: int = 3) -> str:
    """
    Sends a prompt to Ollama running locally.
    Ollama exposes a simple HTTP API at localhost:11434.
    """
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": GENERATOR_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 0.85,
            "top_p": 0.9,
        },
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"].strip()
        except requests.exceptions.ConnectionError:
            if attempt == 0:
                print("\n[!] Cannot connect to Ollama. Is it running?")
                print("    Run this in another terminal: ollama serve")
                sys.exit(1)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return None

    return None


def generate_prompt() -> str:
    topic = random.choice(SEED_TOPICS)
    framing = random.choice(FRAMINGS)
    return framing.format(topic)


def main():
    parser = argparse.ArgumentParser(description="Generate Grim training data via Ollama")
    parser.add_argument("--count", type=int, default=500, help="Number of examples to generate")
    parser.add_argument("--output", type=str, required=True, help="Output JSONL file path")
    parser.add_argument("--model", type=str, default="llama3.2:3b", help="Ollama model to use")
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n Generating {args.count} training examples...")
    print(f" Output: {args.output}")
    print(f" Model: {args.model}")
    print(f" Make sure Ollama is running (ollama serve &)\n")

    # Test connection first
    print("Testing Ollama connection...")
    test = call_ollama("Say OK.", model=args.model)
    if test is None:
        print("[!] Failed to connect to Ollama. Exiting.")
        sys.exit(1)
    print(f"Connected. Model responded: {test[:50]}...\n")

    generated = 0
    skipped = 0

    with open(output_path, "w") as f:
        pbar = tqdm(total=args.count, unit="example")

        while generated < args.count:
            user_prompt = generate_prompt()
            response = call_ollama(user_prompt, model=args.model)

            if response is None or len(response) < 100:
                skipped += 1
                continue

            # Each line is one valid JSON object
            record = {
                "prompt": user_prompt,
                "response": response,
            }
            f.write(json.dumps(record) + "\n")
            generated += 1
            pbar.update(1)
            pbar.set_postfix({"skipped": skipped})

        pbar.close()

    print(f"\n Done!")
    print(f"   Generated: {generated}")
    print(f"   Skipped (bad output): {skipped}")
    print(f"   Saved to: {output_path}")
    print(f"\n Next step:")
    print(f"   python src/data/formatter.py --input {args.output} --output data/processed/train.jsonl")


if __name__ == "__main__":
    main()
