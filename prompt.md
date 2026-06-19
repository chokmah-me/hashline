## Hashline Patch Format (works with DeepSeek v4, Gemini, Kimi k2, Grok, Claude)

Every file section starts with [PATH#TAG].

SWAP N.=M:
+ replacement lines

DEL N

INS.POST N:
+ inserted line

Rules:
- Use numbers exactly as returned by the most recent `hashline read`.
- Never output old content in the body — the range handles deletion.
- Re-ground (re-read) after every apply.
- Tight ranges only.

This format dramatically reduces failures on DeepSeek v4, Gemini, and Kimi k2 2.7 compared to raw str_replace.