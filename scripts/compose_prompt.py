#!/usr/bin/env python3
"""
Compose a ready-to-use system prompt for hashline from base + model-specific delta.

Usage (from source):
    python scripts/compose_prompt.py --model gemini

Usage (after pip install):
    python -c "from hashline.scripts.compose_prompt import compose; print(compose('kimi'))"
    # or copy the script

Models: deepseek, gemini, kimi
"""

import argparse

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


def compose(model: str) -> str:
    """Return the full composed prompt for the given model."""
    model = model.lower()
    if model not in DELTAS:
        raise ValueError(f"Unknown model: {model}. Choose from: {list(DELTAS)}")
    delta = DELTAS[model]
    return BASE + "\n" + delta + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compose hashline system prompt")
    parser.add_argument(
        "--model",
        required=True,
        choices=list(DELTAS.keys()),
        help="Target model (deepseek, gemini, kimi)",
    )
    args = parser.parse_args()

    prompt = compose(args.model)
    print(prompt)
    print("\n# --- End of prompt --- ")
    print(f"# Use this with {args.model}")