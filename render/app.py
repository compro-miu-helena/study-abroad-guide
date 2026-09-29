"""Explora — Study Abroad Guide (CS529 Day 2 assignment).
Generated from main.ipynb for Hugging Face Spaces deployment.
"""

from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

import warnings
warnings.filterwarnings("ignore", message=".*IProgress not found.*")
import gradio as gr
print(f"Gradio {gr.__version__} loaded.")

### API key config (on Spaces, set OPENAI_API_KEY as a Secret)

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
    print("API key found.")
    client = OpenAI(api_key=OPENAI_API_KEY, timeout=20.0)
else:
    print("OPENAI_API_KEY not set — add it as a Secret in the Space settings.")
    client = None

with open("prompts/chatbot.txt", encoding="utf-8") as f:
    template = f.read()
with open("prompts/explora.md", encoding="utf-8") as f:
    project_info = f.read()

system_prompt = (
    template
    .replace("{{projectInfo}}", project_info)
)

assert "{{" not in system_prompt, "Unsubstituted placeholder left in the system prompt!"
print(f"System prompt built: {len(system_prompt)} characters, no placeholders left.")
print("---- preview ----")
print(system_prompt[:900] + "...")

### Input validation
MAX_MESSAGE_LENGTH = 1000

def validate_input(message):
    """Validate a user message. Returns (ok, text_or_error)."""
    if message is None:
        return False, "⚠️ Please type a message first."
    text = str(message).strip()
    if not text:
        return False, "⚠️ Your message is empty — try e.g. 'What is campus life like at US universities?'"
    if len(text) > MAX_MESSAGE_LENGTH:
        return False, f"⚠️ Message too long ({len(text)} chars). Please keep it under {MAX_MESSAGE_LENGTH} characters."
    return True, text


# Self-test — no API key needed
cases = [
    ("", False),
    ("   ", False),
    (None, False),
    ("What scholarships exist for international students?", True),
    ("  hello  ", True),
    ("x" * 1001, False),
    ("x" * 1000, True),
]
for raw, expected in cases:
    ok, out = validate_input(raw)
    label = "PASS" if ok == expected else "FAIL"
    preview = repr(str(raw)[:30])
    print(f"{label}: input={preview} -> ok={ok} | {out[:75]}")
    assert ok == expected, f"Validation failed for {preview!r}"
print("\nAll validation tests passed ✅")

## Chat logic

MODEL = "gpt-4o-mini"

def chat(message, history):
    """history: list of {"role": "user"|"assistant", "content": str} (Gradio messages format)."""
    ok, result = validate_input(message)
    if not ok:
        return result  # friendly validation message, no API call spent
    if client is None:
        return "⚠️ The OpenAI API key isn't configured. Add OPENAI_API_KEY to your .env file and re-run the setup cell."
    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": h["role"], "content": h["content"]} for h in (history or [])]
    messages.append({"role": "user", "content": result})
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=200,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        msg = str(e).lower()
        if "authentication" in type(e).__name__.lower() or "invalid_api_key" in msg or "unauthorized" in msg:
            return "⚠️ The API key was rejected. Check that OPENAI_API_KEY in your .env file is valid and has credits."
        return "⚠️ Sorry, the assistant service didn't respond. Please try again in a moment."

## Gradio UI

import inspect
_chatbot_kwargs = {"label": "Chat", "height": 420}
# Gradio 5.x needs type="messages" for dict-style history; Gradio 6+ dropped the parameter.
if "type" in inspect.signature(gr.Chatbot.__init__).parameters:
    _chatbot_kwargs["type"] = "messages"
_blocks_kwargs = {"title": "Explora — Study Abroad Guide"}
_port = int(os.environ.get("PORT", "7860"))
_launch_kwargs = {"server_name": "0.0.0.0", "server_port": _port}
# Gradio 6 moved `theme` from Blocks() to launch().
if int(gr.__version__.split(".")[0]) >= 6:
    _launch_kwargs["theme"] = gr.themes.Soft()
else:
    _blocks_kwargs["theme"] = gr.themes.Soft()
with gr.Blocks(**_blocks_kwargs) as demo:
    gr.Markdown("# 🎓 Explora — Study Abroad Guide\n*General, welcoming information for international students researching study in the United States.*")
    chatbot = gr.Chatbot(**_chatbot_kwargs)
    with gr.Row():
        msg = gr.Textbox(label="Your message", placeholder="e.g., What is campus life like at US universities?", scale=4, max_lines=4)
        send_btn = gr.Button("Send ➤", variant="primary", scale=1)
    clear_btn = gr.Button("🧹 Clear chat")
    gr.Examples(
        examples=[
            "What is campus life like at universities in the United States?",
            "Are there scholarships for international students in the US?",
            "What is the academic environment like at US colleges?",
            "What kind of support do US universities offer international students?",
        ],
        inputs=msg,
        label="Try an example question",
    )
    with gr.Accordion("What can I ask about?", open=False):
        gr.Markdown(
            "- 🎓 Universities & colleges in the **United States**\n"
            "- 🏫 Campus life, academic environment, student experience\n"
            "- 💰 Tuition & scholarships (general information)\n"
            "- 🤝 International student support services\n\n"
            "Out of scope: other countries, visas/immigration advice, and step-by-step application instructions."
        )
    gr.Markdown("*CS529 Day 2 assignment · Python/Gradio port of [helenapedro/study-abroad-guide](https://github.com/compro-miu-helena/study-abroad-guide.git) · Powered by OpenAI gpt-4o-mini*")

    def respond(message, history):
        reply = chat(message, history or [])
        history = (history or []) + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply},
        ]
        return "", history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    send_btn.click(respond, [msg, chatbot], [msg, chatbot])
    clear_btn.click(lambda: ([], ""), None, [chatbot, msg])

print("UI built ✅ — launching...")

demo.launch(**_launch_kwargs)
