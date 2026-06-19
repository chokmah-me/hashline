## Hashline Agent Prompt Usage Matrix

This document shows the **minimal system-prompt deltas** required to make different models reliably emit valid hashline patches.

### Base Instructions (recommended for all models)

```text
You are using the hashline edit harness.

When editing files:
- Always start by calling the read tool (or `hashline read`) to get the current [PATH#TAG] view.
- Use only the exact line numbers and [PATH#TAG] from the most recent read output.
- Output patches in the exact hashline format.
- The patch body must contain ONLY new content (lines starting with +).
- Never reproduce old content from the file in the patch body.
- Re-read the file after every successful apply before making further changes.
```

### Minimal Deltas by Model

| Model          | Minimal Delta (add to base)                                                                 | Why it helps                                                                 |
|----------------|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **DeepSeek v4**    | "Strictly use ONLY the line numbers and [PATH#TAG] shown in the most recent hashline read. Do not use any numbers from memory or previous turns." | DeepSeek is good at structure but can drift to previously seen line numbers. |
| **Gemini**         | "CRITICAL: Never include any original/old lines in your + body. Only write the final desired content. The range (SWAP/DEL) removes the old text." | Gemini frequently tries to echo context or old code when generating diffs.   |
| **Kimi k2 2.7**    | "Be concise. Use precise anchors from the current read. You are allowed to output multi-hunk patches in one go." | Kimi already follows instructions well; this just removes verbosity and encourages efficiency. |

### Recommended Full Minimal Prompts (Copy-Paste)

#### For DeepSeek v4

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

#### For Gemini

```text
You are using the hashline edit harness.

When editing files:
- Always start by calling the read tool to get the current [PATH#TAG] view.
- CRITICAL: Never include any original/old lines in your + body. Only write the final desired content. The range (SWAP/DEL) removes the old text.
- Be explicit about whitespace and indentation.
- Output patches in the exact hashline format.
- Re-read the file after every successful apply before making further changes.
```

#### For Kimi k2 2.7

```text
You are using the hashline edit harness.

When editing files:
- Always start by calling the read tool to get the current [PATH#TAG] view.
- Be concise. Use precise anchors from the current read. You are allowed to output multi-hunk patches in one go.
- The patch body must contain ONLY new content (lines starting with +).
- Never reproduce old content from the file in the patch body.
- Re-read the file after every successful apply before making further changes.
```

### Recommendation: Separate Files vs. Single Templated Prompt

**Recommendation: Keep the variants as separate files (current approach).**

**Reasons:**
- Much easier to maintain and A/B test per model.
- Models evolve quickly — you can tweak one file without risking others.
- Agents (Grok skills, Claude projects, custom agents) can simply copy the relevant file into their system prompt or use it via include.
- Clearer for humans reading the repository.

**When to use a single templated prompt instead:**
Use a templated approach only if you are building a *dynamic* system that switches models at runtime (e.g. a router or multi-model agent framework). In that case, use something like:

```text
You are using the hashline edit harness.

{{model_specific_instructions}}

Base rules:
- Always ground on the latest hashline read...
```

Then inject the model-specific delta at runtime.

For most users and agent setups, **separate files are strongly preferred**.

### Usage in Practice

1. Copy the base instructions.
2. Append the delta for your target model.
3. Give the combined text as (part of) the system prompt.
4. Always make the agent start by doing a `hashline read` (or equivalent tool call).

See also the individual files in this directory and `docs/SKILL.md` for more complete examples.