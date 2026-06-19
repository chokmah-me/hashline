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

# Get a ready-to-use system prompt tailored to a model
hashline compose --model gemini
```

## Compose Prompts for Different Models

```bash
# From installed package
hashline compose --model kimi

# From source
python scripts/compose_prompt.py --model deepseek
```

See `prompts/agent_prompts.md` for the full usage matrix with minimal deltas.

## Model-Specific Prompt Variants

Different models follow the hashline format best with slightly different reminders.

See the `prompts/` directory for ready-to-use variants:

- `prompts/base.md`
- `prompts/deepseek.md`
- `prompts/gemini.md`
- `prompts/kimi.md`
- `prompts/claude.md`
- `prompts/grok.md`

## Grok Skill Example Usage

The full ready-to-use Grok skill (with model-aware Example Sessions) is available at:

- Local: `~/.grok/skills/hashline/SKILL.md`
- In this repo: `docs/SKILL.md`

It now references the tighter deltas in `agent_prompts.md`.

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
# compose prompt
hashline compose --model gemini
```