```
  ██████╗ ██████╗ ██╗███╗   ███╗ █████╗ ██╗
 ██╔════╝ ██╔══██╗██║████╗ ████║██╔══██╗██║
 ██║  ███╗██████╔╝██║██╔████╔██║███████║██║
 ██║   ██║██╔══██╗██║██║╚██╔╝██║██╔══██║██║
 ╚██████╔╝██║  ██║██║██║ ╚═╝ ██║██║  ██║██║
  ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝

  The AI that tells you the truth you don't want to hear.
```

> Drop an idea, a plan, a habit, or a life decision.  
> Grim won't sugarcoat it.

---

## What is this?

grimai is a locally fine-tuned AI advisor trained to give brutally honest, structured feedback on your ideas, habits, decisions, and plans — with a roadmap to actually fix them.

Built on Llama 3.2 3B fine-tuned with QLoRA via MLX on Apple Silicon. No cloud costs. No API keys. Runs entirely on your MacBook.

---

## Stack

| Layer          | Tool                             |
| -------------- | -------------------------------- |
| Base model     | meta-llama/Llama-3.2-3B-Instruct |
| Fine-tuning    | MLX-LM + LoRA (Apple Silicon)    |
| Synthetic data | Ollama (local generation)        |
| UI             | Streamlit                        |
| Logging        | Weights and Biases (free)        |

---

## Quickstart — read every step, do not skip

### Step 0 — What you need before anything

- MacBook with M1/M2/M3 chip (M1 Pro is perfect)
- macOS 13 Ventura or later
- About 10GB free disk space
- Terminal app: press Cmd+Space, type Terminal, hit Enter

---

### Step 1 — Install Homebrew

Homebrew is a package manager — like an App Store for developer tools.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Close Terminal and reopen it. Then verify:

```bash
brew --version
# Should show: Homebrew 4.x.x
```

---

### Step 2 — Install Python 3.11

```bash
brew install python@3.11
python3.11 --version
# Should show: Python 3.11.x
```

---

### Step 3 — Install Ollama

Ollama runs AI models locally. We use it to generate our training data.

```bash
brew install ollama
```

Start it in the background:

```bash
ollama serve &
```

Pull the model:

```bash
ollama pull llama3.2:3b
# Downloads ~2GB — grab a coffee
```

Test it:

```bash
ollama run llama3.2:3b "Say: I am ready."
# Press Ctrl+C to exit after it replies
```

---

### Step 4 — Clone and set up the project

```bash
git clone https://github.com/yourusername/grimai.git
cd grimai

# Create isolated Python environment
python3.11 -m venv .venv
source .venv/bin/activate
# Your terminal now shows (.venv) — that means it's active

# Install everything
pip install -r requirements.txt
# Takes 2-5 minutes
```

---

### Step 5 — Generate training data

Creates 500 training examples using Ollama locally. No internet needed.

```bash
python scripts/gen_synthetic.py --count 500 --output data/synthetic/grim_train.jsonl
```

Check what was made:

```bash
head -n 1 data/synthetic/grim_train.jsonl
```

---

### Step 6 — Format the data

```bash
python src/data/formatter.py \
  --input data/synthetic/grim_train.jsonl \
  --output data/processed/train.jsonl
```

---

### Step 7 — Download the base model

You need a free Hugging Face account. Accept the Llama 3.2 license at:
https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct

Then login:

```bash
pip install huggingface_hub
huggingface-cli login
# Paste your HF token when prompted
```

Download the model:

```bash
python src/data/loader.py
# Downloads ~6GB — this takes a while
```

---

### Step 8 — Fine-tune the model

```bash
python src/train/qlora.py \
  --config configs/training.yaml \
  --data data/processed/train.jsonl \
  --output models/adapters/grim-v1
```

On M1 Pro with 500 examples this takes about 30-60 minutes. Watch the loss go down. That is the model getting smarter.

Optional: log to Weights and Biases dashboard (looks amazing):

```bash
wandb login
# Free account at wandb.ai
```

---

### Step 9 — Test your model

```bash
python scripts/test_model.py \
  --adapter models/adapters/grim-v1 \
  --prompt "My business idea is a subscription box for office supplies"
```

Grim should tear it apart constructively.

---

### Step 10 — Launch the UI

```bash
streamlit run app/ui.py
# Opens at http://localhost:8501
```

---

## Project structure

```
grimai/
├── README.md
├── .gitignore
├── requirements.txt
├── configs/
│   ├── training.yaml        # hyperparameters
│   └── inference.yaml       # generation settings
├── data/
│   ├── raw/                 # never committed
│   ├── processed/           # never committed
│   └── synthetic/           # never committed
├── src/
│   ├── data/
│   │   ├── loader.py        # downloads base model
│   │   ├── cleaner.py       # filters bad examples
│   │   └── formatter.py     # formats into chat template
│   ├── train/
│   │   ├── qlora.py         # main training script
│   │   └── utils.py         # logging and checkpoints
│   ├── infer/
│   │   ├── chat.py          # CLI chat interface
│   │   └── engine.py        # loads adapter and runs inference
│   └── prompts/
│       └── system.py        # Grim's personality
├── scripts/
│   ├── gen_synthetic.py     # generates training data
│   └── test_model.py        # quick post-training test
├── models/
│   └── adapters/            # never committed
├── notebooks/
│   └── explore.ipynb        # data exploration
└── app/
    └── ui.py                # Streamlit UI
```

---

## Tips

- Never push data/, models/, or .venv/ to GitHub — they are in .gitignore
- If training crashes, check RAM: open Activity Monitor and look at Memory tab
- If Ollama stops working, restart it: `ollama serve &`
- The adapter is only ~100MB. The base model is the large one and lives in ~/.cache/

---

## License

MIT

python scripts/test_model.py \
 --adapter models/adapters/grim-v1 \
 --prompt "My startup idea is a subscription box for office supplies"

# Or run all built-in tests:

python scripts/test_model.py --adapter models/adapters/grim-v1 --all

# Chatt

python src/infer/chat.py --adapter models/adapters/grim-v1

# UI

streamlit run app/ui.py

# Opens at http://localhost:8501
