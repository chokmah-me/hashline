"""Hashline edit harness — line-anchored, hash-verified patches for LLM agents.

See README.md for usage and prompt.md for the agent contract.
"""

from .hashline import (  # noqa: F401
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