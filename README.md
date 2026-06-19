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

See the `prompts/` directory for ready-to-use variants:

- `prompts/base.md`
- `prompts/deepseek.md`
- `prompts/gemini.md`
- `prompts/kimi.md`
- `prompts/claude.md`
- `prompts/grok.md`

Copy the relevant one into your system prompt or agent instructions.

## GitHub Actions / CI

- Tests run automatically on push and pull requests (see `.github/workflows/ci.yml`).
- Matrix: Python 3.8 – 3.13
- Also verifies the `hashline` CLI entry point.

## For Claude Code Users

```bash
python -m hashline.inject_claude .
```

## Development

```bash
git clone https://github.com/chokmah-me/hashline
pip install -e ".[test]"
pytest
```