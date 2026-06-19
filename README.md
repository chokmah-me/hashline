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

## Grok Skill Example Usage

The full ready-to-use Grok skill (with model-aware Example Sessions for Grok + DeepSeek/Gemini/Kimi) is available at:

- Local: `~/.grok/skills/hashline/SKILL.md`
- In this repo: `docs/SKILL.md`

It includes exact `hashline read` outputs and the precise patch blocks an agent should emit.

## GitHub Actions / CI

Separate jobs on every push/PR:
- `test`: pytest across Python 3.8-3.13 + CLI check
- `lint`: ruff check + format
- `typecheck`: mypy
- `demo`: end-to-end `read` → (model-style patch) → `apply` for base case + Gemini (see `tests/harness_demo.py`)

See `.github/workflows/ci.yml`.

## For Claude Code Users

```bash
python -m hashline.inject_claude .
```

## Development

```bash
git clone https://github.com/chokmah-me/hashline
pip install -e ".[dev]"
# lint
ruff check .
ruff format --check .
# typecheck
mypy hashline
# test + demo
pytest
python tests/harness_demo.py --models base gemini
```