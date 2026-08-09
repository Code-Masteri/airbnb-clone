"""
qlora.py — Fine-tune Llama 3.2 3B on Apple Silicon using MLX + LoRA.

What LoRA does (explained simply):
  A 3B parameter model has 3 billion numbers that define its behavior.
  Training all of them would take weeks on your Mac.
  LoRA says: "instead of changing all 3B numbers, let's add tiny
  side-matrices (adapters) to some layers and only train those."
  The adapters are ~10M parameters — much faster to train.
  After training, the adapter is a ~100MB file you keep.
  At inference time, you load the base model + adapter together.

Run it:
  python src/train/qlora.py \
    --config configs/training.yaml \
    --data data/processed/train.jsonl \
    --output models/adapters/grim-v1
"""

import argparse
import json
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.train.utils import TrainingLogger, format_time, count_parameters


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_dataset(data_path: str) -> list[dict]:
    """Load JSONL training data. Each line is one example."""
    data = []
    with open(data_path) as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def main():
    parser = argparse.ArgumentParser(description="Fine-tune Grim with LoRA on MLX")
    parser.add_argument("--config", required=True, help="Path to training.yaml")
    parser.add_argument("--data", required=True, help="Path to processed train.jsonl")
    parser.add_argument("--output", required=True, help="Where to save the adapter")
    args = parser.parse_args()

    # ---- Load config ----
    print(f"\n Loading config: {args.config}")
    cfg = load_config(args.config)

    # ---- Load data ----
    print(f" Loading data: {args.data}")
    if not Path(args.data).exists():
        print(f"[!] Data file not found: {args.data}")
        print(f"    Run formatter.py first.")
        sys.exit(1)

    dataset = load_dataset(args.data)
    print(f" Examples: {len(dataset)}")

    if len(dataset) < 10:
        print("[!] Very few examples. Generate more with gen_synthetic.py")
        sys.exit(1)

    # ---- Import MLX ----
    try:
        import mlx.core as mx
        import mlx.optimizers as optim
        from mlx_lm import load
        from mlx_lm.tuner.lora import inject_lora
        from mlx_lm.tuner.trainer import train, TrainingArgs
    except ImportError:
        print("\n[!] MLX not installed.")
        print("    Run: pip install mlx mlx-lm")
        sys.exit(1)

    # ---- Load model ----
    model_id = cfg.get("model", "meta-llama/Llama-3.2-3B-Instruct")
    print(f"\n Loading model: {model_id}")
    print(" (Using cached version if available)\n")

    try:
        model, tokenizer = load(model_id)
    except Exception as e:
        print(f"[!] Failed to load model: {e}")
        print("\n Make sure you ran: python src/data/loader.py")
        sys.exit(1)

    # ---- Apply LoRA (FIXED) ----
    num_layers = cfg.get("lora_layers", 16)
    lora_rank = cfg.get("lora_rank", 8)
    lora_alpha = cfg.get("lora_alpha", 16)

    print(f" Applying LoRA:")
    print(f"   Layers:  {num_layers}")
    print(f"   Rank:    {lora_rank}")
    print(f"   Alpha:   {lora_alpha}")

    model.freeze()

    inject_lora(
        model,
        r=lora_rank,
        alpha=lora_alpha,
        target_modules=["q_proj", "v_proj"],  # can expand later
        num_layers=num_layers,
    )

    # ---- Count parameters ----
    params = count_parameters(model)
    print(f"\n Parameters:")
    print(f"   Total:     {params['total']:,}")
    print(f"   Trainable: {params['trainable']:,} ({params['trainable_pct']}%)")

    # ---- Tokenize dataset ----
    print(f"\n Tokenizing {len(dataset)} examples...")

    def tokenize(example: dict) -> dict:
        text = example["text"]
        tokens = tokenizer.encode(text)
        max_len = cfg.get("max_seq_length", 512)
        if len(tokens) > max_len:
            tokens = tokens[:max_len]
        return {"input_ids": tokens}

    tokenized = [tokenize(ex) for ex in dataset]

    avg_len = sum(len(t["input_ids"]) for t in tokenized) // len(tokenized)
    print(f" Done. Avg length: {avg_len} tokens")

    # ---- Training args ----
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    batch_size = cfg.get("batch_size", 2)
    num_epochs = cfg.get("num_epochs", 3)

    training_args = TrainingArgs(
        batch_size=batch_size,
        iters=(len(tokenized) * num_epochs) // batch_size,
        val_batches=0,
        steps_per_report=cfg.get("log_every", 10),
        steps_per_eval=9999,
        save_every=cfg.get("save_every", 100),
        adapter_path=str(output_path),
        max_seq_length=cfg.get("max_seq_length", 512),
        grad_checkpoint=cfg.get("grad_checkpoint", True),
    )

    # ---- Optimizer ----
    lr = cfg.get("learning_rate", 2e-4)
    optimizer = optim.AdamW(learning_rate=lr)

    # ---- Logger ----
    logger = TrainingLogger(
        log_dir=str(output_path / "logs"),
        use_wandb=cfg.get("use_wandb", False),
        project=cfg.get("wandb_project", "grimai"),
    )

    # ---- Train ----
    print(f"\n Starting training...")
    print(f" Epochs:     {num_epochs}")
    print(f" Batch size: {batch_size}")
    print(f" LR:         {lr}")
    print(f" Output:     {output_path}")
    print(f"\n Watch the loss go down.\n")

    start = time.time()

    try:
        train(
            model=model,
            tokenizer=tokenizer,
            args=training_args,
            train_dataset=tokenized,
            val_dataset=[],
        )
    except KeyboardInterrupt:
        print("\n\n Training interrupted. Partial adapter saved at:", output_path)

    elapsed = time.time() - start
    logger.finish()

    print(f"\n Training complete!")
    print(f" Time: {format_time(elapsed)}")
    print(f" Adapter saved to: {output_path}")

    print(f"\n Next step:")
    print(f"   python scripts/test_model.py \\")
    print(f"     --adapter {args.output} \\")
    print(f'     --prompt "My business idea is a subscription box for office supplies"')


if __name__ == "__main__":
    main()