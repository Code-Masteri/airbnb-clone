"""
server.py — FastAPI server for grimai.
Place this in the root of your grimai folder.
Run: 
  source .venv/bin/activate
  pip install fastapi uvicorn mlx-lm
  python server.py
"""
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from mlx_lm import load, stream_generate

# Configuration
MODEL_PATH = "meta-llama/Llama-3.2-3B-Instruct"
ADAPTER_PATH = "models/adapters/grim-v1"

SYSTEM_PROMPT = """You are Grim — a brutally honest AI advisor. 
Your job is to give people the feedback they actually need, not the validation they want. 
Always respond in this exact structure:
THE VERDICT: Bottom line.
WHAT'S BROKEN: Bullet points.
IF YOU DO NOTHING: 1 week, 1 month, 6 months outlook.
THE FIX: Action steps.
THE ONE THING: Single most important action.
*Closing line in italics.*"""

# Global state for model
state = {"model": None, "tokenizer": None}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load model
    print(f"\n Loading Grim model: {MODEL_PATH}...")
    try:
        model, tokenizer = load(MODEL_PATH, adapter_path=ADAPTER_PATH)
        state["model"] = model
        state["tokenizer"] = tokenizer
        print(" Model loaded and ready.\n")
    except Exception as e:
        print(f"[!] Failed to load model: {e}")
        sys.exit(1)
    yield
    # Shutdown: Clean up if necessary
    state.clear()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "model": MODEL_PATH, 
        "loaded": state["model"] is not None
    }

@app.post("/chat")
async def chat(req: ChatRequest):
    model = state["model"]
    tokenizer = state["tokenizer"]
    
    if model is None:
        return JSONResponse({"error": "Model not loaded"}, status_code=503)

    # Use the official chat template for Llama-3.2
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": req.message.strip()}
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    def generate():
        try:
            # mlx_lm.stream_generate is a sync generator
            # For Llama-3, stop tokens are usually handled by the tokenizer/template
            for response in stream_generate(
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                max_tokens=600,
                temp=0.7,
                top_p=0.9,
            ):
                yield response
        except Exception as e:
            yield f"\n\n[ERROR]: {str(e)}"

    # We use a standard generator here. FastAPI will automatically 
    # run this in a threadpool to avoid blocking the event loop.
    return StreamingResponse(generate(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
