# Sunset policy

hashline is a **capability prosthetic**: it exists because some models could not reliably
edit files with exact-string replace. Prosthetics depreciate — every frontier release makes
native editing more reliable, so this repo is on an explicit sunset track rather than a
growth track.

## Rules (as of 2026-07-05)

1. **The per-model prompt matrix is frozen.** No new cells in `prompts/` — new models get
   `prompts/base.md` or nothing. Hand-tuned per-model deltas are N×M maintenance with a
   guaranteed expiry date on every cell.
2. **Claude Code does not use hashline** (decision 2026-07-02): its native Edit/Write tools
   passed the removal test, and the enforce-hashline hook added friction without value.
3. **Removal test, per model** — run on each major release of a still-enrolled model
   (Grok, DeepSeek, Gemini, Kimi):
   - Give the model 10 multi-file edit tasks (≥3 files, ≥5 hunks each) using its native
     edit mechanism, no hashline.
   - If ≥9/10 apply cleanly with no corrupted/duplicated/lost lines, drop that model's
     `prompts/` variant and stop recommending hashline for it. Log the result in
     `CHANGELOG.md`.
4. **End state:** when no enrolled model fails the removal test, archive the repo. It may
   retain value for small local models — that becomes the README's only claim.

## Why

Sutton's Bitter Lesson, applied to harnesses: machinery that compensates for a model
weakness loses value with every model release, and hides the improvement when it arrives
(the workaround keeps firing, so nobody notices it is no longer needed). An explicit
removal test makes the improvement visible instead.
