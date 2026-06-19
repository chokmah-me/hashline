... (keeping previous content, add to Development and Quick Usage) 

## Compose Prompts for Different Models

```bash
# Get a ready-to-use system prompt
hashline compose --model gemini

# Or using the script directly from source
python scripts/compose_prompt.py --model kimi
```

See `prompts/agent_prompts.md` for the full matrix of minimal deltas.

## Development

```bash
git clone https://github.com/chokmah-me/hashline
pip install -e ".[dev]"
# ...
hashline compose --model deepseek
```