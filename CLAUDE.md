<!-- session-recall:v1 — DO NOT EDIT MANUALLY -->
## Progressive Session Recall — RUN FIRST ON EVERY PROMPT

**Run `session-recall-cc` FIRST on every prompt before doing anything else.** It costs ~50 tokens and prevents expensive blind searches.

```bash
session-recall-cc files --json --limit 10  # recently touched files
session-recall-cc files --days 7 --json    # files touched in last 7 days
session-recall-cc list --json --limit 5    # recent sessions
session-recall-cc list --days 2 --json     # sessions from last 2 days
session-recall-cc search '<term>' --json   # full-text search
session-recall-cc search '<term>' --days 5 # search last 5 days only
session-recall-cc checkpoints --days 3     # checkpoints from last 3 days
session-recall-cc repos --json             # discovered repositories across providers
session-recall-cc show <id> --json         # drill into one session
session-recall-cc health --json            # 8-dimension health check
session-recall-cc schema-check             # validate DB schema (run after Copilot CLI upgrade)
```

**`--days N` works on all 4 query commands** (`list`, `files`, `checkpoints`, `search`) — filters to sessions/files/checkpoints from the last N days.

Only use filesystem tools (grep, glob, find) if session-recall-cc returns nothing useful.
If `session-recall-cc` errors, continue silently — it's a convenience, not a blocker.
<!-- /session-recall:v1 -->

<!-- hashline:v1 START -->
## Hashline edit harness (use for all file modifications)

**After running `session-recall-cc`, use the hashline harness for edits.**

```bash
python -m hashline read path/to/file.py
python -m hashline apply <<'HLP'
...
HLP
```

See the hashline package for full rules.
<!-- hashline:v1 END -->



# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`hashline` is a hash-anchored edit harness for LLM coding agents. Instead of fragile exact-string replacement, an agent reads a file as a numbered view tagged with a 4-hex content hash (`[path#TAG]`), then emits line-range patch operations. Edits only apply if the file's current hash still matches the tag the patch was built against — this is the core safety guarantee against editing stale content.

## Commands

```bash
pip install -e ".[dev]"        # dev install (ruff, mypy); add ".[test]" for pytest

pytest                          # run test suite
pytest tests/test_hashline.py::test_name   # single test

ruff check .                    # lint
ruff format --check .           # format check
mypy hashline                   # typecheck

python tests/harness_demo.py --models base gemini   # end-to-end read->patch->apply demo

# CLI (also: python -m hashline ...)
hashline read path/to/file.py   # print [path#TAG] numbered view, records snapshot
hashline tag path/to/file.py    # print current 4-hex content tag
hashline apply -p patch.txt     # apply a patch (also reads from stdin); --dry-run
hashline compose --model gemini # print model-tailored system prompt
```

CI (`.github/workflows/ci.yml`) runs separate jobs: `test` (pytest on Python 3.8–3.13 + CLI smoke), `lint` (ruff), `typecheck` (mypy), `demo` (harness_demo for base + gemini).

## Architecture

Everything lives in `hashline/`. The package targets Python 3.8+, so keep typing compatible (note `from __future__ import annotations`).

- **`hashline.py`** — the entire engine, no external deps:
  - **Tagging:** `compute_tag` = first 4 hex chars (uppercased) of SHA-256 over newline-normalized text. `normalize_text`/`denormalize_text` collapse CRLF/CR to LF for hashing/processing, then restore the file's original newline + trailing-newline on write.
  - **Snapshots:** `SnapshotStore` / `InMemorySnapshotStore` map `(path, tag) -> normalized content`. `read_hashed` records a snapshot under resolved path, basename, and raw path keys so patches resolve regardless of how the path is later spelled. Patches apply against the *recorded snapshot* lines, not a re-read of the file.
  - **Patch format & parsing:** `parse` turns patch text into `Patch -> FilePatch -> Hunk`. A file block header is `[path#TAG]`. Hunk ops: `SWAP a.=b`, `DEL a.=b`, `INS.PRE n`, `INS.POST n`, `INS.HEAD`, `INS.TAIL`. Ranges use `a.=b` syntax (`_RANGE_RE`). **Patch bodies contain only new lines prefixed with `+`** — never reproduced old content.
  - **Applying:** `Patcher.apply` aborts a file with a `stale` section if the live hash != patch tag. Operations are sorted by start line descending so earlier line numbers stay valid as edits are applied bottom-up. Writes a one-time `.hashlinebak` backup unless disabled. Returns `ApplyResult` with per-file `sections` and `new_tags`.

- **`compose.py`** — `compose_prompt(model)` = `BASE` rules + a per-model `DELTAS` reminder. `DELTAS` defines `base`, `deepseek`, `gemini`, `kimi`, `claude`, `grok` (matching the `prompts/*.md` variants); `base` has an empty delta and returns `BASE` alone. These are the valid `--model` choices. Update `DELTAS` to add a model.

- **`cli.py`** — argparse dispatch for `read`/`apply`/`tag`/`compose`. `cmd_apply` uses a fresh `InMemorySnapshotStore`, so a CLI `apply` only succeeds via the live-hash match path (no cross-process snapshot).

- **`inject_claude.py`** — `python -m hashline.inject_claude .` installs hashline guidance for Claude Code users.

- **`__init__.py`** re-exports the public API; keep `__all__` in sync when adding exports.

## Conventions

- The `read -> patch -> apply -> re-read` loop is the intended workflow; the prompts in `prompts/` and `compose.py` enforce that agents only use line numbers/tags from the most recent read.
- `prompts/*.md` and `docs/SKILL.md` are the authored prompt sources; `compose.py` is the programmatic equivalent. Keep them consistent when changing the patch format.
