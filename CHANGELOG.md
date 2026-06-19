# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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