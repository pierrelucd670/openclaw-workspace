---
name: comfyui-nsfw-photoreal
description: Génération NSFW photoréaliste haute qualité avec JuggernautXL/EpicRealism/Lustify + LoRAs NSFW + face restore pipeline. 16 catégories documentées.
when: L'utilisateur veut générer des images NSFW réalistes (photos, corps humain, scènes intimes) avec un rendu photo-quality professionnel.
---

# ComfyUI NSFW Photoreal

Génération NSFW photoréaliste pour humains réalistes. 3 modèles supportés.

## Guide rapide des settings par modèle

| Modèle | CFG | Sampler | Steps | VAE | CLIP skip | Particularité |
|--------|-----|---------|-------|-----|-----------|---------------|
| **JuggernautXL Ragnarok** | 6-8 | DPM++ 2M Karras | 25-30 | sdxl_vae | 2 | "RAW photo, photorealistic:1.3" |
| **EpicRealismXL PureFix** | 5 | DPM++ 2M Karras | 20-25 | sdxl_vae | 2 | Peu/pas de negatives |
| **LustifySDXLNSFW ggwpV7** | 6-7 | DPM++ 2M Karras | 25 | sdxl_vae | 2 | Tags Danbooru + langage naturel |

## Prompt formula JuggernautXL (testé, 8/10 qualité)

```
RAW photo, (photorealistic:1.3), [description sujet], [pose], [éclairage], 85mm f/1.8, film grain, natural skin texture, 8k uhd
```

**Negative**: `(worst quality, low quality:1.4), plastic skin, doll-like, overexposed skin, (oversaturated:1.3), bad anatomy, bad hands, extra limbs, cartoon, 3d render`

## Catégories NSFW supportées (prompts dans NSFW_PROMPTING_GUIDE.md)

1. Solo femme — poses simples
2. Masturbation
3. Blowjob / Oral sex
4. Doggystyle
5. Missionnaire
6. Gangbang (PonyDiffusion recommandé)
7. BDSM / Bondage
8. Gay / Hommes (voir gay-nsfw-suite)
9. Sissy / Femboy / Crossdresser
10. Trans / Pre-op
11. Cunnilingus
12. Bukkake / Cum
13. Lesbien / Femme sur femme
14. Hentai / Anime (voir pony-nsfw-studio)
15. Furry / Anthro (voir pony-nsfw-studio)
16. POV (Point of View)

## Pipeline

1. **Checkpoint** → JuggernautXL (ou EpicRealism/Lustify)
2. **VAE** → sdxl_vae.safetensors (LOAD explicite, pas built-in)
3. **CLIP skip** → -2
4. **LoRA** → NSFW Master (0.5-0.7), dildo (0.5), AndroCore (0.5)
5. **KSampler** → CFG selon modèle
6. **VAE Decode** → via SDXL VAE
7. **Face Restore** → ReActorRestoreFace (GFPGAN/CodeFormer)
8. **Upscale** → Ultimate SD Upscale (optionnel)

## Samba notification

Après chaque génération, exécuter `scripts/notify_samba.sh` pour que Windows voie le fichier immédiatement.

## Script

Voir `scripts/generate_nsfw_photoreal.py`
