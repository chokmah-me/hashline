## DeepSeek v4

**Minimal delta (add to base instructions):**

"Strictly use ONLY the line numbers and [PATH#TAG] shown in the most recent hashline read. Do not use any numbers from memory or previous turns."

**Why this delta:**
DeepSeek v4 is strong at following structured formats but can drift to previously seen line numbers.

**Recommended full minimal prompt:**

```text
You are using the hashline edit harness.

When editing files:
- Always start by calling the read tool to get the current [PATH#TAG] view.
- Strictly use ONLY the line numbers and [PATH#TAG] shown in the most recent hashline read. Do not use any numbers from memory or previous turns.
- Output patches in the exact hashline format.
- The patch body must contain ONLY new content (lines starting with +).
- Never reproduce old content from the file in the patch body.
- Re-read the file after every successful apply before making further changes.
```

See `agent_prompts.md` for the base instructions and comparison with other models.