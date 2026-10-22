# AGENTS.md — hashline

Line-range edits for LLM coding agents. Every read is tagged with a 4-hex content hash; patches against a stale tag are rejected. Pure Python.

## Commands

```powershell
pip install -e ".[dev,test]"
pytest
ruff check .
ruff format --check .
mypy hashline
python tests/harness_demo.py --models base gemini

hashline read path\to\file.py
hashline apply < my.patch
hashline compose --model gemini
```

Python 3.8+. Extra `dev` is ruff/mypy; extra `test` is pytest.

## Work rules

- The loop is `read → patch → apply → re-read`. Patch bodies contain only `+` new lines, never reproduced old content.
- File block header is `[path#TAG]`. Ops: `SWAP a.=b`, `DEL a.=b`, `INS.PRE n`, `INS.POST n`, `INS.HEAD`, `INS.TAIL`.
- Keep `prompts/*.md`, `docs/SKILL.md`, and `hashline/compose.py` consistent when the patch format changes.
- Target typing compatible with Python 3.8 (`from __future__ import annotations` as needed).

## Pointers

- `README.md` / `QUICKSTART.md` — usage
- `CLAUDE.md` — engine layout
- `docs/SKILL.md` — Grok skill
- `.github/workflows/ci.yml` — test/lint/typecheck/demo jobs
