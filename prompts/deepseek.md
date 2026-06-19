## DeepSeek v4 Specific Guidance

DeepSeek v4 is strong at following structured formats.

When using hashline:
- Explicitly tell the model: "Use ONLY the line numbers and [PATH#TAG] from the most recent `hashline read` output. Do not guess or remember previous content."
- It handles ranges well. You can use SWAP.BLK style if you describe the block.
- Good at compact output — leverage the token savings.

Recommended prefix for DeepSeek sessions:
"You are using the hashline edit harness. Ground every edit on a fresh read output."

Base instructions:
{{base}}