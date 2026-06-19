# hashline

Reliable, hash-anchored edit harness for LLM agents.

Implements the technique from https://blog.can.ac/2026/02/12/the-harness-problem/

## Install

```bash
pip install hashline
# or from source
git clone https://github.com/chokmah-me/hashline
cd hashline
pip install -e .
```

## Usage

```bash
# Get a stable view with anchors
hashline read path/to/file.py

# Apply an edit using the anchors (compact)
hashline apply << 'H'
[path#TAG]
SWAP 5.=5:
+    improved line
H
```

See `prompt.md` for the full rules the agent should follow.

## For Claude Code

Run `session-recall-cc` first, then use the `hashline` commands.

The included `hashline inject-claude` (or the script) can update your CLAUDE.md files.