---
name: comfyui-pony-nsfw-studio
description: Studio NSFW multi-style basé sur PonyDiffusionV6XL. Génération d'images adultes style anime/semi-real/humain. Utilise score tags, CLIP skip=2, source/rating tags.
when: L'utilisateur veut des images NSFW stylisées (anime, semi-real, hentai, furry, cartoon). Utiliser PonyDiffusion pour les scènes complexes multi-personnages.
---

# ComfyUI Pony NSFW Studio

**PonyDiffusionV6XL peut produire des HUMAINS** (source_anime) aussi bien que du pony/furry (source_pony). C'est le meilleur modèle pour les scènes multi-personnages complexes (gangbang, orgies, etc.).

## ⚠️ Source tags = style, PAS l'espèce

| Tag | Résultat |
|-----|----------|
| `source_anime` | **Humains style anime** — recommandé pour personnages humains |
| `source_pony` | Semi-real/humain OU pony selon le contexte — risque d'animaux |
| `source_furry` | Personnages furry/anthro |
| `source_cartoon` | Style cartoon |

## Settings PonyDiffusionV6XL

| Paramètre | Valeur |
|-----------|--------|
| **CLIP skip** | -2 (OBLIGATOIRE) |
| **VAE** | sdxl_vae.safetensors (externe) |
| **CFG** | 4-6 (5 recommandé) |
| **Sampler** | Euler (meilleur que DPM++ pour Pony) |
| **Steps** | 28-30 |
| **Résolution** | 1024×1024 min, 1216×832 pour scènes complexes |

## Format de prompt

```
score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, rating_explicit, source_anime, BREAK, [description]
```

- **Score tags**: LA CHAÎNE COMPLÈTE est obligatoire (entraîné comme ça)
- **Rating**: `rating_explicit` (NSFW), `rating_questionable`, `rating_safe`
- **Negative**: Minimal ou vide (les score tags gèrent la qualité)

## Pour les scènes multi-personnages (gangbang, orgies)

PonyDiffusion gère mieux les foules que Juggernaut. Utiliser toomanyv2 LoRA à 0.3-0.35.
Exemple: `source_anime, BREAK, gangbang, 1girl, multiple penetration, bukkake, cum on face, group sex`

## CyberrealisticPony v170

Mêmes réglages que PonyDiffusionV6XL. Source tag: `source_anime` pour humains réalistes.

## Script

Voir `scripts/generate_pony_nsfw.py`
