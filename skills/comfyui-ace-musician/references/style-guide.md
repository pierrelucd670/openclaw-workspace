# ACE Musician — Style Guide & Tuning

## ⚠️ Configuration critique ComfyUI

```
ComfyUI DOIT être lancé SANS --force-fp16.
Le modèle XL Turbo est en bf16 natif.
--force-fp16 cast bf16 → fp16 → silence total.
```

Commande correcte:
```bash
python main.py --listen 0.0.0.0 --port 8188 --cuda-device 0 --normalvram
```

```
User Prompt → LM (auto-expansion) → DiT Decoder (diffusion) → VAE → Audio
```

### LM (Language Model)
- Transforme un prompt simple en blueprint complet
- Génère métadonnées (BPM, key, structure), lyrics, captions détaillées
- Chain-of-Thought: raisonne avant de générer
- Désactivable avec `--no-lm` pour contrôle direct

### DiT Decoder
- XL (4B): 2560 hidden, 32 layers → qualité maximale
- 2B: 2048 hidden, 24 layers → bon compromis
- Turbo: distillation, 8 steps, pas de CFG
- Base/SFT: 50 steps, CFG 3-5

## Optimisation T4 16GB

### Stratégie mémoire
```
GPU: Tesla T4 (16 GB)
XL Turbo (~9 GB INT8) + LM 1.7B (~3.5 GB) = ~12.5 GB
Reste ~3.5 GB pour buffers → OK avec CPU offload partiel
```

### Recommandé: XL Turbo + LM 1.7B + CPU offload + INT8
```bash
# Dans ComfyUI: activer --cpu-vae, --lowvram
python3 main.py --cpu-vae --lowvram --gpu-only
```

### Fallback: 2B Turbo + LM 0.6B (si OOM)
```bash
# Plus léger, très rapide, bonne qualité
python3 generate.py --model turbo --lm 0.6B
```

## Paramètres avancés

### Duration vs Qualité
| Durée | Qualité | Note |
|-------|---------|------|
| 30-90s | Excellente | Courts extraits, boucles |
| 2-4 min | Très bonne | Sweet spot |
| 5-7 min | Bonne | Légère baisse de cohérence |
| 8-10 min | Variable | Peut devenir répétitif |

### BPM par genre
| Genre | BPM typique |
|-------|------------|
| Hip-Hop/Trap | 60-100 (half-time) / 120-160 |
| House | 120-130 |
| Techno | 125-140 |
| Drum & Bass | 160-180 |
| Dubstep | 140-150 |
| Rock | 100-140 |
| Pop | 100-130 |
| Jazz | 80-160 (swing feel) |
| Classical | Variable |

### Keys & Moods
| Key | Mood |
|-----|------|
| C major | Bright, innocent |
| D minor | Melancholic, serious |
| E minor | Dark, passionate |
| F major | Warm, pastoral |
| G major | Joyful, triumphant |
| A minor | Sad, tender |
| Bb minor | Gloomy, dramatic |

## Tâches spéciales

### Cover
```
"cover of [original.wav] in [new style], [prompt]"
```
Recrée un morceau existant dans un nouveau style.

### Repaint
```
"repaint 30-60s of [audio.wav] with [new prompt]"
```
Édite un segment spécifique.

### Extract (stems)
```
"extract vocals from [audio.wav]"
"extract drums from [audio.wav]"
```
Sépare les pistes individuelles.

### Vocal2BGM
```
"generate accompaniment for [vocals.wav]"
```
Crée un backing track pour une piste vocale.

### Lego (multi-track)
```
"assemble [bass.wav] [drums.wav] [guitar.wav] into full mix"
```

## Dépannage

### OOM (Out of Memory)
1. Passer au 2B: `--model turbo`
2. Désactiver LM: `--no-lm`
3. Réduire durée: `--duration 120`
4. Activer lowvram dans ComfyUI

### Sortie silencieuse / bruit
1. Vérifier le sampler/scheduler (Turbo = euler/normal)
2. Pour SFT/Base: augmenter CFG légèrement (4→5)
3. Vérifier que le modèle est bien chargé (.safetensors complet)

### Qualité insuffisante
1. Passer de Turbo → SFT (plus de steps)
2. Passer de 2B → XL
3. Améliorer le prompt (plus détaillé, structure explicite)
4. LM disable → enable (auto-expansion améliore la cohérence)

## Benchmarks (vérifiés live 19 mai 2026)

### XL Turbo (T4 16GB, FP16, offload)
- 2:40 song (160s): ~120s génération
- Format: FLAC → converti MP3 320kbps (ffmpeg)

### XL Turbo (4090, 24GB — théorique)
- 4 min song: ~8-12s
- 10 min song: ~20-30s

## LoRA Training

Fine-tune ACE-Step sur ton style:
```bash
# Gradio Web UI: "LoRA Training" tab
# 8 chansons minimum, 1h sur RTX 3090 (12GB)
# Formats: .wav, .mp3, .flac
```

Output: `acestep_lora.safetensors` → à placer dans `ComfyUI/models/loras/`
