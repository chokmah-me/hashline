---
name: hashline
description: >
  Use the hashline edit harness for reliable file edits. Preferred over raw search_replace
  for any non-trivial change. Triggered by "hashline", "use hash anchors", "reliable edit",
  "edit harness", or when the user asks for edits / fixes / refactors.
metadata:
  short-description: "Hash-anchored verified edits (from the harness problem paper)"
---

# Hashline Edit Harness

**The edit tool is the harness.** `search_replace` (exact string match) is brittle and wastes tokens. Use hashline instead.

## Always do this for edits

1. **Ground first** (after `pip install hashline` or from source). Prefer the installed command:
   ```bash
   hashline read path/to/file.ext
   # fallback: python -m hashline read path/to/file.ext
   ```
   (or post-process a recent `read_file` output if you already have the exact lines).

2. In your thinking, use the exact format from the output:
   - Header: `[path#TAG]`
   - Anchors: line numbers that came from that exact read.
   - Ops: `SWAP N.=M:`, `DEL N`, `INS.POST N:`, `INS.PRE N:`, `INS.HEAD:`, `INS.TAIL:`

3. Apply (preferred — keeps output tokens low and anchors stable):
   ```bash
   hashline apply <<'EOF'
   [the/full/patch/you/just/wrote]
   EOF
   ```

   For tiny single-line cases you may fall back to a minimal unique `old_string` + `search_replace` (you already know the exact text from the read).

4. **Immediately re-ground** (`hashline read` or `read_file`) before the next edit on that file. Every successful apply produces a fresh `#TAG`.

## The contract (paste this into your context when editing)

```
<rules>
- Line numbers + [PATH#TAG] come from the latest hashline read / read_file view.
- Numbers are from the ORIGINAL snapshot; they do not auto-shift.
- Re-ground after every edit — new TAG every time.
- Ranges are TIGHT: only lines whose content you are changing.
- Body rows are only "+TEXT" (or bare "+" for blank).
- Never echo old content. The range deletes; the body is the final state.
- Stale tag? Stop and re-read.
</rules>
```

Full authoritative rules + examples (including model-specific variants) live in the hashline repo:
https://github.com/chokmah-me/hashline (see prompt.md and the prompts/ directory)

## Model-Aware Example Sessions

Use the base contract above + the **tighter, minimal deltas** from `prompts/agent_prompts.md`.

The `prompts/` directory now contains focused minimal instructions for each model. See `prompts/agent_prompts.md` for the comparison table, "Why this delta" explanations, and ready-to-use full minimal prompts.

### Grok (this TUI / current environment)
Recommended prefix: "You are using the hashline edit harness. Always ground on the most recent read output."

**Concrete example an agent should emit**

User request: "Fix the multiplier bug in process_data"

Agent actions (exact text to emit):

```bash
hashline read src/processor.py
```

(Receives something like:)
```
[src/processor.py#7F2A]
1:def process_data(items):
2:    out = []
3:    for x in items:
4:        if x > 0:
5:            out.append(x * 2)
6:    return out
```

Reasoning: "The *2 on line 5 is wrong per the request. I'll replace only that line."

```bash
hashline apply << 'EOF'
[src/processor.py#7F2A]
SWAP 5.=5:
+            out.append(x * 3)
EOF
```

Then immediately:

```bash
hashline read src/processor.py
```

### DeepSeek v4
Recommended prefix (tight delta from agent_prompts.md): "Strictly use ONLY the line numbers and [PATH#TAG] shown in the most recent hashline read. Do not use any numbers from memory or previous turns."

**Concrete example**

Agent emits:

```bash
hashline read utils.py
```

(Example received view:)
```
[utils.py#B41C]
1:def clamp(val, lo, hi):
2:    if val < lo:
3:        return lo
4:    if val > hi:
5:        return hi
6:    return val
```

```bash
hashline apply << 'EOF'
[utils.py#B41C]
SWAP 2.=2:
+    if val <= lo:
EOF
```

Re-ground:
```bash
hashline read utils.py
```

### Gemini
Recommended prefix (tight delta from agent_prompts.md): "CRITICAL: Never include any original/old lines in your + body. Only write the final desired content. The range (SWAP/DEL) removes the old text."

**Concrete example** (Gemini tends to want extra safety reminders)

Agent emits:

```bash
hashline read formatter.py
```

(Example view:)
```
[formatter.py#C9E3]
1:def format_name(first, last):
2:    return first + " " + last
```

```bash
hashline apply << 'EOF'
[formatter.py#C9E3]
SWAP 2.=2:
+    return f"{first} {last}"
EOF
```

Re-ground immediately.

### Kimi k2 2.7
Recommended prefix (tight delta from agent_prompts.md): "Be concise. Use precise anchors from the current read. You are allowed to output multi-hunk patches in one go."

**Concrete example** (Kimi handles multi-op patches well)

Agent emits:

```bash
hashline read data.py
```

(Example view:)
```
[data.py#4D8F]
1:def summarize(nums):
2:    total = 0
3:    count = 0
4:    for n in nums:
5:        total += n
6:        count += 1
7:    return total / count
```

```bash
hashline apply << 'EOF'
[data.py#4D8F]
INS.POST 1:
+    if not nums:
+        return 0.0
SWAP 7.=7:
+    return total / count if count else 0.0
EOF
```

Re-ground:
```bash
hashline read data.py
```

## Integration with other skills

- `implement`, `review`, `check-work`: prefer hashline for actual mutations.
- Subagents: "use the hashline harness for edits — run `hashline read` first".
- Plan mode: use it when materializing plans into code.

## Claude Code users (session-recall-cc)

The package works identically.

Always run `session-recall-cc ...` first, then the hashline commands.

Update CLAUDE.md files with:
```bash
python -m hashline.inject_claude .
```

See the repo for the full `claude.md-snippet`.

## Implementation note for you (the agent)

- Install with `pip install git+https://github.com/chokmah-me/hashline.git`
- Core is pure stdlib + pathlib.
- Snapshots live under `~/.hashline/snapshots`.
- Prefer `hashline read` / `hashline apply` over raw `search_replace`.
- After any apply, re-read before further edits on that path.

Use the harness. Your success rate (and token budget) will thank you.