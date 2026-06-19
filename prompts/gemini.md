## Gemini

**Minimal delta (add to base instructions):**

"CRITICAL: Never include any original/old lines in your + body. Only write the final desired content. The range (SWAP/DEL) removes the old text."

**Why this delta:**
Gemini can be sensitive to exact formatting and frequently tries to reproduce old content or context when generating edits.

**Recommended full minimal prompt:**

```text
You are using the hashline edit harness.

When editing files:
- Always start by calling the read tool to get the current [PATH#TAG] view.
- CRITICAL: Never include any original/old lines in your + body. Only write the final desired content. The range (SWAP/DEL) removes the old text.
- Be explicit about whitespace and indentation.
- Output patches in the exact hashline format.
- Re-read the file after every successful apply before making further changes.
```

See `agent_prompts.md` for the base instructions and comparison with other models.