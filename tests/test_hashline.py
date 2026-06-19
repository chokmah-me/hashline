"""Tests for hashline core."""

import tempfile
import unittest
from pathlib import Path

from hashline.hashline import (
    compute_tag,
    read_hashed,
    parse,
    apply_patch,
    InMemorySnapshotStore,
    Patcher,
)
from hashline.compose import compose_prompt, list_models, BASE


def _tag_of(view):
    return view.split("#", 1)[1].split("\n", 1)[0].split("]", 1)[0]


class TestHashline(unittest.TestCase):
    def test_tag_stable(self):
        text = "def f():\n    return 1\n"
        self.assertEqual(compute_tag(text), compute_tag(text))
        self.assertEqual(len(compute_tag(text)), 4)

    def test_read_hashed_format(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "ex.py"
            p.write_text("a = 1\nb = 2\n", encoding="utf-8")
            view = read_hashed(p)
            self.assertIn("[", view)
            self.assertIn("#", view)
            self.assertIn("1:a = 1", view)

    def test_basic_swap(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            orig = "def f():\n    x = 1\n    return x\n"
            p.write_text(orig, encoding="utf-8")
            view = read_hashed(p, store=store)
            tag = view.split("#", 1)[1].split("\n", 1)[0].split("]", 1)[0]
            patch = f"""[{p.name}#{tag}]
SWAP 2.=2:
+    x = 42
"""
            patcher = Patcher(store=store, fs_root=td)
            res = patcher.apply(parse(patch))
            self.assertTrue(any(s.get("op") == "update" for s in res.sections))
            self.assertIn("x = 42", p.read_text())

    def test_ins_and_del(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            orig = "line1\nline2\nline3\n"
            p.write_text(orig, encoding="utf-8")
            view = read_hashed(p, store=store)
            tag = view.split("#", 1)[1].split("\n", 1)[0].split("]", 1)[0]
            patch = f"""[{p.name}#{tag}]
DEL 2
INS.POST 1:
+inserted after 1
"""
            patcher = Patcher(store=store, fs_root=td)
            patcher.apply(parse(patch))
            final = p.read_text().splitlines()
            self.assertEqual(final, ["line1", "inserted after 1", "line3"])

    def test_stale_rejected(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_text("one\ntwo\n", encoding="utf-8")
            view = read_hashed(p, store=store)
            tag = view.split("#", 1)[1].split("\n", 1)[0].split("]", 1)[0]
            p.write_text("one\nTWO\nthree\n", encoding="utf-8")
            patch = f"""[{p.name}#{tag}]
DEL 2
"""
            patcher = Patcher(store=store, fs_root=td)
            res = patcher.apply(parse(patch))
            self.assertTrue(any(s.get("op") == "stale" for s in res.sections))

    def test_head_tail(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_text("body\n", encoding="utf-8")
            view = read_hashed(p, store=store)
            tag = view.split("#", 1)[1].split("\n", 1)[0].split("]", 1)[0]
            patch = f"""[{p.name}#{tag}]
INS.HEAD:
+# header
INS.TAIL:
+trailer
"""
            patcher = Patcher(store=store, fs_root=td)
            patcher.apply(parse(patch))
            content = p.read_text()
            self.assertTrue(content.startswith("# header\n"))
            self.assertTrue(content.endswith("trailer\n") or content.endswith("trailer"))

    def test_parse_multi(self):
        txt = """[a.py#ABCD]
SWAP 1.=1:
+new
[b.py#1234]
DEL 5
"""
        p = parse(txt)
        self.assertEqual(len(p.files), 2)
        self.assertEqual(p.files[0].hunks[0].op, "SWAP")

    def test_roundtrip_tag(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_text("a = 1\nb = 2\n", encoding="utf-8")
            tag = _tag_of(read_hashed(p, store=store))
            patch = f"[{p.name}#{tag}]\nSWAP 1.=1:\n+a = 99\n"
            res = Patcher(store=store, fs_root=td).apply(parse(patch))
            new_tag = res.new_tags[str(p.resolve())]
            # reported tag matches actual file content and a fresh read
            self.assertEqual(new_tag, compute_tag(p.read_text()))
            self.assertEqual(new_tag, _tag_of(read_hashed(p, store=store)))

    def test_crlf_preserved(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_bytes(b"one\r\ntwo\r\n")
            tag = _tag_of(read_hashed(p, store=store))
            patch = f"[{p.name}#{tag}]\nSWAP 2.=2:\n+TWO\n"
            Patcher(store=store, fs_root=td).apply(parse(patch))
            self.assertEqual(p.read_bytes(), b"one\r\nTWO\r\n")

    def test_cr_preserved(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_bytes(b"one\rtwo\r")
            tag = _tag_of(read_hashed(p, store=store))
            patch = f"[{p.name}#{tag}]\nSWAP 2.=2:\n+TWO\n"
            Patcher(store=store, fs_root=td).apply(parse(patch))
            self.assertEqual(p.read_bytes(), b"one\rTWO\r")

    def test_no_trailing_newline_preserved(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_text("a\nb", encoding="utf-8")  # no trailing newline
            tag = _tag_of(read_hashed(p, store=store))
            patch = f"[{p.name}#{tag}]\nSWAP 1.=1:\n+A\n"
            Patcher(store=store, fs_root=td).apply(parse(patch))
            self.assertEqual(p.read_text(), "A\nb")

    def test_reversed_range(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_text("1\n2\n3\n4\n", encoding="utf-8")
            tag = _tag_of(read_hashed(p, store=store))
            patch = f"[{p.name}#{tag}]\nSWAP 3.=1:\n+X\n"
            Patcher(store=store, fs_root=td).apply(parse(patch))
            self.assertEqual(p.read_text().splitlines(), ["X", "4"])

    def test_multiple_ops_bottom_up(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_text("a\nb\nc\nd\n", encoding="utf-8")
            tag = _tag_of(read_hashed(p, store=store))
            patch = (
                f"[{p.name}#{tag}]\n"
                "DEL 4\n"
                "SWAP 1.=1:\n+A\n"
                "INS.POST 2:\n+after-b\n"
            )
            Patcher(store=store, fs_root=td).apply(parse(patch))
            self.assertEqual(p.read_text().splitlines(), ["A", "b", "after-b", "c"])

    def test_ins_pre_first_line(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_text("first\nsecond\n", encoding="utf-8")
            tag = _tag_of(read_hashed(p, store=store))
            patch = f"[{p.name}#{tag}]\nINS.PRE 1:\n+zero\n"
            Patcher(store=store, fs_root=td).apply(parse(patch))
            self.assertEqual(p.read_text().splitlines(), ["zero", "first", "second"])

    def test_del_all_lines(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_text("x\ny\n", encoding="utf-8")
            tag = _tag_of(read_hashed(p, store=store))
            patch = f"[{p.name}#{tag}]\nDEL 1.=2\n"
            Patcher(store=store, fs_root=td).apply(parse(patch))
            self.assertEqual(p.read_text(), "\n")

    def test_stale_after_self_edit(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_text("a\nb\n", encoding="utf-8")
            tag = _tag_of(read_hashed(p, store=store))
            patcher = Patcher(store=store, fs_root=td)
            patcher.apply(parse(f"[{p.name}#{tag}]\nSWAP 1.=1:\n+A\n"))
            # reusing the stale tag must be rejected
            res = patcher.apply(parse(f"[{p.name}#{tag}]\nSWAP 2.=2:\n+B\n"))
            self.assertTrue(any(s.get("op") == "stale" for s in res.sections))

    def test_cli_live_hash_path(self):
        # fresh store with no recorded snapshot -> must succeed via live-hash fallback
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_text("hello\n", encoding="utf-8")
            tag = compute_tag(p.read_text())
            patch = f"[{p.resolve().as_posix()}#{tag}]\nSWAP 1.=1:\n+HELLO\n"
            res = apply_patch(patch, store=InMemorySnapshotStore())
            self.assertTrue(any(s.get("op") == "update" for s in res.sections))
            self.assertEqual(p.read_text(), "HELLO\n")

    def test_noop_skips_write(self):
        store = InMemorySnapshotStore()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "t.py"
            p.write_text("same\n", encoding="utf-8")
            tag = _tag_of(read_hashed(p, store=store))
            patch = f"[{p.name}#{tag}]\nSWAP 1.=1:\n+same\n"
            res = Patcher(store=store, fs_root=td).apply(parse(patch))
            self.assertTrue(any(s.get("op") == "noop" for s in res.sections))
            self.assertFalse((td / "t.py.hashlinebak").exists())

    def test_malformed_strict_raises(self):
        with self.assertRaises(ValueError):
            parse("[a.py#ABCD]\nBOGUS 1\n")

    def test_malformed_non_strict_warns(self):
        p = parse("[a.py#ABCD]\nBOGUS 1\nSWAP 1.=1:\n+ok\n", strict=False)
        self.assertTrue(p.warnings)
        self.assertEqual(len(p.files[0].hunks), 1)


class TestCompose(unittest.TestCase):
    def test_base_alone(self):
        self.assertEqual(compose_prompt("base"), BASE.strip())

    def test_unknown_model_raises(self):
        with self.assertRaises(ValueError):
            compose_prompt("does-not-exist")

    def test_all_models_compose(self):
        for m in list_models():
            self.assertTrue(compose_prompt(m).startswith(BASE.strip()))


if __name__ == "__main__":
    unittest.main()
