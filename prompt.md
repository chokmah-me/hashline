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