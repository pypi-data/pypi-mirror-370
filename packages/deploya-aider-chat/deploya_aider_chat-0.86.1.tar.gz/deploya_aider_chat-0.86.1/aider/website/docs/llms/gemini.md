---
parent: Connecting to LLMs
nav_order: 300
---

# Gemini

You'll need a [Gemini API key](https://aistudio.google.com/app/u/2/apikey).

<<<<<<< HEAD
```
python -m pip install -U deploya-aider-chat
=======
First, install aider:
>>>>>>> upstream/main

{% include install.md %}

<<<<<<< HEAD
# Or with pipx...
pipx inject deploya-aider-chat google-generativeai
=======
Then configure your API keys:
>>>>>>> upstream/main

```bash
export GEMINI_API_KEY=<key> # Mac/Linux
setx   GEMINI_API_KEY <key> # Windows, restart shell after setx
```

Start working with aider and Gemini on your codebase:


```bash
# Change directory into your codebase
cd /to/your/project

# You can run the Gemini 2.5 Pro model with this shortcut:
aider --model gemini

# You can run the Gemini 2.5 Pro Exp for free, with usage limits:
aider --model gemini-exp

# List models available from Gemini
aider --list-models gemini/
```

You may need to install the `google-generativeai` package. 

```bash
# If you installed with aider-install or `uv tool`
uv tool run --from aider-chat pip install google-generativeai

# Or with pipx...
pipx inject aider-chat google-generativeai

# Or with pip
pip install -U google-generativeai
```
