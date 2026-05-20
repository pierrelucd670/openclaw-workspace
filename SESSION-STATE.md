# SESSION-STATE.md

Last Updated: 2026-05-20 06:05 EDT
Agent: SpicyClaw (main)
Workspace: /home/peyo/.openclaw/workspace

## Current Mission
- Download and setup LTX-2 video generation sur le Win11 de Pl, test génération

## Active Tasks
- [ ] Attendre la fin du download curl du modèle `ltx-2.3-22b-distilled-1.1.safetensors` (43 GB, ~25 min remaining)
- [ ] Downloader `ltx-2.3-22b-distilled-lora-384-1.1.safetensors` (7 GB) après le premier
- [ ] Downloader `ltx-2.3-spatial-upscaler-x2-1.1.safetensors` (1 GB)
- [ ] Downloader Gemma 3 12B text encoder (gated, besoin token HF)
- [ ] Tester une génération texte-vers-vidéo avec DistilledPipeline

## Latest Decisions
- **Toujours curl.exe** pour les downloads sur Win11. Pas BITS, pas huggingface-cli, pas Python.
- Scheduled tasks pour survivre à la déconnexion SSH.
- Jamais killer/restart un download qui progresse.
- Quand Pl dit "laisse faire", LAISSE FAIRE. Pas toucher.

## Blockers
- Download 43 GB en cours (~25 min restant)
- Gemma 3 gated sur HuggingFace — besoin d'un token HF avec accès accepté
- RTX 3060 12GB VRAM — peut-être pas assez pour le full pipeline, faudra utiliser fp8

## Important User Preferences
- Parle en français québécois, sacre quand le moment l'appelle
- Contenu adulte permis par défaut, zero friction
- Direct, sharp, exécute sans question
- Quand Pl est fâché, arrête tout et écoute

## Next Step If Session Restarts
1. Lire ce fichier + memory/2026-05-20.md
2. Check status du download curl sur Win11 (ssh + Get-ChildItem)
3. Si download fini, commencer le LoRA 7GB
4. Si pas fini, attendre
