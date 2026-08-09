"""
ui.py — Streamlit UI for Grim.

Run it:
  streamlit run app/ui.py

Set the adapter path via environment variable or edit ADAPTER_PATH below.
  GRIM_ADAPTER=models/adapters/grim-v1 streamlit run app/ui.py
"""

import os
import sys
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.infer.engine import GrimEngine

# --- Config ---
ADAPTER_PATH = os.getenv("GRIM_ADAPTER", "models/adapters/grim-v1")

EXAMPLE_PROMPTS = [
    "Roast my startup idea: an app that connects dog owners",
    "I keep procrastinating on my side project. Be brutal.",
    "I want to quit my job and freelance full time. What am I missing?",
    "My plan is to learn ML in 3 months while working full time.",
    "Show me what happens in 6 months if I keep skipping the gym",
]

# --- Page config ---
st.set_page_config(
    page_title="grimai",
    page_icon="☠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Custom CSS ---
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  .stApp {
    background-color: #F5F3EE;
  }

  h1 {
    font-family: 'Instrument Serif', serif;
    font-weight: 400;
    font-size: 2.6rem !important;
    color: #1A1917;
    letter-spacing: -0.5px;
  }

  h1 em {
    color: #9A9690;
    font-style: italic;
  }

  .subtitle {
    color: #7A7770;
    font-size: 0.95rem;
    font-weight: 300;
    margin-bottom: 2rem;
  }

  .stTextArea textarea {
    background: #FFFFFF !important;
    border: 0.5px solid rgba(0,0,0,0.12) !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    color: #1A1917 !important;
    padding: 1rem !important;
  }

  .stTextArea textarea:focus {
    border-color: rgba(0,0,0,0.3) !important;
    box-shadow: none !important;
  }

  .stButton button {
    background: #1A1917 !important;
    color: #F5F3EE !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 400 !important;
    font-size: 0.9rem !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.15s !important;
  }

  .stButton button:hover {
    opacity: 0.8 !important;
  }

  .response-box {
    background: #FFFFFF;
    border: 0.5px solid rgba(0,0,0,0.1);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-top: 1.5rem;
    font-size: 0.95rem;
    line-height: 1.75;
    color: #1A1917;
    white-space: pre-wrap;
  }

  .section-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    color: #9A9690;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
  }

  .example-chip {
    display: inline-block;
    background: #ECEAE4;
    border-radius: 8px;
    padding: 6px 12px;
    margin: 4px;
    font-size: 0.82rem;
    color: #4A4844;
    cursor: pointer;
  }

  .divider {
    border: none;
    border-top: 0.5px solid rgba(0,0,0,0.1);
    margin: 1.5rem 0;
  }

  /* Dark mode */
  @media (prefers-color-scheme: dark) {
    .stApp { background-color: #0F0E0D; }
    h1 { color: #F0EDE6; }
    .response-box {
      background: #1A1917;
      border-color: rgba(255,255,255,0.08);
      color: #F0EDE6;
    }
    .example-chip { background: #2A2826; color: #A09C96; }
    .stTextArea textarea {
      background: #1A1917 !important;
      color: #F0EDE6 !important;
      border-color: rgba(255,255,255,0.1) !important;
    }
    .stButton button {
      background: #F0EDE6 !important;
      color: #0F0E0D !important;
    }
  }
</style>
""", unsafe_allow_html=True)


# --- Load model (cached so it only loads once) ---
@st.cache_resource(show_spinner=False)
def load_engine():
    engine = GrimEngine(adapter_path=ADAPTER_PATH)
    engine.load()
    return engine


# --- Header ---
st.markdown("<h1>Hey. <em>Be honest.</em><br>What do you want torn apart?</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Grim gives you brutal feedback on ideas, habits, plans, and decisions.<br>No sugarcoating.</p>', unsafe_allow_html=True)

# --- Example prompts ---
st.markdown('<p class="section-label">Try one of these</p>', unsafe_allow_html=True)
cols = st.columns(len(EXAMPLE_PROMPTS))
selected_example = None
for i, prompt in enumerate(EXAMPLE_PROMPTS):
    with cols[i % 3]:
        if st.button(prompt[:40] + "...", key=f"ex_{i}", use_container_width=True):
            selected_example = prompt

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- Input ---
default_text = selected_example if selected_example else ""
user_input = st.text_area(
    label="Your input",
    value=default_text,
    placeholder="Paste your idea, plan, habit, or decision here...",
    height=120,
    label_visibility="collapsed",
)

col1, col2 = st.columns([5, 1])
with col2:
    submit = st.button("Ask Grim →", use_container_width=True)

# --- Generate response ---
if submit and user_input.strip():
    with st.spinner("Grim is thinking..."):
        try:
            engine = load_engine()
        except Exception as e:
            st.error(f"Failed to load model: {e}")
            st.info("Make sure training is complete and the adapter exists at: " + ADAPTER_PATH)
            st.stop()

    # Stream the response
    response_placeholder = st.empty()
    full_response = ""

    response_placeholder.markdown(
        f'<div class="response-box">▌</div>',
        unsafe_allow_html=True,
    )

    for token in engine.stream(user_input):
        full_response += token
        response_placeholder.markdown(
            f'<div class="response-box">{full_response}▌</div>',
            unsafe_allow_html=True,
        )

    # Final response without cursor
    response_placeholder.markdown(
        f'<div class="response-box">{full_response}</div>',
        unsafe_allow_html=True,
    )

elif submit and not user_input.strip():
    st.warning("Type something first.")

# --- Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center; color:#9A9690; font-size:0.8rem; font-weight:300;">'
    'grimai · runs locally · no data leaves your machine'
    '</p>',
    unsafe_allow_html=True,
)
