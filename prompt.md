## Hashline Patch Language

See the model-specific variants in the `prompts/` directory.

Base rules (use this + the appropriate model variant):

[PATH#TAG]

SWAP N.=M:
+new content here

DEL N

INS.POST N:
+line to insert

Rules:
- Numbers come from the latest `hashline read` (or equivalent)
- Body is ONLY `+` lines
- Re-ground after every edit
- Stale tag? Re-read immediately

For best results with a specific model, prepend the content from `prompts/<model>.md`.

**See `prompts/agent_prompts.md` for a compact usage matrix** showing the *minimal* deltas for DeepSeek v4, Gemini, and Kimi k2 2.7, plus ready-to-copy full prompts and guidance on separate files vs. templated approach.