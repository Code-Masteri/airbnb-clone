"""
engine.py — Loads the fine-tuned model and runs inference.

This is the core inference module used by both the CLI and the UI.
It loads the base model + LoRA adapter together and generates text.
"""

import sys
from pathlib import Path
from typing import Iterator

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.prompts.system import build_prompt


class GrimEngine:
    """
    Wraps MLX model loading and text generation.
    Load once, call many times.
    """

    def __init__(self, adapter_path: str, config_path: str = "configs/inference.yaml"):
        self.adapter_path = adapter_path
        self.config = self._load_config(config_path)
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def _load_config(self, path: str) -> dict:
        try:
            with open(path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Sensible defaults if config file is missing
            return {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 800,
                "repetition_penalty": 1.1,
            }
    def load(self):
        """
        Load the model and adapter into memory.
        This takes a few seconds the first time.
        """
        if self._loaded:
            return

        try:
            from mlx_lm import load
        except ImportError:
            print("[!] MLX not found. Run: pip install mlx mlx-lm")
            sys.exit(1)

        print(f" Loading model + adapter: {self.adapter_path}")
        print( " (Takes ~10 seconds on first load...)")

        adapter = Path(self.adapter_path)
        if not adapter.exists():
            print(f"\n[!] Adapter not found: {adapter}")
            print(f"    Did training finish? Check: {adapter}")
            sys.exit(1)

        # Load base model from HF cache + apply LoRA adapter on top
        from mlx_lm import load
        self.model, self.tokenizer = load(
            "meta-llama/Llama-3.2-3B-Instruct",
            adapter_path=str(adapter),
        )
        self._loaded = True
        print(" Model ready.\n")

    def generate(self, user_message: str) -> str:
        """
        Generate a Grim response for the given user message.
        Returns the full response string.
        """
        if not self._loaded:
            self.load()

        from mlx_lm import generate

        prompt = build_prompt(user_message)

        response = generate(
            model=self.model,
            tokenizer=self.tokenizer,
            prompt=prompt,
            max_tokens=self.config.get("max_tokens", 800),
            temp=self.config.get("temperature", 0.7),
            top_p=self.config.get("top_p", 0.9),
            repetition_penalty=self.config.get("repetition_penalty", 1.1),
        )

        # Clean up — sometimes the model echoes the prompt
        if "<|assistant|>" in response:
            response = response.split("<|assistant|>")[-1]

        for stop in ["<|end|>", "<|user|>", "<|system|>"]:
            response = response.split(stop)[0]

        return response.strip()

    def stream(self, user_message: str) -> Iterator[str]:
        """
        Stream the response token by token.
        Useful for the UI to show text as it's being generated.
        """
        if not self._loaded:
            self.load()

        from mlx_lm.utils import stream_generate

        prompt = build_prompt(user_message)
        stop_tokens = self.config.get("stop_tokens", ["<|end|>", "<|user|>"])

        for token in stream_generate(
            model=self.model,
            tokenizer=self.tokenizer,
            prompt=prompt,
            max_tokens=self.config.get("max_tokens", 800),
            temp=self.config.get("temperature", 0.7),
            top_p=self.config.get("top_p", 0.9),
        ):
            # Stop if we hit a stop token
            if any(s in token for s in stop_tokens):
                break
            yield token
