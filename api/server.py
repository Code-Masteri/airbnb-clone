"""
server.py — Tiny FastAPI server that wraps the MLX model.
Next.js frontend calls this at http://localhost:8000/chat

Run it:
  cd grimai
  source .venv/bin/activate
  pip install fastapi uvicorn
  python ../grimai-api/server.py
"""

import subprocess
import sys
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """You are Grim — a brutally honest AI advisor.

Your job is to give people the feedback they actually need, not the validation they want.

Always respond in this exact structure:

THE VERDICT
One or two sentences. The honest bottom line. No softening.

WHAT'S BROKEN
- Bullet point 1
- Bullet point 2
- Bullet point 3

IF YOU DO NOTHING
- 1 week: what happens
- 1 month: what happens
- 6 months: what happens

THE FIX
- Step 1
- Step 2
- Step 3

THE ONE THING
One sentence. The single most important action right now.

*Closing line — punchy and memorable.*

Rules: No empty praise. Keep it under 400 words. Be direct."""

MODEL = "meta-llama/Llama-3.2-3B-Instruct"
ADAPTER = "models/adapters/grim-v1"

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    prompt = (
        f"<|system|>\n{SYSTEM_PROMPT}\n"
        f"<|user|>\n{req.message}\n"
        f"<|assistant|>\n"
    )

    def generate():
        cmd = [
            sys.executable, "-m", "mlx_lm", "generate",
            "--model", MODEL,
            "--adapter-path", ADAPTER,
            "--prompt", prompt,
            "--max-tokens", "500",
            "--temp", "0.7",
        ]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            cwd=str(Path(__file__).parent.parent / "grimai"),
        )
        skip_prompt = True
        for line in proc.stdout:
            if skip_prompt and "<|assistant|>" in line:
                skip_prompt = False
                continue
            if skip_prompt:
                continue
            for stop in ["<|end|>", "<|user|>", "<|system|>", "==========", "Prompt:"]:
                if stop in line:
                    proc.kill()
                    return
            yield line
        proc.wait()

    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL, "adapter": ADAPTER}

if __name__ == "__main__":
    import uvicorn
    print("\n Grim API running at http://localhost:8000")
    print(" Next.js frontend should be at http://localhost:3000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
