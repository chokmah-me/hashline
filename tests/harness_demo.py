"""Minimal end-to-end demo for the hashline harness.

Simulates an agent doing:
  read → (model-style patch) → apply

Run:
  python -m pytest tests/harness_demo.py -q
  # or directly
  python tests/harness_demo.py --models base gemini
"""

import argparse
import tempfile
import sys
from pathlib import Path

from hashline.hashline import (
    read_hashed,
    parse,
    apply_patch,
    InMemorySnapshotStore,
)


def run_scenario(name: str, source: str, patch_text: str) -> bool:
    """Run one read → model-patch → apply cycle and return success."""
    print(f"\n=== Scenario: {name} ===")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "sample.py"
        p.write_text(source, encoding="utf-8")

        # 1. Read (what the agent would do)
        view = read_hashed(p)
        print("READ VIEW (first 8 lines):")
        print("\n".join(view.splitlines()[:8]))

        # Extract tag for realism (agent would copy it)
        tag = view.split("#", 1)[1].split("\n", 1)[0].split("]", 1)[0]
        print(f"TAG: {tag}")

        # 2. Model-style patch (what an LLM would emit after seeing the view)
        print("\nMODEL PATCH:")
        print(patch_text)

        # 3. Apply
        store = InMemorySnapshotStore()
        try:
            res = apply_patch(patch_text, store=store)
            print("\nAPPLY RESULT:", res.sections)
        except Exception as e:
            print("APPLY FAILED:", e)
            return False

        # 4. Re-ground + verify
        new_view = read_hashed(p)
        new_content = p.read_text(encoding="utf-8")
        print("\nRESULTING FILE:")
        print(new_content)

        # Basic success criteria
        success = (
            len(res.sections) > 0 and
            "error" not in str(res.sections[0].get("op", "")) and
            "stale" not in str(res.sections[0].get("op", ""))
        )
        print(f"\nSCENARIO {name}: {'PASS' if success else 'FAIL'}")
        return success


BASE_SOURCE = '''def process(items):
    out = []
    for x in items:
        if x > 0:
            out.append(x * 2)
    return out
'''

BASE_PATCH = '''[sample.py#PLACEHOLDER]
SWAP 5.=5:
+            out.append(x * 3)
'''

GEMINI_SOURCE = '''def format_name(first, last):
    return first + " " + last
'''

GEMINI_PATCH = '''[sample.py#PLACEHOLDER]
SWAP 2.=2:
+    return f"{first} {last}"
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["base", "gemini"],
                        help="Which scenarios to run")
    args = parser.parse_args()

    all_ok = True

    if "base" in args.models:
        # Real run will replace the placeholder tag inside the demo
        # For the demo we let the library compute the real tag
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.py"
            p.write_text(BASE_SOURCE, encoding="utf-8")
            view = read_hashed(p)
            tag = view.split("#", 1)[1].split("\n", 1)[0].split("]", 1)[0]
            patch = BASE_PATCH.replace("PLACEHOLDER", tag)
            ok = run_scenario("base", BASE_SOURCE, patch)
            all_ok = all_ok and ok

    if "gemini" in args.models:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.py"
            p.write_text(GEMINI_SOURCE, encoding="utf-8")
            view = read_hashed(p)
            tag = view.split("#", 1)[1].split("\n", 1)[0].split("]", 1)[0]
            patch = GEMINI_PATCH.replace("PLACEHOLDER", tag)
            ok = run_scenario("gemini", GEMINI_SOURCE, patch)
            all_ok = all_ok and ok

    print("\n=== OVERALL ===")
    print("ALL SCENARIOS PASSED" if all_ok else "SOME SCENARIOS FAILED")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
