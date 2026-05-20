---
name: creative-hub
description: Studio de création multimédia local — Vidéo (LTX-2), Audio (Qwen3-TTS), 3D (Hunyuan3D 2.0), Image (ComfyUI). Orchestré via SSH (Win11) et exécution locale (Serveur AI).
---

# 🎬 Creative Hub — Studio Multimédia Local

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR (SpicyClaw)                 │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ ComfyUI  │  │  LTX-2   │  │ Qwen3-TTS│  │Hunyuan3D │ │
│  │  Image   │  │  Vidéo   │  │  Audio   │  │   3D     │ │
│  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤ │
│  │ T4 #0    │  │ RTX 3060 │  │ T4 #1    │  │ T4 #2    │ │
│  │ Serveur  │  │ Win11    │  │ Serveur  │  │ Serveur  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Capacités par modalité

### 🎨 Image — ComfyUI (T4 #0, Serveur)
- **Path**: `/home/peyo/ComfyUI`
- **Skills**: `comfyui-nsfw-photoreal`, `comfyui-pony-nsfw-studio`, `comfyui-ultimate-upscaler`
- **Pipeline**: JuggernautXL + ReActor (dufour_face)

### 🎬 Vidéo — LTX-2 (RTX 3060 12GB, Win11)
- **Path**: `G:\ai\ltx2`
- **Accès**: SSH `peyo6@192.168.2.13`
- **Env**: Conda `G:\ai\ltx2\conda_env` (Python 3.12, CUDA 12.4)
- **Repo**: https://github.com/Lightricks/LTX-2
- **Capacité**: 4K native, 20s, audio synchronisé

### 🎵 Audio — Qwen3-TTS (T4 #1, Serveur)
- **Path**: `/home/peyo/ai-stack/qwen3-tts/Qwen3-TTS`
- **Venv**: `/home/peyo/ai-stack/qwen3-tts/venv`
- **GPU**: `CUDA_VISIBLE_DEVICES=1`
- **Repo**: https://github.com/QwenLM/Qwen3-TTS
- **Capacité**: Voice cloning, voice design, streaming, 10+ langues

### 🧊 3D — Hunyuan3D 2.0 (T4 #2, Serveur)
- **Path**: `/home/peyo/ai-stack/hunyuan3d/Hunyuan3D-2`
- **Venv**: `/home/peyo/ai-stack/hunyuan3d/venv`
- **GPU**: `CUDA_VISIBLE_DEVICES=2`
- **Repo**: https://github.com/Tencent-Hunyuan/Hunyuan3D-2
- **Capacité**: High-res 3D assets, textures PBR, multi-view

## Usage

### Vidéo (Win11 via SSH)
```bash
ssh peyo6@192.168.2.13 "cd G:\ai\ltx2 && conda activate conda_env && python generate.py --prompt '...'"
```

### Audio (Serveur)
```bash
CUDA_VISIBLE_DEVICES=1 /home/peyo/ai-stack/qwen3-tts/venv/bin/python generate.py --text "..." --voice clone
```

### 3D (Serveur)
```bash
CUDA_VISIBLE_DEVICES=2 /home/peyo/ai-stack/hunyuan3d/venv/bin/python generate.py --image input.png
```

## Intégration FORGE

Chaque échec de génération → `forge_postmortem.py <domain>` → artefact dans Qdrant.
Avant chaque tâche → `forge_preflight.py <domain>` → leçons injectées.
