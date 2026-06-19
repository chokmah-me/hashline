# hashline

Reliable hash-anchored line edit harness for LLM coding agents.

Based on the technique described in https://blog.can.ac/2026/02/12/the-harness-problem/

## Install

```bash
pip install git+https://github.com/chokmah-me/hashline.git
```

## Quick start

```bash
# Ground an edit
hashline read src/module.py

# Apply a compact patch using the anchors the model saw
hashline apply << 'EOF'
[src/module.py#ABCD]
SWAP 12.=14:
+    better implementation
EOF
```

Full rules for agents are in `prompt.md`.

## Claude Code

Run your `session-recall-cc` commands first, then use `hashline` for edits.

You can use the built-in injector:

```bash
python -m hashline.inject_claude --help
# or after install
hashline inject-claude .
```