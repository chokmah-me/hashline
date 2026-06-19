"""Hashline CLI.

Install with: pip install git+https://github.com/chokmah-me/hashline.git

Usage:
  hashline read path/to/file.py
  hashline apply < patch.txt
  hashline tag path/to/file.py
  hashline compose --model gemini
"""

import argparse
import sys
from pathlib import Path

from .hashline import (
    apply_patch,
    compute_tag,
    read_hashed,
    read_raw,
    InMemorySnapshotStore,
)
from .compose import compose_prompt, list_models


def _force_utf8_io():
    # Files routinely contain non-ASCII (emoji, math symbols). On Windows the
    # default console encoding is cp1252, so printing a hashed view crashes with
    # UnicodeEncodeError and reading a piped patch silently mangles non-ASCII
    # (double-encoding em-dashes etc.). Reconfigure stdin/stdout/stderr to UTF-8.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def main(argv=None):
    _force_utf8_io()
    parser = argparse.ArgumentParser(
        prog="hashline", description="Hash-anchored LLM edit harness"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_read = sub.add_parser("read", help="Print hashed view with [path#TAG]")
    p_read.add_argument("path")
    p_read.set_defaults(func=cmd_read)

    p_apply = sub.add_parser("apply", help="Apply a hashline patch")
    p_apply.add_argument("--patch-file", "-p")
    p_apply.add_argument("--dry-run", action="store_true")
    p_apply.add_argument(
        "--no-strict",
        dest="strict",
        action="store_false",
        help="Apply valid hunks and warn (instead of rejecting) on malformed patch lines",
    )
    p_apply.set_defaults(func=cmd_apply, strict=True)

    p_tag = sub.add_parser("tag", help="Print current 4-hex content tag")
    p_tag.add_argument("path")
    p_tag.set_defaults(func=cmd_tag)

    p_compose = sub.add_parser(
        "compose", help="Compose system prompt from base + model delta"
    )
    p_compose.add_argument(
        "--model", required=True, choices=list_models(), help="Target model"
    )
    p_compose.set_defaults(func=cmd_compose)

    args = parser.parse_args(argv)
    args.func(args)


def cmd_read(args):
    text = read_hashed(args.path)
    print(text)


def cmd_apply(args):
    if args.patch_file:
        patch_text = Path(args.patch_file).read_text(encoding="utf-8")
    else:
        patch_text = sys.stdin.read()

    if not patch_text.strip():
        print("No patch provided", file=sys.stderr)
        sys.exit(2)

    store = InMemorySnapshotStore()
    try:
        res = apply_patch(
            patch_text, store=store, dry_run=args.dry_run, strict=args.strict
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    for w in res.warnings:
        print(f"warning: {w}", file=sys.stderr)

    for sec in res.sections:
        print(sec)

    if args.dry_run:
        print("(dry-run)")

    if any(s.get("op") in ("stale", "error") for s in res.sections):
        sys.exit(1)


def cmd_tag(args):
    raw = read_raw(Path(args.path))
    print(compute_tag(raw))


def cmd_compose(args):
    prompt = compose_prompt(args.model)
    print(prompt)
    print("\n# Copy the above into your system prompt for", args.model)


if __name__ == "__main__":
    main()
