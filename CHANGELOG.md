# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2026-06-19

### Fixed
- **Windows / non-UTF-8 console encoding bugs in the CLI** (found while editing an
  emoji- and symbol-heavy repo):
  - `hashline read` crashed with `UnicodeEncodeError` when printing a file
    containing non-cp1252 characters (e.g. `≥`, emoji).
  - `hashline apply` reading a patch from **stdin** silently double-encoded
    non-ASCII content (em-dashes became mojibake) because stdin was decoded with
    the platform default instead of UTF-8.
  - Both fixed by forcing UTF-8 on `stdin`/`stdout`/`stderr` at CLI startup
    (`_force_utf8_io`). Added subprocess regression tests that pin the read and
    stdin-apply paths under a simulated non-UTF-8 console.

## [0.4.0] - 2026-06-19

### Added
- `QUICKSTART.md` — end-to-end guide explaining the purpose of hashline, how the
  read → patch → apply → re-read loop works, and copy-paste setup for Claude,
  Grok, DeepSeek, Gemini, and Kimi
- `parse(..., strict=True)` / `apply_patch(..., strict=True)` validation: malformed
  patch lines (unknown ops, orphan `+` bodies, bad ranges) are collected on
  `Patch.warnings` and `ApplyResult.warnings`; strict mode (the new default)
  raises `ValueError` instead of silently dropping them
- `hashline apply --no-strict` flag to apply valid hunks and warn on malformed
  lines instead of rejecting the whole patch
- `read_raw` / `write_raw` helpers exported from the package
- Python 3.13 classifier; expanded test suite (newline round-trips, tag
  round-trips, multi-op ordering, edge inserts/deletes, compose coverage)

### Changed
- **Default behavior change:** `parse`/`apply_patch` now reject malformed patches
  by default (`strict=True`). Pass `strict=False` for the previous lenient
  behavior.
- `hashline apply` now prints parse warnings and `noop` sections and exits
  non-zero on `stale`/`error` sections, so scripted callers can detect failures
- No-op patches (final content identical to current) are skipped instead of
  rewriting the file and creating a `.hashlinebak`

### Fixed
- Cross-platform newline corruption: file I/O now uses `newline=""` so the
  normalize/denormalize logic controls on-disk line endings (previously Windows
  silently rewrote LF → CRLF on every edit)
- Trailing-newline preservation for CR-only files
- `compose.py` crashed on import under Python 3.8 (`list[str]` annotation without
  `from __future__ import annotations`)
- `inject_claude.py` crashed because `Optional` was used without being imported
- `.gitignore` now excludes `*.hashlinebak` backups

## [0.2.0] - 2026-06-19

### Added
- End-to-end `tests/harness_demo.py` for verifying read → model-style patch → apply cycles (base case + Gemini)
- Dedicated `demo` job in GitHub Actions CI
- Full model-aware Grok skill (`docs/SKILL.md`) with concrete Example Sessions for Grok, DeepSeek v4, Gemini, and Kimi k2 2.7, including exact `hashline read` outputs and patch blocks agents should emit
- Model-specific prompt variants directory (`prompts/`) with guidance for different LLMs

### Changed
- Bumped version to 0.2.0
- Updated `pyproject.toml` documentation for test/demo extras
- Enhanced README.md with Grok skill example usage and CI job details
- Improved release process (assets, changelog, tagging)

### Fixed
- Various documentation and example refinements for multi-model support

## [0.1.0] - 2026-06-19

### Added
- Initial release of the hashline edit harness
- Core library for hash-anchored reads (`read_hashed`) and patches (SWAP, DEL, INS operations)
- CLI: `hashline read`, `hashline apply`, `hashline tag`
- `pyproject.toml` packaging with console script entrypoint
- Pure Python implementation (stdlib only, zero runtime dependencies)
- Model prompt variants for Grok, Claude, DeepSeek v4, Gemini, Kimi k2 2.7
- Claude Code injector (`inject_claude.py`)
- Basic tests and CI (test, lint with ruff, typecheck with mypy)
- Grok skill skeleton
- Documentation (README, prompt.md, prompts/)

Initial version supporting reliable LLM-driven file edits across multiple models via content-hash line anchors.