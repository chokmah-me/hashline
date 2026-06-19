#!/usr/bin/env python3
"""
Safe injector for the hashline block into CLAUDE.md files.

Usage after pip install:
  python -m hashline.inject_claude .

It looks for session-recall-cc or session-recall END markers and inserts
instructions right after them. Idempotent, creates .bak.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Optional

SNIPPET = """<!-- hashline:v1 START -->
## Hashline edit harness (use for all file modifications)

**After running `session-recall-cc`, use the hashline harness for edits.**

```bash
python -m hashline read path/to/file.py
python -m hashline apply <<\'HLP\'
...
HLP
```

See the hashline package for full rules.
<!-- hashline:v1 END -->
"""

RECALL_CC_END = re.compile(r"<!--\s*session-recall-cc:v1\s+END\s*-->", re.IGNORECASE)
RECALL_V1_END = re.compile(r"<!--\s*/session-recall:v1\s*-->", re.IGNORECASE)
HASHLINE_MARKER = re.compile(r"<!--\s*hashline:v1\s+START", re.IGNORECASE)


def find_recall_end(text: str) -> Optional[int]:
    m = RECALL_CC_END.search(text)
    if m:
        return m.end()
    m = RECALL_V1_END.search(text)
    if m:
        return m.end()
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=["."])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    for root in args.paths:
        for p in Path(root).rglob("CLAUDE.md"):
            text = p.read_text(encoding="utf-8")
            if HASHLINE_MARKER.search(text) and not args.force:
                print(f"SKIP (already has hashline): {p}")
                continue
            end = find_recall_end(text)
            if not end:
                print(f"SKIP (no recall block): {p}")
                continue
            new_text = text[:end] + "\n\n" + SNIPPET + "\n" + text[end:]
            if args.dry_run:
                print(f"DRY-RUN would update: {p}")
                continue
            bak = p.with_suffix(p.suffix + ".bak")
            if not bak.exists():
                bak.write_text(text, encoding="utf-8")
            p.write_text(new_text, encoding="utf-8")
            print(f"UPDATED: {p}")


if __name__ == "__main__":
    main()
