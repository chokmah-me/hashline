""Hashline CLI.

Usage examples (from any agent terminal):
  python -m hashline read src/foo.py
  hashline read src/foo.py          # after pip install
  hashline apply < patch.hln

Snapshots prefer user-home cache (~/.hashline/snapshots) so Claude Code
session-recall-cc is not polluted, while edits still touch real source files.
"""

import argparse
import sys
from pathlib import Path

from .hashline import (
    apply_patch,
    compute_tag,
    read_hashed,
)

# (Implementation continues - full file will be pushed)
def main(argv=None):
    # stub for initial push; full implementation follows in next commit
    print("hashline CLI (initial import)")

if __name__ == "__main__":
    main()