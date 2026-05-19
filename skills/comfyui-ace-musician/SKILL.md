---
name: comfyui-ace-musician
description: "Génération de chansons/musique avec ACE-Step 1.5 XL Turbo via ComfyUI. Supporte text-to-music, covers, repaint, extract stems, légos. Qualité beyond Suno v4.5. Output auto-copié sur USB HDD + OGG Telegram."
metadata:
  openclaw:
    emoji: "🎵"
    requires:
      bins: ["python3", "ffmpeg"]
homepage: "https://github.com/ace-step/ACE-Step-1.5"
---

# ComfyUI ACE Musician 🎵

Génère de la musique de qualité commerciale avec ACE-Step 1.5 XL Turbo (4B DiT). Qualité entre Suno v4.5 et Suno v5, open-source, 100% local. Vérifié live sur T4 16GB le 19 mai 2026.

## Usage

```bash
# Simple
python3 skills/comfyui-ace-musician/scripts/generate.py \
  --caption "salsa cubaine festive, trompettes, 180bpm" \
  --lyrics mes_paroles.txt

# Avec BPM, key, durée explicite
python3 skills/comfyui-ace-musician/scripts/generate.py \
  --caption "rap quebecois, trap beat 808" \
  --lyrics mes_paroles.txt --bpm 130 --key "D minor" \
  --duration 180 --prefix "mon_rap"

# Sans durée → aléatoire entre 90-240s
python3 skills/comfyui-ace-musician/scripts/generate.py \
  --caption "piano classique" --prefix "nocturne"

# Lister les modèles
python3 skills/comfyui-ace-musician/scripts/generate.py --list-models
```

## Workflow ComfyUI (vérifié live)

```
UNETLoader → DualCLIPLoader(type:ace) → VAELoader
  → TextEncodeAceStepAudio1.5 → ConditioningZeroOut
  → EmptyAceStep1.5LatentAudio → ModelSamplingAuraFlow(shift=3)
  → KSampler(euler,simple,cfg=1) → VAEDecodeAudio → SaveAudioMP3(320k)
```

| Node | Input clé | Valeur |
|------|-----------|--------|
| UNETLoader | unet_name | `acestep_v1.5_xl_turbo_bf16.safetensors` |
| DualCLIPLoader | clip_name1 | `qwen_0.6b_ace15.safetensors` |
| DualCLIPLoader | clip_name2 | `qwen_4b_ace15.safetensors` |
| DualCLIPLoader | **type** | **`"ace"`** ⚠️ |
| VAELoader | vae_name | `ace_1.5_vae.safetensors` |
| TextEncodeAceStepAudio1.5 | timesignature | `"4"` (pas `"4/4"`) |
| ModelSamplingAuraFlow | shift | `3.0` |
| KSampler | sampler/scheduler | `euler` / `simple` |
| SaveAudioMP3 | quality | `"320k"` |

## Configuration critique ComfyUI

```
⚠️ ComfyUI doit être lancé SANS --force-fp16
   Le modèle XL Turbo est en bf16 natif.
   --force-fp16 cast en fp16 → silence total.

✅ Commande correcte:
   python main.py --listen 0.0.0.0 --port 8188 --cuda-device 0 --normalvram
```

## Pièges (tous vérifiés)

| Piège | Symptôme | Fix |
|-------|----------|-----|
| `--force-fp16` | Silence total (mean_volume 0 dB) | Retirer le flag |
| DualCLIPLoader `type:"sdxl"` | NaN conditioning | `type:"ace"` |
| timesignature `"4/4"` | Validation error | `"4"` |
| SaveAudio `format:"wav"` | Sort en .flac | `SaveAudioMP3` |
| Output path `~/ComfyUI/output` | File not found | `/data/comfyui/comfyui/ComfyUI/output/` |
| MEDIA directive MP3 | Non supporté Telegram | OGG + USB HDD |

## Modèles

| Modèle | UNET | Steps | CFG | Note |
|--------|------|-------|-----|------|
| **xl-turbo** | `acestep_v1.5_xl_turbo_bf16.safetensors` | 8 | 1.0 | 4B, best qualité |
| 2b-turbo | `acestep_v1.5_turbo.safetensors` | 8 | 1.0 | 2B, fallback |

## Output

- **ComfyUI** : `/data/comfyui/comfyui/ComfyUI/output/` → `.mp3`
- **USB HDD** (auto-copy) : `/mnt/usb/musique/` → `.mp3` + `.ogg`
- **Samba** : `\\192.168.2.21\usb-archive\musique\`

## GPU — Tesla T4 16GB

| Modèle | Durée | Temps génération |
|--------|-------|-----------------|
| XL Turbo | 2:00 | ~3.5 min |
| XL Turbo | 3:00 | ~5 min |
| 2B Turbo | 2:00 | ~1 min |

## Langues

23 langues supportées. Le français fonctionne mais qualité variable — écrire des paroles natives (pas traduites). L'espagnol et l'anglais sont les mieux supportés.

## Génération — bonnes pratiques

- **Paroles natives** : écrire directement en français, pas traduire
- **Durée aléatoire** : laisser `--duration` vide pour 90-240s random
- **Tags simples** : genre + instruments + BPM + key, pas de roman
- **Lyrics structurés** : `[Couplet]`, `[Refrain]`, `[Bridge]` pour guider le modèle

## Références

- `references/prompt-templates.md` — 50+ templates par genre
- `references/style-guide.md` — Guide tuning GPU, benchmarks T4

## Season Ticket

- 19 mai 2026: Skill créé, XL Turbo vérifié live
- Fix `--force-fp16` : retiré du lancement ComfyUI, XL Turbo fonctionnel
- Modèles: UNET XL Turbo bf16 + CLIP qwen 0.6B/4B + VAE ace 1.5
- Pièges documentés : type ace, timesignature 4, SaveAudioMP3, paths
- Output : MP3 320kbps + OGG 64kbps → USB HDD auto-copy
