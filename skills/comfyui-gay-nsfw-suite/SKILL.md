---
name: comfyui-gay-nsfw-suite
description: Suite spécialisée pour contenu NSFW masculin/queer. Combine HomofidelisXL, PornWorks BadBoysPhoto, Starstruck GayYaoi et la LoRA Gay NSFW SDXL.
when: L'utilisateur demande du contenu gay, masculin, queer — photos réalistes d'hommes, nus masculins, bodybuilders. Utiliser PornWorks pour l'anatomie masculine parfaite.
---

# ComfyUI Gay NSFW Suite

3 modèles spécialisés contenu masculin/queer.

## PornWorks BadBoysPhoto v06 (⭐ meilleur pour hommes)

| Paramètre | Valeur | Note |
|-----------|--------|------|
| **CFG** | **4** | PAS 6-7! CFG 4 = officiel |
| **Sampler** | `dpmpp_2m_sde_gpu` | Pas DPM++ 2M standard |
| **Scheduler** | karras | |
| **Steps** | 30 | |
| **VAE** | sdxl_vae.safetensors | |
| **Negative** | `score_6, score_5, score_4` | Pony negative |

- Prompt: langage naturel DESCRIPTIF + tags Danbooru
- Score tags compatibles: `score_9, score_8_up, score_7_up`
- Résolution: 1024×1024 ou 1024×1536

## HomofidelisXL v30

- CFG 5-7, DPM++ 2M Karras, 25-28 steps
- VAE: sdxl_vae
- Negative: `extra penis, double penis, misplaced penis, two penises`
- **1 personnage seulement** = meilleure anatomie
- LoRA Gay NSFW: 0.5-0.6 (pas plus haut)
- Résolution: 1024×1536 (full body portrait)

## Starstruck GayYaoi v10

- Style anime/yaoi
- CFG 5-7, DPM++ 2M Karras, 25 steps
- Tags anime/yaoi + langage naturel

## Script

Voir `scripts/generate_gay_nsfw.py`
