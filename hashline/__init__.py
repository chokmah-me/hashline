"""Hashline edit harness — line-anchored, hash-verified patches for LLM agents.

See README.md for usage and prompts/agent_prompts.md for model-specific guidance.
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
from .compose import compose_prompt, list_models  # noqa: F401

__all__ = [
    "compute_tag",
    "normalize_text",
    "SnapshotStore",
    "InMemorySnapshotStore",
    "read_hashed",
    "Patch",
    "Patcher",
    "apply_patch",
    "compose_prompt",
    "list_models",
]
