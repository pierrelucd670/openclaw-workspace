---
name: comfyui-bondage-artist
description: Génération bondage/shibari. Supporte PonyDiffusion (style anime) et JuggernautXL (réaliste humain) avec les LoRAs shibari et suspension.
when: L'utilisateur demande des images de bondage, shibari, cordes, suspensions, BDSM.
---

# ComfyUI Bondage Artist

## Sur JuggernautXL (⭐ humain réaliste)

| Paramètre | Valeur |
|-----------|--------|
| CFG | 6-7 |
| Sampler | DPM++ 2M Karras |
| Steps | 25-28 |
| VAE | sdxl_vae |
| CLIP skip | 2 |
| Prompt | `RAW photo, (photorealistic:1.3), naked woman bound, rope bondage, shibari, 85mm f/1.8` |
| Negative | `(worst quality, low quality:1.4), cartoon, anime, 3d render` |
| LoRA shibari | 0.5-0.6 |

## Sur PonyDiffusionV6XL (style anime/semi-real)

| Paramètre | Valeur |
|-----------|--------|
| CFG | 5 |
| Sampler | Euler |
| Steps | 28-30 |
| CLIP skip | -2 |
| Score tags | Chaîne complète + rating_explicit + source_anime |
| LoRA shibari | 0.6-0.8 |
| LoRA suspension | 0.6-0.7 |

## LoRAs disponibles

| LoRA | Taille | Usage | Poids |
|------|--------|-------|-------|
| shibari_1990s_ZiB | 85MB | Motifs shibari, cordes | 0.5-0.8 |
| suspension_bondage_hng | 219MB | Suspensions | 0.6-0.7 |

## Script

Voir `scripts/generate_bondage.py`
