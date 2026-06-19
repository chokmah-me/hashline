# hashline

**Hash-anchored edit harness for LLM coding agents.**

Stable, verifiable line-based edits using short content hashes instead of fragile exact string replace.

**Supported / well-tested models:**
- Grok
- Claude Code
- DeepSeek v4
- Gemini
- Kimi k2 2.7

## Installation

```bash
pip install git+https://github.com/chokmah-me/hashline.git
```

## Quick Usage

```bash
hashline read path/to/file.py
hashline apply < my.patch
```

## Model-Specific Prompt Variants

Different models follow the hashline format best with slightly different reminders.

See the `prompts/` directory:

- `prompts/base.md` — core rules
- `prompts/deepseek.md`
- `prompts/gemini.md`
- `prompts/kimi.md`
- `prompts/claude.md`
- `prompts/grok.md`

You can copy the relevant variant into your system prompt or agent instructions.

## For Claude Code

```bash
python -m hashline.inject_claude .
```

## CI

Tests run on every push/PR via GitHub Actions (see `.github/workflows/ci.yml`).

## Development
```bash
git clone https://github.com/chokmah-me/hashline
pip install -e "[test]"
pytest
```