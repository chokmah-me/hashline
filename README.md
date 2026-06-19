# hashline

**Hash-anchored edit harness for LLM coding agents.**

Stable, verifiable line-based edits using short content hashes instead of fragile exact string replace.

Works especially well with:
- Grok
- Claude Code
- **DeepSeek v4**
- **Gemini**
- **Kimi k2 2.7** (Moonshot)

## Installation

```bash
pip install git+https://github.com/chokmah-me/hashline.git
```

After install you get the `hashline` command.

## Basic Usage

```bash
hashline read src/foo.py
hashline apply < my.patch
```

See `prompt.md` for the exact patch language the model should use.

## Model-Specific Tips

### DeepSeek v4
DeepSeek follows structured formats well. Use explicit "Use the exact [path#TAG] format from the read output" in your system prompt.

### Gemini
Gemini can be sensitive to whitespace. Always remind it: "Do not reproduce old content. Only output + lines for the ranges."

### Kimi k2 2.7
Kimi is excellent at following the compact patch syntax. It benefits greatly from the token savings.

## For Claude Code Users
Run your normal session-recall first, then use `hashline` for edits.

Use the injector:
```bash
python -m hashline.inject_claude .
```

## Development
```bash
git clone https://github.com/chokmah-me/hashline
git clone ...
pip install -e .
```