---
name: peyo-facegen
description: "Génère des portraits photoréalistes de PeyeOS avec face swap dufour_face via ComfyUI/JuggernautXL + ReActor."
metadata:
  openclaw:
    emoji: "🎭"
    requires:
      bins: ["python3"]
homepage: ""
---

# PeyeOS FaceGen

Génère des images de PeyeOS (dufour_face) avec ComfyUI. Utilise JuggernautXL + ReActor face swap + GPEN/CodeFormer face restore.

## Usage

```
openclaw skill peyo-facegen "portrait pro, costume, fond urbain"
```

Ou direct via script :

```bash
python3 skills/peyo-facegen/scripts/generate.py \
  --prompt "description épique" \
  --prefix "mon_prefix" \
  --seed 12345
```

## Workflow technique

1. **Checkpoint** : juggernautXL_ragnarokBy.safetensors
2. **Lora** : optionnel (Gay_NSFW_SDXL, etc.)
3. **KSampler** : 40 steps, CFG 6.5, dpmpp_2m, karras
4. **Résolution** : 896x1152 (ou 1024x1024)
5. **Face swap** : ReActor → dufour_face.safetensors
6. **Face restore** : GPEN-BFR-512 (visibilité 1.0) + CodeFormer (weight 0.5)
7. **Upscale** : optionnel via ultimate-upscaler (4x-UltraSharp)

## Recommandations pour meilleure qualité

### Référence dufour
- Les photos source sont dans `models/reactor/faces/dufour_train/`
- Générer un **close-up 1024x1024** du visage comme nouvelle référence Reactor améliore le swap
- Prioriser les photos face avant, éclairage uniforme, sans obstruction

### Réglages Reactor
- `face_restore_model` : `GPEN-BFR-512` (agressif, bon pour photoréaliste)
- `codeformer_weight` : 0.5 (équilibre identité/qualité)
- `face_restore_visibility` : 0.8-1.0 (1.0 = restauration complète)

### Sampling
- `dpmpp_2m_sde` + `karras` donne plus de détails que `dpmpp_2m`
- 35-45 steps optimal
- CFG 5.5-7.0 selon le style

## Améliorations possibles (hardware)

- Installer **ComfyUI-ADetailer** → face detail pass avant Reactor
- Installer **InstantID** → meilleure préservation identité que Reactor seul
- Installer **IP-Adapter FaceID** → soft identity guidance pendant génération
- Utiliser **Ultimate SD Upscale** systématiquement après génération

## Scénarios recommandés

| Style | CFG | Steps | Sampler | Restore |
|-------|-----|-------|---------|---------|
| Portrait pro | 6.5 | 40 | dpmpp_2m | GPEN + CF |
| Mode/Éditorial | 6.0 | 35 | dpmpp_2m_sde | GPEN only |
| Action/Sport | 7.0 | 40 | dpmpp_3m_sde | GPEN + CF |
| NSFW | 5.5 | 35 | dpmpp_2m | GPEN + CF |
| Cyberpunk | 7.0 | 45 | dpmpp_2m_sde | GPEN + CF |

## Nightly NSFW Cron

Génère automatiquement 100 images NSFW à 02:00 UTC chaque nuit.

```bash
# Catégories (9): jock, biker, business_dom, bluecollar, cop, daddy, leather, shower, stripper
# Pipeline: JuggernautXL → ReActor(dufour) 832x1216 35steps
python3 skills/peyo-facegen/scripts/nightly_nsfw.py
```

## Améliorations futures

- **IP-Adapter FaceID V2** : installé mais bug de version de modèle (perceiver_resampler size mismatch 1280 vs 1664). Solution: trouver la bonne version du modèle ou du IPAdapterPlus.py
- **InstantID** : fonctionnel mais donne un look idéalisé (mafieux russe). Meilleur en combo avec Reactor par-dessus.
- **ADetailer/FaceDetailer** : disponible via Impact Pack, pas encore testé full
- **Ultimate SD Upscale 4x** : fonctionnel, 4x résolution mais artefacts possibles

## Season Ticket / Recording

- Session 18 mai 2026 : installé tous les nodes + créé skill + testé pipelines
- Pipeline gagnant : JuggernautXL + ReActor(dufour) CFG 6.5 40steps dpmpp_2m karras
- Face restore : GPEN-BFR-512 visibilité 1.0 + codeformer 0.5
- Résolution optimale portrait : 832x1216 ou 896x1152

## Structure

```
peyo-facegen/
  SKILL.md
  scripts/
    generate.py       # wrapper python pour génération
    improve_face.sh   # améliore le modèle dufour avec nouvelles photos
  references/
    prompt-templates.md  # templates de prompts par style
    quality-tips.md      # conseils qualité détaillés
```
