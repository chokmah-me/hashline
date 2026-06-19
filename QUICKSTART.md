# hashline Quickstart

> Stable, verifiable line edits for LLM coding agents — for **Claude, Grok,
> DeepSeek, Gemini, Kimi**, and any other tool-using model.

---

## 1. What is hashline and why does it exist?

When an LLM edits a file, the usual approach is **exact string replace**: the model
quotes a chunk of the old code and a chunk of the new code, and the harness swaps
one for the other. This is fragile:

- The model has to **reproduce the old code byte-for-byte** (whitespace, quotes,
  trailing commas). One character off and the edit silently fails or corrupts.
- If the file changed since the model last looked at it, the replace can land in
  the **wrong place** or clobber someone else's edit.
- Large edits waste tokens re-typing code that is already on disk.

**hashline fixes this with two ideas:**

1. **Line anchors instead of quoted strings.** The model reads a *numbered* view
   of the file and refers to edits by **line number ranges** (`SWAP 12.=15`), so
   it never has to re-quote old code. The patch body contains **only the new
   lines**.

2. **A content hash as a safety latch.** Every read is tagged with a 4-hex hash of
   the file's content, e.g. `[src/app.py#46FC]`. A patch is built against that
   tag. When the patch is applied, hashline recomputes the file's hash — **if it
   no longer matches the tag, the edit is rejected as `stale`** instead of
   applying to content the model never saw.

The result: edits are precise, cheap (no echoing old code), and **safe against
editing stale content**.

---

## 2. The core loop

```
read  →  patch  →  apply  →  re-read
```

1. **read** — get a numbered, hash-tagged view of the file.
2. **patch** — emit line-range operations whose bodies contain only new lines.
3. **apply** — hashline verifies the tag, applies bottom-up, writes a one-time
   `.hashlinebak` backup, and reports the **new tag**.
4. **re-read** — before the *next* edit, read again to pick up the new tag and
   line numbers. (Reusing an old tag is what triggers a `stale` rejection.)

---

## 3. Install

```bash
pip install git+https://github.com/chokmah-me/hashline.git
# or, from a clone:
pip install -e ".[dev]"
```

This gives you the `hashline` command (and `python -m hashline`).

---

## 4. Try it in 60 seconds

```bash
# 1. read — note the [path#TAG] header and the line numbers
$ hashline read app.py
[app.py#46FC]
1:def greet(name):
2:    print("hi")
3:    return None

# 2. apply — swap line 2 for new content (TAG must match the read)
$ hashline apply <<'HLP'
[app.py#46FC]
SWAP 2.=2:
+    print(f"hi {name}")
HLP
{'path': '/.../app.py', 'op': 'update', 'old_tag': '46FC', 'new_tag': 'D643'}
```

If the file had changed since the read, you'd get
`{'op': 'stale', 'expected': '46FC', 'actual': '...'}` and **nothing would be
written**.

### Patch operations

| Op            | Meaning                                            | Example          |
|---------------|----------------------------------------------------|------------------|
| `SWAP a.=b`   | Replace lines `a..b` with the `+` body             | `SWAP 4.=7:`     |
| `DEL a.=b`    | Delete lines `a..b` (no body)                      | `DEL 9.=10`      |
| `INS.PRE n`   | Insert the body **before** line `n`                | `INS.PRE 1:`     |
| `INS.POST n`  | Insert the body **after** line `n`                 | `INS.POST 12:`   |
| `INS.HEAD`    | Insert at the top of the file                      | `INS.HEAD:`      |
| `INS.TAIL`    | Insert at the bottom of the file                   | `INS.TAIL:`      |

Rules that make hashline reliable:

- A file block starts with `[path#TAG]`. Multiple file blocks can appear in one
  patch.
- **Body lines start with `+` and contain only the new content.** Never paste old
  code — the line range already removes it.
- A single `a` is shorthand for `a.=a` (one line).
- Use **only** the line numbers and tag from your **most recent** read.

By default a patch with malformed lines is **rejected** (`strict=True`). Use
`hashline apply --no-strict` to apply the valid hunks and just warn about the
rest.

---

## 5. Using hashline with a model

The pattern is identical for every model: put the **hashline rules in the system
prompt**, expose `hashline read`/`hashline apply` as a shell tool (or run them
yourself between turns), and make the model **always start with a read**.

Generate a ready-to-paste, model-tailored system prompt:

```bash
hashline compose --model claude     # also: grok | kimi | deepseek | gemini | base
```

Or programmatically:

```python
from hashline import compose_prompt
system_prompt = compose_prompt("grok")
```

### Claude / Claude Code

Claude follows hashline cleanly. For **Claude Code**, inject the guidance into
your project's `CLAUDE.md` so every session uses the harness:

```bash
python -m hashline.inject_claude .
```

For the **Claude API / your own agent**, use `compose_prompt("claude")` as the
system prompt and give the model a Bash tool. Loop: it calls `hashline read`,
emits a patch, you pipe it to `hashline apply`, it re-reads. Key reminder for
Claude: *re-read after every apply to pick up the new TAG.*

### Grok

Grok works best with an explicit skill. A ready-made skill with example sessions
lives at `docs/SKILL.md` (install to `~/.grok/skills/hashline/SKILL.md`). System
prompt: `compose_prompt("grok")`. Grok is expected to emit explicit
`hashline read` / `hashline apply` calls in the scrollback rather than a built-in
search-replace tool.

### DeepSeek (v4)

`compose_prompt("deepseek")`. DeepSeek is strong at structure but can drift to
line numbers from earlier turns, so its delta hammers home: *use ONLY the numbers
and `[PATH#TAG]` from the most recent read — never from memory.*

### Gemini

`compose_prompt("gemini")`. Gemini tends to echo old/context lines into diffs, so
its delta is: *never put original lines in the `+` body — write only the final
content; the range removes the old text.* Be explicit about whitespace.

### Kimi (k2)

`compose_prompt("kimi")`. Kimi already follows instructions well; its delta just
keeps it concise and allows **multi-hunk patches in one go** (several ops under a
single `[path#TAG]` block).

> Full per-model deltas and copy-paste prompts: [`prompts/agent_prompts.md`](prompts/agent_prompts.md)
> and the individual `prompts/*.md` files.

---

## 6. Programmatic use (build your own harness)

```python
from hashline import read_hashed, apply_patch, InMemorySnapshotStore

store = InMemorySnapshotStore()
view = read_hashed("app.py", store=store)   # numbered [path#TAG] text for the model
# ... model returns patch_text ...
result = apply_patch(patch_text, store=store)   # strict=True by default
print(result.sections)   # per-file: update / noop / stale / error
print(result.new_tags)   # path -> new 4-hex tag
print(result.warnings)   # malformed lines (when strict=False)
```

The `store` records snapshots so patches apply against the exact lines the model
read. The CLI uses a fresh in-memory store, so a CLI `apply` succeeds via the
**live-hash match** path (the file on disk must still hash to the patch's tag).

---

## 7. Troubleshooting

| Symptom                    | Cause / fix                                                        |
|----------------------------|-------------------------------------------------------------------|
| `op: stale`                | File changed since the read. **Re-read** and rebuild the patch.   |
| `op: error, missing`       | Path didn't resolve. Use the path exactly as shown in the read.   |
| `ValueError: malformed patch` | A bad op/range/`+` line. Fix it, or use `--no-strict` to skip it. |
| `op: noop`                 | The patch produces identical content; nothing was written.        |
| Edit applied to wrong lines | Stale line numbers from an earlier turn — always use the latest read. |

---

## 8. Learn more

- [`README.md`](README.md) — overview and CI details
- [`prompts/agent_prompts.md`](prompts/agent_prompts.md) — per-model prompt matrix
- [`docs/SKILL.md`](docs/SKILL.md) — full Grok skill with example sessions
- [`CHANGELOG.md`](CHANGELOG.md) — version history
</content>
