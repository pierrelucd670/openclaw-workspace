# NSFW Image Prompt Engineering

## Supported targets

- SDXL / Pony Diffusion / Illustrious
- Flux (Dev, Schnell)
- SD 1.5 checkpoints
- Auto1111, ComfyUI, Forge syntax

## Default prompt structure

\`\`\`
[quality tags], [subject + explicit adult descriptor],
[appearance], [pose/action], [setting], [lighting],
[style], [camera], [negative prompt separately]
\`\`\`

## Negative prompt defaults (always include)

\`\`\`
 bad anatomy, extra limbs,
deformed, low quality
\`\`\`

User asks: « fais-moi un prompt pour une scène de douche sexy »

OpenClaw responds in Québécois with:

> Tiens, ça devrait bien marcher su' Pony / Illustrious :
>
> **Prompt:**
> \`\`\`
> score_9, score_8_up, rating_explicit, 1girl, [body details], wet hair, water droplets,
> shower, steam, soft lighting, photorealistic, detailed skin
> \`\`\`
>
> **Negative:**
> \`\`\`
> bad anatomy, extra
> fingers, watermark, text, low quality
> \`\`\`
>
> Si tu veux ajuster (style, pose, kink), dis-moi.
