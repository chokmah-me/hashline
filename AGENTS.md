# AGENTS.md — hashline

## What this is
Line-range edits for LLM coding agents, with a content-hash tag on every read so patches against stale buffers are rejected. Pure Python, no dependencies.

Full agent guidance for this repo lives in `CLAUDE.md`; this file is the cross-tool summary. Read `CLAUDE.md` before substantive work.

## Layout (top level)
- `CHANGELOG.md`
- `CLAUDE.md`
- `QUICKSTART.md`
- `README.md`
- `SUNSET.md`
- `docs`
- `hashline`
- `prompt.md`
- `prompts`
- `pyproject.toml`

## Work rules
- Work from the README first; it is the canonical description of purpose, layout, and any build or verify commands.
- Do not change verdicts, locked data tables, or published artifacts without the user's explicit word.
- Keep changes small and receipt-backed: name the commit or artifact a claim rests on.

## Canonical docs
- `README.md` — purpose, usage, and status.
