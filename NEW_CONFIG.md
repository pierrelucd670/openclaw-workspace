# Optimisations appliquées

## 1. Concurrence
- `maxConcurrent` passé de **8** à **16** dans `openclaw.json` (déjà redémarré).  
- Cela permet jusqu’à 16 tâches simultanées (CPU et sous‑agents) tant que la RAM le supporte.

## 2. Swap
- Deux fichiers swap actifs :
  - `/swap.img` – 8 GiB
  - `/swapfile` – 16 GiB
- Aucun swap n’est utilisé actuellement (`USED 0B`).
- Ils offrent une marge de sécurité importante pour les pics de mémoire.

## 3. ZRAM (compression mémoire)
- Non activé ; si besoin, on pourra le mettre en place avec `modprobe zram`.

## 4. GPU disponible
| GPU | Modèle | Mémoire totale | Mémoire utilisée | Température | Puissance |
|-----|--------|----------------|------------------|------------|----------|
| 0   | Tesla T4 | 15 GiB | ~2 GiB (processes Python) | 56 °C | 36 W |
| 1   | Tesla T4 | 16 GiB | 0 GiB | 57 °C | 35 W |
| 2   | Tesla T4 | 15 GiB | 0 GiB | 57 °C | 36 W |

## 5. Plugins activés (boost de capacités)
```json
"plugins": {
  "entries": {
    "browser": { "enabled": true },
    "summarize": { "enabled": true },
    "openai-whisper": { "enabled": true },
    "weather": { "enabled": true },
    "video-frames": { "enabled": true },
    "nano-pdf": { "enabled": true },
    "diffs": { "enabled": true },
    "taskflow": { "enabled": true }
  }
}
```
Ces plugins permettent :
- Navigation web automatisée
- Résumé de contenus (articles, PDF, vidéos)
- Transcription audio locale
- Accès météo
- Extraction de frames vidéo
- Édition PDF via CLI
- Diff generation & partage
- Orchestration de jobs complexes (`taskflow`).

## 6. Modèle par défaut
- `openrouter/deepseek/deepseek‑v4‑flash` choisi comme modèle principal.

## 7. Remarques & prochaines étapes
- **Surveiller** l’utilisation CPU/Mémoire avec `htop` ou `top`.
- **Activer ZRAM** si la pression mémoire devient critique.
- **Créer des jobs** `taskflow` pour exploiter les GPU T4 (ex. génération d’images NSFW avec Stable Diffusion).
- **Nettoyer** les logs périodiquement (`journalctl -u openclaw-gateway.service` & workspace logs).

---
*Ce fichier résume toutes les optimisations appliquées et constitue la référence pour la configuration actuelle.*