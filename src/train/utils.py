"""
utils.py — Training utilities: logging, checkpointing, metrics.
"""

import json
import time
from pathlib import Path
from datetime import datetime


class TrainingLogger:
    """
    Logs training metrics to a JSONL file and optionally to Weights & Biases.
    Each line in the log file is one training step.
    """

    def __init__(self, log_dir: str, use_wandb: bool = False, project: str = "grimai"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "training_log.jsonl"
        self.use_wandb = use_wandb
        self.start_time = time.time()

        if use_wandb:
            try:
                import wandb
                wandb.init(project=project, name=f"grim-{datetime.now().strftime('%m%d-%H%M')}")
                self.wandb = wandb
                print(" Weights & Biases logging enabled")
                print(f" Dashboard: {wandb.run.get_url()}")
            except ImportError:
                print("[!] wandb not installed. Run: pip install wandb")
                self.use_wandb = False
            except Exception as e:
                print(f"[!] wandb init failed: {e}")
                print("    Continuing without W&B logging.")
                self.use_wandb = False

    def log(self, step: int, loss: float, lr: float = None):
        """Log a training step."""
        elapsed = time.time() - self.start_time
        record = {
            "step": step,
            "loss": round(loss, 6),
            "elapsed_seconds": round(elapsed, 1),
        }
        if lr is not None:
            record["lr"] = lr

        with open(self.log_file, "a") as f:
            f.write(json.dumps(record) + "\n")

        if self.use_wandb:
            self.wandb.log(record, step=step)

    def finish(self):
        if self.use_wandb:
            self.wandb.finish()


def format_time(seconds: float) -> str:
    """Convert seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


def count_parameters(model) -> dict:
    """Count total and trainable parameters in the model."""
    try:
        import mlx.core as mx
        total = sum(p.size for _, p in model.parameters() if isinstance(p, mx.array))
        # Trainable are the LoRA layers
        trainable = sum(
            p.size for name, p in model.parameters()
            if isinstance(p, mx.array) and "lora" in name.lower()
        )
        return {
            "total": total,
            "trainable": trainable,
            "trainable_pct": round(100 * trainable / total, 2) if total > 0 else 0,
        }
    except Exception:
        return {"total": 0, "trainable": 0, "trainable_pct": 0}
