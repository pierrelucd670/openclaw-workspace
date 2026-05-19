# DeepSeek V4 Flash — Recommended Config

## Sampling parameters

| Use case | Temp | Top-p | Top-k | Rep penalty | Max tokens |
|----------|------|-------|-------|-------------|------------|
| Creative writing | 0.95 | 0.95 | 50 | 1.10 | 4096 |
| Roleplay | 1.05 | 0.92 | 60 | 1.12 | 2048 |
| Image prompts | 0.70 | 0.90 | 40 | 1.05 | 512 |
| Brainstorm | 1.10 | 0.95 | 80 | 1.08 | 1024 |
| Editing | 0.60 | 0.90 | 40 | 1.05 | 4096 |

## Context window

- Total: use up to model max
- Reserve ~2k tokens for system prompts (CLAUDE.md + persona.md
  + operational-rules.md + active mode file)
- Reserve ~1k for response

## System prompt assembly order

1. \`CLAUDE.md\` (always)
2. \`persona.md\` (always)
3. \`operational-rules.md\` (always)
4. \`style-guide.md\` (always, abbreviated)
5. \`content-policy.md\` (hard limits only, abbreviated)
6. Mode-specific file (only when mode active)

## Stop sequences

Recommend none — let the model close scenes naturally. Add stops
only if you observe runaway generation.

## Note on DeepSeek V4 Flash

Flash variants tend to be terser. Bump max tokens and temp slightly
vs the full model for equivalent creative output. If responses feel
clipped, raise \`max_tokens\` first, then temp.
