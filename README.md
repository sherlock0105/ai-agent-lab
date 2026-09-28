# ai-agent-lab

AI agent practice projects. Each lesson has its own folder and dependencies.

## Projects

- [basic_translator](basic_translator/): Translate English into Korean and Greek with CrewAI.

## Run the translator (PowerShell)

Install Python 3.13 and uv, then run:

```powershell
cd basic_translator
Copy-Item .env.example .env
# Set OPENAI_API_KEY in .env before running.
uv run main.py
```

The program calls the OpenAI API and may incur usage charges.
Keep .env and .venv out of Git.

## Add another lesson

Create a sibling folder next to basic_translator, with its own main.py,
pyproject.toml, and uv.lock. Run uv commands from that lesson folder.
