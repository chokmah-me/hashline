#!/usr/bin/env python3
"""
Compose a ready-to-use system prompt for hashline from base + model-specific delta.

Usage:
    # From the repo
    python scripts/compose_prompt.py --model gemini

    # After `pip install hashline`
    hashline compose --model kimi
"""

import argparse

try:
    from hashline.compose import compose_prompt, list_models
except ImportError:
    # Fallback for running directly from source tree
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hashline.compose import compose_prompt, list_models  # type: ignore


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compose hashline system prompt")
    parser.add_argument(
        "--model",
        required=True,
        choices=list_models(),
        help="Target model",
    )
    args = parser.parse_args()

    prompt = compose_prompt(args.model)
    print(prompt)
    print(f"\n# --- Copy above for use with {args.model} ---")