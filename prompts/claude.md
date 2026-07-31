## Claude Specific Guidance

**Claude passed the removal test** (2026-07-02, see `../SUNSET.md`): Claude Code's native
Edit/Write tools edit reliably without hashline. Do not instruct Claude Code to use
`hashline read`/`apply`, and do not inject the claude.md-snippet where native tools exist.

This variant remains only for Claude deployments *without* reliable native editing tools
(bare-API integrations). For those, the base contract suffices — no Claude-specific delta
is needed:

{{base}}
