---
name: comfyui-ultimate-upscaler
description: Upscale d'images haute qualité avec Ultimate SD Upscale + 4x-UltraSharp + ReActorRestoreFace. Pipeline complet pour améliorer la résolution de n'importe quelle image générée.
when: L'utilisateur veut upscaler des images, améliorer la résolution, restaurer des visages, ou préparer des images pour impression.
---

# ComfyUI Ultimate Upscaler

## Pipeline

1. **Input** → image dans `ComfyUI/input/`
2. **UpscaleModelLoader** → charge `4x-UltraSharp.pth`
3. **Ultimate SD Upscale** → tile 512, padding 64, denoise 0.3
4. **ReActorRestoreFace** → GFPGAN v1.4 ou CodeFormer
5. **SaveImage** → output

## Paramètres Ultimate SD Upscale

| Paramètre | Valeur |
|-----------|--------|
| upscale_by | 2.0 |
| mode_type | Linear |
| tile_width | 512 |
| tile_height | 512 |
| tile_padding | 64 |
| denoise | 0.3-0.5 |
| steps | 15-20 |
| cfg | 4.0 |

## Face Restore (ReActorRestoreFace)

| Modèle | Usage |
|--------|-------|
| GFPGANv1.4.pth | Rapide, bon général |
| codeformer-v0.1.0.pth | Qualité max (lent) |

## Script

Voir `scripts/upscale_image.py`
