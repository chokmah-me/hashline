"""Prompt composition utilities for hashline.

Usage:
    from hashline.compose import compose_prompt
    prompt = compose_prompt("gemini")
"""

BASE = '''You are using the hashline edit harness.

When editing files:
- Always start by calling the read tool (or `hashline read`) to get the current [PATH#TAG] view.
- Use only the exact line numbers and [PATH#TAG] from the most recent read output.
- Output patches in the exact hashline format.
- The patch body must contain ONLY new content (lines starting with +).
- Never reproduce old content from the file in the patch body.
- Re-read the file after every successful apply before making further changes.
'''

DELTAS = {
    "deepseek": "Strictly use ONLY the line numbers and [PATH#TAG] shown in the most recent hashline read. Do not use any numbers from memory or previous turns.",
    "gemini": "CRITICAL: Never include any original/old lines in your + body. Only write the final desired content. The range (SWAP/DEL) removes the old text.",
    "kimi": "Be concise. Use precise anchors from the current read. You are allowed to output multi-hunk patches in one go.",
}


def compose_prompt(model: str) -> str:
    """Return a ready-to-use system prompt for the given model."""
    model = model.lower().strip()
    if model not in DELTAS:
        raise ValueError(f"Unsupported model '{model}'. Choose from: {list(DELTAS.keys())}")
    return BASE.strip() + "\n\n" + DELTAS[model]


def list_models() -> list[str]:
    return list(DELTAS.keys())
