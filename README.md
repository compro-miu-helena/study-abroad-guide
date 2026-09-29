# Explora Study Abroad Guide (Python/Gradio)

Python + Gradio port of the chatbot from
[helenapedro/study-abroad-guide](https://github.com/compro-miu-helena/study-abroad-guide.git):
a study-abroad guide giving general information about studying in the United States.

## Files

- `main.ipynb` — the assignment notebook
- `prompts/chatbot.txt` — system-prompt template (role, goal, context, constraints, data, output, success criteria)
- `prompts/explora.md` — project rules injected via `{{projectInfo}}`
- `.env.example` — copy to `.env` and add your OpenAI API key
- `ui-screenshot.png` — capture after launching

## Setup

1. `pip install openai python-dotenv gradio`
2. Get an OpenAI API key: platform.openai.com → Billing → add **$5** credit → API keys → create key. (ChatGPT Plus does not include API credit; this assignment costs a few cents on `gpt-4o-mini`.)
3. `cp .env.example .env`, paste the key.
4. Open the notebook in Cursor and run all cells. Run the last cell (`demo.launch(share=True)`) near submission time — links expire after ~72h.

## Submission

- Sakai: the Gradio shareable link (`*.gradio.live`).
- Plus the GitHub repo URL (notebook + files) or the notebook exported as `.html`.
- Keep output cells visible — do not clear them.
