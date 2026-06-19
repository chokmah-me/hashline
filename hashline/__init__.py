"""Hashline edit harness — line-anchored, hash-verified patches for LLM agents.

Compatible with Grok Build (read_file + search_replace + run_terminal) and Claude Code
(via terminal + CLAUDE.md instructions after session-recall-cc).

See README.md and prompt.md for the model-facing contract.
"""
from .hashline import (
    compute_tag,
    normalize_text,
    SnapshotStore,
    InMemorySnapshotStore,
    read_hashed,
    Patch,
    Patcher,
    apply_patch,
)

__all__ = [
    "compute_tag",
    "normalize_text",
    "SnapshotStore",
    "InMemorySnapshotStore",
    "read_hashed",
    "Patch",
    "Patcher",
    "apply_patch",
]
