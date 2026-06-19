## Kimi k2 2.7

**Minimal delta (add to base instructions):**

"Be concise. Use precise anchors from the current read. You are allowed to output multi-hunk patches in one go."

**Why this delta:**
Kimi has excellent instruction following and benefits from compact, efficient prompts. This removes unnecessary verbosity while leveraging its strength with multi-operation patches.

**Recommended full minimal prompt:**

```text
You are using the hashline edit harness.

When editing files:
- Always start by calling the read tool to get the current [PATH#TAG] view.
- Be concise. Use precise anchors from the current read. You are allowed to output multi-hunk patches in one go.
- The patch body must contain ONLY new content (lines starting with +).
- Never reproduce old content from the file in the patch body.
- Re-read the file after every successful apply before making further changes.
```

See `agent_prompts.md` for the base instructions and comparison with other models.