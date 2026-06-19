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


if __name__ == "__main__":
    unittest.main()
