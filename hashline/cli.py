"""Hashline CLI.

Install with: pip install git+https://github.com/chokmah-me/hashline.git

Usage:
  hashline read path/to/file.py
  hashline apply < patch.txt
  hashline tag path/to/file.py
"""

import argparse
import sys
from pathlib import Path

from .hashline import (
    apply_patch,
    compute_tag,
    read_hashed,
    InMemorySnapshotStore,
)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="hashline", description="Hash-anchored LLM edit harness")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_read = sub.add_parser("read", help="Print hashed view with [path#TAG]")
    p_read.add_argument("path")
    p_read.set_defaults(func=cmd_read)

    p_apply = sub.add_parser("apply", help="Apply a hashline patch")
    p_apply.add_argument("--patch-file", "-p")
    p_apply.add_argument("--dry-run", action="store_true")
    p_apply.set_defaults(func=cmd_apply)

    p_tag = sub.add_parser("tag", help="Print current 4-hex content tag")
    p_tag.add_argument("path")
    p_tag.set_defaults(func=cmd_tag)

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
    res = apply_patch(patch_text, store=store, dry_run=args.dry_run)

    for sec in res.sections:
        print(sec)

    if args.dry_run:
        print("(dry-run)")


def cmd_tag(args):
    raw = Path(args.path).read_text(encoding="utf-8", errors="replace")
    print(compute_tag(raw))


if __name__ == "__main__":
    main()