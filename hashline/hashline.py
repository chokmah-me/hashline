"""Core hashline implementation - full working version."""

from __future__ import annotations

import hashlib
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def normalize_text(text: str) -> Tuple[str, str]:
    if not text:
        return "", "\n"
    if "\r\n" in text:
        newline = "\r\n"
    elif "\r" in text and "\n" not in text:
        newline = "\r"
    else:
        newline = "\n"
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized, newline

def denormalize_text(normalized: str, newline: str) -> str:
    if newline == "\n":
        return normalized
    if newline == "\r\n":
        return normalized.replace("\n", "\r\n")
    if newline == "\r":
        return normalized.replace("\n", "\r")
    return normalized

def compute_tag(text: str) -> str:
    norm, _ = normalize_text(text)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:4].upper()


class SnapshotStore:
    def record(self, path: str, content: str) -> str:
        raise NotImplementedError
    def get(self, path: str, tag: str) -> Optional[str]:
        raise NotImplementedError


@dataclass
class InMemorySnapshotStore(SnapshotStore):
    _store: Dict[Tuple[str, str], str] = field(default_factory=dict)

    def record(self, path: str, content: str) -> str:
        norm, _ = normalize_text(content)
        tag = compute_tag(content)
        key = str(Path(path).resolve())
        self._store[(key, tag)] = norm
        self._store[(Path(path).name, tag)] = norm
        self._store[(path, tag)] = norm
        return tag

    def get(self, path: str, tag: str) -> Optional[str]:
        key = str(Path(path).resolve())
        return (self._store.get((key, tag)) or
                self._store.get((Path(path).name, tag)) or
                self._store.get((path, tag)))


_global_store = InMemorySnapshotStore()


def read_hashed(path: str | Path, store: Optional[SnapshotStore] = None) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    raw = p.read_text(encoding="utf-8", errors="replace")
    tag = (store or _global_store).record(str(p), raw)
    norm, _ = normalize_text(raw)
    lines = norm.splitlines(keepends=False)
    out = [f"[{p.as_posix()}#{tag}]"]
    for i, line in enumerate(lines, 1):
        out.append(f"{i}:{line}")
    return "\n".join(out)


@dataclass
class Hunk:
    op: str
    start: Optional[int] = None
    end: Optional[int] = None
    body: List[str] = field(default_factory=list)


@dataclass
class FilePatch:
    path: str
    tag: str
    hunks: List[Hunk] = field(default_factory=list)


@dataclass
class Patch:
    files: List[FilePatch] = field(default_factory=list)


_HUNK_RE = re.compile(r'^(SWAP|DEL|INS\.(?:PRE|POST|HEAD|TAIL))\s*(.*)$')
_RANGE_RE = re.compile(r'^(\d+)(?:\.=(\d+))?\s*:?$')


def _parse_lid(s: str) -> int:
    return int(s.strip())


def _parse_range(s: str) -> Tuple[int, int]:
    s = s.strip().rstrip(":")
    m = _RANGE_RE.match(s)
    if not m:
        lid = _parse_lid(s)
        return lid, lid
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) else a
    return min(a, b), max(a, b)


def parse(patch_text: str) -> Patch:
    lines = patch_text.splitlines()
    patch = Patch()
    current_file = None
    current_hunk = None

    for line in lines:
        line = line.rstrip("\r")
        if not line.strip():
            continue
        if line.startswith("[") and "#" in line and line.endswith("]"):
            inner = line[1:-1]
            path, tag = inner.rsplit("#", 1)
            current_file = FilePatch(path=path.strip(), tag=tag.strip().upper())
            patch.files.append(current_file)
            current_hunk = None
            continue

        m = _HUNK_RE.match(line.strip())
        if m and current_file:
            op = m.group(1)
            rest = m.group(2).strip()
            if op == "DEL":
                a, b = _parse_range(rest)
                current_hunk = Hunk("DEL", a, b)
                current_file.hunks.append(current_hunk)
                current_hunk = None
            elif op.startswith("SWAP"):
                a, b = _parse_range(rest.rstrip(":"))
                current_hunk = Hunk(op, a, b)
                current_file.hunks.append(current_hunk)
            elif op.startswith("INS"):
                if "HEAD" in op or "TAIL" in op:
                    current_hunk = Hunk(op)
                else:
                    lid = _parse_lid(rest.rstrip(":"))
                    current_hunk = Hunk(op, lid, lid)
                current_file.hunks.append(current_hunk)
            continue

        stripped = line.lstrip()
        if stripped.startswith("+") and current_hunk is not None:
            current_hunk.body.append(stripped[1:])
            continue
        if stripped == "+" and current_hunk is not None:
            current_hunk.body.append("")
            continue

    return patch


@dataclass
class ApplyResult:
    sections: List[Dict] = field(default_factory=list)
    new_tags: Dict[str, str] = field(default_factory=dict)


class Patcher:
    def __init__(self, store: Optional[SnapshotStore] = None, fs_root: Optional[Path] = None):
        self.store = store or _global_store
        self.fs_root = fs_root or Path.cwd()

    def _resolve_path(self, p: str) -> Path:
        pp = Path(p)
        if pp.is_absolute():
            return pp.resolve()
        candidate = (self.fs_root / pp).resolve()
        if candidate.exists():
            return candidate
        bare = (self.fs_root / pp.name).resolve()
        if bare.exists():
            return bare
        return candidate

    def apply(self, patch: Patch, dry_run: bool = False, backup: bool = True) -> ApplyResult:
        result = ApplyResult()
        for fp in patch.files:
            path = self._resolve_path(fp.path)
            if not path.exists():
                result.sections.append({"path": str(path), "op": "error", "error": "missing"})
                continue

            current_raw = path.read_text(encoding="utf-8", errors="replace")
            current_tag = compute_tag(current_raw)
            if current_tag != fp.tag:
                result.sections.append({"path": str(path), "op": "stale", "expected": fp.tag, "actual": current_tag})
                continue

            snap = self.store.get(str(path), fp.tag) or current_raw
            orig_lines = snap.splitlines(keepends=False)

            ops = []
            for h in fp.hunks:
                if h.op == "DEL" and h.start and h.end:
                    ops.append(("del", h.start, h.end, []))
                elif h.op.startswith("SWAP") and h.start and h.end:
                    ops.append(("swap", h.start, h.end, list(h.body)))
                elif h.op == "INS.HEAD":
                    ops.append(("ins_head", 1, 0, list(h.body)))
                elif h.op == "INS.TAIL":
                    ops.append(("ins_tail", len(orig_lines)+1, len(orig_lines), list(h.body)))
                elif h.op == "INS.PRE" and h.start:
                    ops.append(("ins_pre", h.start, h.start, list(h.body)))
                elif h.op == "INS.POST" and h.start:
                    ops.append(("ins_post", h.start, h.start, list(h.body)))

            ops.sort(key=lambda o: o[1], reverse=True)

            working = list(orig_lines)
            for kind, a, b, body in ops:
                if kind == "del":
                    working[a-1:b] = []
                elif kind == "swap":
                    working[a-1:b] = body
                elif kind == "ins_head":
                    working = body + working
                elif kind == "ins_tail":
                    working = working + body
                elif kind == "ins_pre":
                    working = working[:a-1] + body + working[a-1:]
                elif kind == "ins_post":
                    working = working[:a] + body + working[a:]

            new_norm = "\n".join(working)
            _, orig_newline = normalize_text(current_raw)
            final = denormalize_text(new_norm + ("\n" if current_raw.endswith("\n") else ""), orig_newline)

            if not dry_run:
                if backup:
                    bak = path.with_suffix(path.suffix + ".hashlinebak")
                    if not bak.exists():
                        shutil.copy2(path, bak)
                path.write_text(final, encoding="utf-8")

            new_tag = compute_tag(final)
            self.store.record(str(path), final)

            result.sections.append({"path": str(path), "op": "update", "old_tag": fp.tag, "new_tag": new_tag})
            result.new_tags[str(path)] = new_tag

        return result


def apply_patch(patch_text: str, store: Optional[SnapshotStore] = None, dry_run: bool = False) -> ApplyResult:
    p = parse(patch_text)
    patcher = Patcher(store=store)
    return patcher.apply(p, dry_run=dry_run)
