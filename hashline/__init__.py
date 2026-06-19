"""Hashline edit harness — line-anchored, hash-verified patches for LLM agents."""

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
