# hashline

**Hash-anchored edit harness for LLM coding agents.**

Stable, verifiable line-based edits using short content hashes.

**Tested / works well with:**
- Grok (xAI)
- Claude Code
- **DeepSeek v4**
- **Gemini (Google)**
- **Kimi k2 2.7 (Moonshot)**

## Install

```bash
pip install git+https://github.com/chokmah-me/hashline.git
```

Then use the `hashline` command.

## How the extension works for different models

The harness itself is model-agnostic. The improvements come from:

1. The `read` output giving the model stable anchors instead of having to copy text.
2. Compact patch format that reduces output tokens and error surface.

### Tips per model

**DeepSeek v4**
- Very good at structured output.
- In your instructions: "Always use the exact [path#TAG] and numbers from the most recent hashline read."

**Gemini**
- Can be whitespace sensitive.
- Strong reminder in prompt: "Body is ONLY the + lines. Do not include any old content."

**Kimi k2 2.7**
- Excellent instruction following for this kind of format.
- Benefits hugely from the token reduction.

See `prompt.md` for the canonical agent contract.