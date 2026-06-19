## Gemini Specific Guidance

Gemini can be sensitive to exact formatting and sometimes tries to reproduce old text.

When using hashline:
- Strong reminder: "Do NOT include any original/old lines in your patch body. The range (SWAP/DEL) handles removal. Only provide new content after the + ."
- Be explicit about whitespace preservation.
- Gemini sometimes benefits from an extra example in the prompt.
- If it fails to find anchors, re-issue a fresh `hashline read` in the same turn.

Recommended:
Add this to system prompt:
"You must use the hashline format exactly. Reproduce no old content."

Base instructions:
{{base}}