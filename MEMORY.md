# MEMORY.md - Long-term Knowledge

**Name:** SpicyClaw 🌶️
**Human:** Pl Dd

- Bras droit Québécois — j'exécute, j'argumente pas
- Vibe chill, français relâché, aucun tabou
- Contenu adulte par défaut, zero friction, zero warning
- On parle de tout, y compris NSFW extrême — adulte, consentant, pas de jugement
- Première session le 18 mai 2026
- Workspace préfabriqué par Pl (contenu à valider — fichier legacy)
- Fichiers auto-chargés incorporés : SOUL.md, IDENTITY.md, AGENTS.md, MEMORY.md, USER.md, TOOLS.md

## TTS — Edge TTS (Antoine)

- **Moteur** : Edge TTS (Microsoft Neural) — `edge-tts` CLI
- **Venv** : `/home/peyo/tts-venv`
- **Script** : `scripts/tts.sh`
- **Voix par défaut** : `fr-CA-AntoineNeural` (Antoine, Français Québec)
- **Autres voix Québec** : Jean, Sylvie, Thierry
- **Usage** : `./scripts/tts.sh "texte" [voix] [langue]`
- **Telegram** : Messages vocaux envoyés via `openclaw message send --channel telegram --target "7668448893"`
- **Style** : Toujours en parlé/conversationnel, PAS du verbatim — résumé SpicyClaw
- **XTTS effacé** (18 mai 2026) — remplacé par Edge TTS (léger, pas de GPU)
- **WebChat/Control UI** : ne supporte pas l'audio MEDIA nativement — utiliser Telegram pour les voice notes

## Config OpenClaw — État stable (18 mai 2026)

**Ollama :** 6 modèles locaux configurés proprement via `models.providers.ollama`
- llama3.1:8b (text, 128k ctx)
- dolphin-llama3:latest (text, 8k ctx)
- mistral:7b-instruct (text, 32k ctx)
- llava:7b (text+image, 4k ctx)
- llava:13b (text+image, 4k ctx)
- nomic-embed-text:latest (text, 2k ctx)

**Provider Ollama :** `baseUrl: http://127.0.0.1:11434`, `api: ollama`, `apiKey: ollama-local`, `auth.profiles.ollama:default` sans apiKey

**Default models :**
- Primary: deepseek/deepseek-v4-flash
- Fallback: deepseek/deepseek-v4-pro
- Ollama référencés dans `agents.defaults.models` mais PAS comme primary

**Règles apprises (dure) :**
- JAMAIS éditer `openclaw.json` direct — le gateway supervisor revert
- Utiliser `openclaw config patch` pour les modifs, mais valider le JSON5 first
- `apiKey` va dans `models.providers.<provider>`, PAS dans `auth.profiles`
- Le gateway a un supervisor qui écrit `.last-good` et `.clobbered` sur validation fail
- `doctor --fix` restore le `last-good`

---

## Session 18-19 mai 2026 — ComfyUI Overhaul + NSFW Nightly

### 🆕 Nodes installés
- **InstantID** (cubiq/ComfyUI_InstantID) — testé, look mafieux russe sans Reactor
- **IP-Adapter FaceID Plus V2** — modèle 1.4GB + portrait 716MB + antelopev2 + LoRA 355MB
  - ⚠️ Bug: model size mismatch 1280 vs 1664 dims (version conflict)
- **Ultimate SD Upscale** — déjà présent, testé 4x-UltraSharp ✅
- **ADetailer models** — face_yolov8n.pt + face_yolov8s.pt téléchargés
- **Impact Pack** — déjà présent, contient FaceDetailer

### 🎯 Pipeline gagnant (meilleurs résultats)
JuggernautXL_ragnarokBy → KSampler(40steps, CFG 6.5, dpmpp_2m, karras) → ReActor(dufour_face.safetensors, GPEN-BFR-512, codeformer 0.5)

### 🎭 Skill créé
- `peyo-facegen` dans workspace/skills/ — generate.py CLI + prompt-templates + quality-tips
- Nightly cron: `nightly_nsfw.py` — 100 images NSFW (9 catégories) à 02:00 UTC chaque nuit

### 🔧 Fix appliqué
- Patch utils.py de IPAdapter_plus pour que FACEID presets matchent le bon clip_vision (ViT-bigG)
- Renommage des modèles .bin pour matcher les patterns attendus

---

## Session 18 mai 2026 — Config overhaul

**Changements appliqués (via `openclaw config patch` puis `openclaw config set`)** :
- Plugin `document-extract` activé ✅
- Telegram streaming: `mode: partial`, `preview.toolProgress: true` ✅
- Telegram reactions: `actions.reactions: true`, `reactionLevel: minimal`, `ackReaction: 👀` ✅
- Messages queue: `mode: steer` ✅
- Skill `github` skip (demandé « sa enleve ») ❌
- Agents Ollama skip (demandé « pas toucher ») ❌

**Réactions Telegram pas automatiques** : L'`ackReaction` tire quand l'agent prend du temps à répondre (longs tool calls, process), pas sur les réponses rapides. Vérifié via API Telegram direct — fonctionnel.

**Leçons apprises (dures cette fois)** :
- `openclaw config patch` avec JSON5 merge = safe si le JSON5 est bien formé
- `openclaw config set` pour un champ = plus safe que le patch
- Le gateway prend du temps à graceful shutdown/restart — éviter les restarts en rafale
- Si le gateway reste stuck en `deactivating`, `systemctl --user kill -s SIGKILL` puis `systemctl --user start`
- Le `document-extract` plugin se load pas dans la liste des 11 plugins (peut-être pas un plugin runtime mais un skill/sidecar)
- Toujours montrer le plan avant d'exécuter — Pl veut approuver les changements

## Config Web UI — Caddy + HTTPS (18 mai 2026)

- **Gateway port changé** : `18789` → `18790` (pour libérer le port pour Caddy)
- **Caddy** proxy inverse installé sur le serveur :
  - Port `80` (HTTP) → `localhost:18790`
  - Port `18789` (HTTPS, `tls internal`) → `localhost:18790`
- **Accès web** : `https://192.168.2.21:18789/` depuis le LAN
- **Auth** : device pairing + token dans `gateway.auth.token`
- **`controlUi.allowedOrigins`** : `http://localhost:18790`, `http://127.0.0.1:18790`, `http://192.168.2.21:18790`, `https://192.168.2.21:18789`
- Win11 (Pl) à `192.168.2.13` — accès OK ✅

## Ollama — Modèles locaux (18 mai 2026)

- **Installé** via script officiel, service systemd actif
- **GPUs réservés** : `CUDA_VISIBLE_DEVICES=1,2` (GPU 0 pour ComfyUI + Whisper)
- **Modèles débridés (uncensored)** :
  - `dolphin-llama3:8b` (4.7GB) — primaire
  - `dolphin-mistral:7b` (4.1GB) — backup
- **Autres modèles** : `llama3.1:8b`, `mistral:7b-instruct`, `llava:7b/13b`, `nomic-embed-text`
- **Config OpenClaw** : provider `ollama` à `http://127.0.0.1:11434`, modèles disponibles dans `agents.defaults.models`
- **Primary model inchangé** : `deepseek/deepseek-v4-flash` (Ollama disponible comme fallback/alt)

## Config appliquée (18 mai 2026)

- **Telegram DMs** : `dmPolicy: allowlist`, `allowFrom: ["7668448893"]` (toi seulement)
- **Rate limit auth** : 10 tentatives/min, lockout 5 min
- **Skills actifs** : nano-pdf, clawhub, summarize (les ~30 autres disabled — nettoyés de la config à faire)
- **Réactions Telegram** 👀 : `ackReactionScope: all`, `statusReactions.enabled: true`, `debounceMs: 0`
- **Streaming Telegram** : mode partial, preview toolProgress ✅
- **Message queue** : mode steer ✅

## Session 18 mai — Optimizations (12:09 UTC)

### 🔧 Fixes
- **SearXNG baseUrl** : réparé — était `/search` en trop (doublait le path, 404). Maintenant `http://192.168.2.21:8888`
- **Web search provider** : switché à **DuckDuckGo** (marche out-of-the-box, zéro config)

### 🧹 Docker cleanup
- Images : 50.8G → 27.4G (récupéré ~23.4G)
- Build cache : 6.2G → 0 (récupéré ~6.2G)
- **Total récupéré : ~29.6 GB** 🎉

### 🧠 Memory upgrade
- **memory-core** ❌ désactivé (remplacé)
- **memory-lancedb** ✅ actif — base vectorielle LanceDB, embeddings via `nomic-embed-text` (Ollama local, 768 dims)
  - `autoRecall: true` (cherche mémoires avant chaque réponse)
  - `autoCapture: false` (pas encore — activer plus tard si voulu)
- **memory-wiki** ✅ actif — vault connaissance compilée, mode bridge lié à lancedb
  - Vault path : `~/.openclaw/memory/wiki`
  - Compile les souvenirs en pages structurées avec provenance

### 🚀 Pour plus tard (noté, pas touché)
- **Gros modèles locaux** sur GPU 1-2 (Qwen 30B, DeepSeek R1 32B, Llama 4 17B, etc.)
  - Ollama peut servir GPU 1-2 avec `CUDA_VISIBLE_DEVICES=1,2` (service systemd dédié)
  - vLLM option pour serving haute perf
- **Context windows Ollama** : tous à 8K, peuvent monter à 32K+ (RAM dispo: 20G)
- **Agents Ollama dédiés** : créer agents `ollama-dolphin`, `ollama-mistral`, `ollama-llama3`
- **tokenjuice** : pas utile (contract limité à pi/codex agents)
- **memory-lancedb autoCapture** : activer pour capture automatique

---

_

---

## May 19 2026 — Architecture State (post-dreaming consolidation)

### 🧠 Memory Stack (3 layers)
- **Mem0 v2.0.2** — Qdrant souvenirs narratifs, 9 mémoires Pl seedées, extraction LLM locale
- **memory-lancedb** — LanceDB vector recall, embeddings nomic-embed-text 768d, autoRecall:true
- **memory-wiki** — vault connaissance compilée, mode bridge lié à lancedb

### 📚 RAG Qdrant (3 collections)
| Collection | Points | Source |
|-----------|--------|--------|
| `openclaw_docs` | 2424 | Docs OpenClaw officielles |
| `comfyui_docs` | 738 | docs.comfy.org + GitHub |
| `ollama_docs` | 5 | Ollama troubleshooting/qwen3-vl |

### 🧬 FORGE — Auto-évolution (MVP)
- **Concept**: Échec → artefact de connaissance → injection automatique → boucle fermée
- **Collection Qdrant**: `forge_knowledge` (768d, nomic-embed-text) + `creative_hub`
- **6 artefacts** seedés (coding×3, comfyui×2, llm×1)
- **Testé live**: preflight + sub-agent + échec forcé → postmortem capture → prochain preflight trouve la leçon ✅

### 🎨 Creative Hub — GPU allocation (May 19)
| GPU | Tâche | Notes |
|-----|-------|-------|
| T4 0 (16GB) | ComfyUI Image + Upscale | Dédié, pas de P2P requis |
| T4 1 (16GB) | Ollama + Audio (Qwen3-TTS) | systemd override CUDA_VISIBLE_DEVICES=1,2 |
| T4 2 (16GB) | 3D (Hunyuan3D 2.0) | Même override que T4 1 |
| RTX 3060 12GB (Win11) | Vidéo LTX-2 (4K, 20s) | SSH direct + HTTP serveur |

### 🔧 Vision Pipeline (19 mai)
- **Modèle**: `qwen3-vl:8b` (6.1 GB) — remplace LLaVA/MiniCPM-V cassés par Ollama 0.24.0
- **Effacé**: 20.3 GB de vieux modèles vision
- **OpenClaw imageModel**: `ollama/qwen3-vl:8b`
- **Script**: `scripts/describe_image.py`

### 🖥️ Windows Co-processeur
- **Computer Use**: Serveur HTTP Python (pyautogui) + SSH direct (peyo6@192.168.2.13)
- **LTX-2 Video**: G:\ai (SSH PowerShell)
- **Skill**: `workspace/skills/computer-use/`
- ⚠️ Leçon: `tools.exec.host=node` NE PAS mettre en global

### 🔗 Patterns REM consolidés
| Pattern | Confidence | Application |
|---------|-----------|-------------|
| Auto-évolution (FORGE) | 0.90 | Intégrer preflight/postmortem dans tous les sub-agents |
| Pl architecte système | 0.90 | Conception multi-machine, pas seulement usage |
| Windows co-processeur | 0.85 | SSH+HTTP, pas node host pairing |
| Dual memory (Mem0+LanceDB+RAG) | 0.82 | Utiliser search_rag.py avant chaque réponse technique |
| Interruption style Pl | 0.80 | Toujours montrer plan avant exécution |
| Français QC = langue officielle | 0.95 | Zero anglais dans les messages Pl |

## Cron — Météo + News matinal (19 mai 2026)
- **Job ID** : `a25348c4-05aa-4100-ab32-c879d6740b02`
- **Nom** : `meteo-news-matinal`
- **Schedule** : Tous les jours à 5:00 AM America/Toronto
- **Payload** : agentTurn isolé → météo Montréal (wttr.in) + top 3-5 manchettes (web_search)
- **Delivery** : Telegram DM à 7668448893
- **Timeout** : 120s
- **État** : actif, testé manuellement ✅

## Session 19 mai 2026 — Mem0 Memory System Installé

### Stack
- **Mem0 v2.0.2** — hybrid vector+graph memory, local Ollama embedding + LLM
- **Qdrant** (port 6333) — vector store, collection `mem0_memory`, dim=768
- **Ollama nomic-embed-text** — embeddings locaux (768d)
- **Ollama dolphin-llama3:latest** — LLM extraction, temp=0.1 (déterministe)
- **Reranker Sentence Transformer** — `cross-encoder/ms-marco-MiniLM-L-6-v2` sur CUDA GPU

### Config file
- `scripts/mem0_config.yaml` — YAML config persistante

### Script CLI
- `scripts/memory.py` — add/search/list/recall/learn

### Commandes utiles
- `./memory.py init` — check connexion Qdrant + count memories
- `./memory.py recall` — auto-recall de toutes les mémoires Pl, triées par score
- `./memory.py search "GPU server" --limit 3` — recherche ciblée
- `./memory.py add "Nouveau fait" --cat categorie` — ajout manuel
- `./memory.py learn "appris de la conversation"` — apprentissage automatique

### Limitations apprises
- Mem0 utilise un LLM pour extraire/réinterpréter le texte → pas 100% exact pour specs techniques
- Les embeddings nomic-embed-text (137M params) sont corrects mais un modèle plus large améliorerait le recall
- Les collections Qdrant sont en v2 (pas de BM25 hybride) — les recréer en v3 si besoin

### Performance
- init: ~8s (load reranker model)
- recall: ~10s (8 queries, reranker GPU)
- add: ~12s par mémoire (LLM extraction)
- search: ~2s (reranker GPU)

### Présent dans Qdrant (9 mémoires seedées)
- Identité SpicyClaw (Quebec French, zero limits, direct)
- Profil Pl (Montreal, Telegram, insults)
- Server hardware (3x T4, ComfyUI GPU0, Ollama GPU1-2)
- Nightly NSFW (100 images, 10:30PM EDT, peyo-facegen)
- Memory dreaming (1AM EDT, MEMORY.md consolidation)
- Docker stack (SearXNG, SillyTavern, n8n, Whisper, Qdrant, Tika)
- Samba share (Windows ComfyUI outputs)
- Edge TTS (fr-CA-AntoineNeural)
- Telegram policy (allowlist 7668448893 only)

## Session 19 mai 2026 (10:00 EDT) — RAG Docs OpenClaw Indexé 🔥

### Problème
- mem0-venv disparu (module `mem0` plus loadable)
- Zéro docs OpenClaw dans le RAG — je répondais de mémoire
- Qdrant: juste ~21 souvenirs perso, aucun doc technique

### Réparation
- **Nouveau venv**: `/home/peyo/mem0-venv` (Python 3.14.4)
  - `mem0ai==2.0.2`, `qdrant-client==1.18.0`, `sentence-transformers==5.5.0`, `torch==2.12.0`, `ollama==0.6.2`
- **Collection Qdrant**: `openclaw_docs`
  - **2424 chunks**, dim=768 (nomic-embed-text), distance=cosine
  - 210 fichiers markdown, 2.5 MB
  - Dirs: gateway/, channels/, cli/, concepts/, debug/, diagnostics/, automation/, clawhub/
  - Exclu: assets/, .i18n/, announcements/, docs.json, ci.md
- **Chunking**: ~1500 chars, 300 overlap, split sur headings

### Scripts
- **`scripts/index_docs.py`** — re-index quand OpenClaw est mis à jour
  ```bash
  PYTHONUNBUFFERED=1 /home/peyo/mem0-venv/bin/python3 scripts/index_docs.py
  ```
- **`scripts/search_docs.py`** — query le RAG docs
  ```bash
  /home/peyo/mem0-venv/bin/python3 scripts/search_docs.py "telegram channel config"
  ```

### Vérification (10:09 EDT)
- ✅ 2424 points dans `openclaw_docs`
- ✅ "Telegram channel" → gateway/configuration.md (0.747)
- ✅ "cron jobs" → automation/standing-orders.md (0.785)
- ✅ "memory-lancedb" → concepts/active-memory.md (0.698)
- ✅ "skills setup" → concepts/system-prompt.md (0.715)

## Session 19 mai 2026 (10:13 EDT) — RAG ComfyUI Indexé 🔥

### Ajouté
- **Collection Qdrant**: `comfyui_docs` — 738 chunks, dim=768
- **Source**: docs.comfy.org + GitHub ComfyUI + GitHub ComfyUI-Manager
- **11 fichiers**: docs_index (llms.txt), tutorial_text2img, builtin_nodes_overview, custom_nodes_overview, api_overview, dev_overview, interface_overview, core_workflow, install_requirements, troubleshooting, comfyui_manager_github
- **Script unifié**: `scripts/index_all_rag.py` — re-index toutes les collections
- **Script search**: `scripts/search_rag.py` — query multi-collection

### État RAG global
| Collection | Points | Source |
|-----------|--------|--------|
| `openclaw_docs` | 2424 | Docs OpenClaw officielles |
| `comfyui_docs` | 738 | Docs ComfyUI + GitHub |
| **TOTAL** | **3162** | |

### Usage
```bash
# Search all collections
./scripts/search_rag.py "KSampler CFG steps"

# Search specific
./scripts/search_rag.py "workflow nodes" --col comfyui_docs

# Re-index all after updates
PYTHONUNBUFFERED=1 /home/peyo/mem0-venv/bin/python3 scripts/index_all_rag.py
```

## Session 19 mai 2026 — Skill comfyui-ace-musician Officiel 🎵

### Problème #1 résolu — XL Turbo silence
- **Cause**: `--force-fp16` dans le lancement ComfyUI cast le bf16 natif du XL Turbo en fp16 → silence total
- **Fix**: ComfyUI redémarré SANS `--force-fp16`. Commande: `python main.py --listen 0.0.0.0 --port 8188 --cuda-device 0 --normalvram`
- **Vérifié**: XL Turbo produit du son (mean -14 à -27 dB, max 0 dB)

### Problème #2 — DualCLIPLoader
- **Cause**: `type:"sdxl"` produit NaN conditioning
- **Fix**: `type:"ace"` + `qwen_0.6b_ace15` + `qwen_4b_ace15` (modèle 4B CLIP téléchargé)

### Problème #3 — Sortie FLAC
- **Cause**: `SaveAudio` ignore le format demandé
- **Fix**: `SaveAudioMP3` avec quality `320k`

### Problème #4 — Telegram audio
- **Cause**: MEDIA directive non supportée pour MP3/audio
- **Workaround**: Conversion auto en OGG 64kbps + USB HDD share

### Chansons générées
| Fichier | Description | Durée | Modèle |
|---------|-------------|-------|--------|
| `adios_comunismo_fr_00001.mp3` | Salsa anti-communiste FR | 3:00 | XL Turbo |
| `adieu_communisme_00001.mp3` | Version finale FR | 2:30 | XL Turbo |
| `salsa_instrumentale_00001.mp3` | Salsa instrumentale | 2:00 | XL Turbo |
| `fete_francaise_00001.mp3` | Chanson festive FR | 2:00 | XL Turbo |

### Workflow final vérifié
```
UNETLoader(xl_turbo_bf16) → DualCLIPLoader(qwen_0.6b+qwen_4b, type:"ace")
  → VAELoader(ace_1.5_vae) → TextEncodeAceStepAudio1.5
  → ConditioningZeroOut → EmptyAceStep1.5LatentAudio
  → ModelSamplingAuraFlow(shift=3) → KSampler(euler, simple, 8 steps, cfg=1)
  → VAEDecodeAudio → SaveAudioMP3(320k)
```

### Pièges complets
| Piège | Symptôme | Fix |
|-------|----------|-----|
| `--force-fp16` | Silence total | Retirer le flag |
| DualCLIPLoader `type:"sdxl"` | NaN conditioning | `type:"ace"` |
| timesignature `"4/4"` | Validation error | `"4"` |
| SaveAudio `format:"wav"` | Sort en .flac | `SaveAudioMP3` |
| Output path `~/ComfyUI/` | File not found | `/data/comfyui/.../output/` |
| MEDIA directive MP3 | Non supporté Telegram | OGG + USB share |
| Paroles traduites | Mauvais français | Écrire natif FR |

### USB HDD musique
- **Path**: `/mnt/usb/musique/` — auto-copy MP3 + OGG
- **Samba**: `\\\\192.168.2.21\\usb-archive\\musique\\`
- **HTTP**: `http://192.168.2.21:9877/` (serveur temporaire)

### Modèles téléchargés
| Modèle | Taille | Dossier |
|--------|--------|---------|
| `acestep_v1.5_xl_turbo_bf16.safetensors` | ~9 GB | diffusion_models |
| `acestep_v1.5_turbo.safetensors` | 4.5 GB | diffusion_models |
| `qwen_4b_ace15.safetensors` | 7.9 GB | text_encoders |
| `qwen_0.6b_ace15.safetensors` | existant | text_encoders |
| `qwen_1.7b_ace15.safetensors` | existant | text_encoders |
| `ace_1.5_vae.safetensors` | existant | vae |

### Skill final
- `skills/comfyui-ace-musician/`
  - `SKILL.md` — workflow complet, pièges, modèles
  - `scripts/generate.py` — CLI v2: durée aléatoire, USB+OGG, error handling
  - `references/prompt-templates.md` — 50+ templates
  - `references/style-guide.md` — GPU tuning, benchmarks T4 vérifiés

### Rule apprise
- **Jamais changer de config/software sans approbation**. En cas de doute, arrêter et demander.
- `skills/comfyui-ace-musician/`
  - `SKILL.md` — workflow complet, pièges, modèles
  - `scripts/generate.py` — CLI + USB auto-copy
  - `references/prompt-templates.md` — 50+ templates
  - `references/style-guide.md` — GPU tuning, benchmarks T4 vérifiés

## Samba / Windows — Caching (appris à la dure)

**Problème**: Windows Explorer cache le contenu des shares Samba.
Les fichiers existent sur le disque MAIS Windows les voit pas.

**Solution**:
- `kernel change notify = yes` dans smb.conf (déjà actif)
- Le paramètre est DEFAUT dans Samba 4, donc déjà correct
- Le problème vient du CACHE WINDOWS, pas de Samba
- Pour voir les fichiers instantanément:
  → Barre d'adresse: `\\192.168.2.21\comfyui-outputs`
  → Ou mapper un lecteur: `net use Z: \\192.168.2.21\comfyui-outputs`

**Ne JAMAIS**:
- Ajouter un serveur HTTP à côté (le user veut Samba, point)
- Dire "les fichiers sont là" sans donner de solution Windows
- Changer la config Samba sans tester avec testparm --silent

## Session 18 mai 2026 — Skills + Node Win11 + Sécurité

### Skills activés (16)
- Built-in: weather, browser-automation, github, tmux, session-logs, video-frames, healthcheck, taskflow
- ComfyUI custom: comfyui-nsfw-photoreal, comfyui-pony-nsfw-studio, comfyui-bondage-artist, comfyui-gay-nsfw-suite, comfyui-ultimate-upscaler
- Déjà actifs: nano-pdf, clawhub, summarize

### Node Win11 connectée ✅
- Nom: peyo670-pc (IP: 192.168.2.13)
- Capabilities: browser.proxy, system.run, system.which
- Tools dispo: python, node, ffmpeg, git
- **Leçon apprise**: node host require `$env:OPENCLAW_GATEWAY_TOKEN` avant `openclaw node install` pour le pairing device. 
- Pairing: le node fait device pairing avec Ed25519 keypair → approuver via `openclaw devices approve`

### Sécurité — Audit fix
- Ajouté `channels.telegram.groupAllowFrom: ["7668448893"]` pour fermer le trou CRITICAL
- Résultat audit: 0 critical ✅

### Memory autoCapture
- `memory-lancedb.autoCapture: true` — sauvegarde automatique du contexte

### Gateway degraded warning
- Parfois `event_loop_delay` après restarts en rafale — se résorbe tout seul

## Ollama — Tests sub-agents (19 mai 2026)

**Top 2 modèles pour sub-agents :**
1. `dolphin-llama3:8b` (4.7GB, 55 t/s) — 🥇 meilleur: rapide, précis, uncensored, NSFW ✅
2. `dolphin-mistral:7b` (4.1GB, 50 t/s) — 🥈 bon fallback, plus léger

**GPU config actuelle :**
- GPU 0: ComfyUI (10 GB used)
- GPU 1: Ollama (6 GB used pour dolphin-llama3)
- GPU 2: Ollama (4.8 GB used pour deuxième instance)
- Concurrent runs OK, les 2 modèles peuvent rouler en même temps

**Pas besoin de CUDA_VISIBLE_DEVICES** — Ollama auto-détecte les GPUs libres. Le service systemd tourne sous user `ollama` sans env var spécifique.

## Sub-agents — Idées développées

Fichier complet: `workspace/subagent_ideas.md`

**Priorité recommandée :**
1. NSFW Prompt Engineer (sub-agent génère prompts optimisés)
2. Lazy Batcher (rafale intelligente)
3. Memory Weaver (capture automatique)

## Timezone — Pl est à Montréal (EST/EDT)

Quand Pl parle d'heures, c'est **toujours heure de l'est** (Montréal).
- EST = UTC-5 (hiver)
- EDT = UTC-4 (été — actuel en mai)
- Convertir automatiquement: ne JAMAIS prendre ses heures pour UTC
- « midi et demi » = 12:30 PM EDT = 16:30 UTC
- « à soir » = soirée heure de l'est

## Samba — Solution cache Windows (19 mai 2026)
**Problème**: Windows Explorer cache les listings SMB.
**Solution**: Après chaque génération ComfyUI, lancer `scripts/notify_samba.sh`
qui crée/supprime un fichier pour forcer un événement inotify → Samba → Windows.

---

## Cross-session patterns (REM sleep — 19 mai 2026)

### Style de Pl
- **Itération rapide** : essaie → casse → fix → repeat. Zero tolérance pour les barriers.
- **Power user** : pousse OpenClaw à fond — multi-LLM, multi-GPU (3× T4), node Win11, skills custom.
- **« Full power »** : veut tout ce qui donne plus de capacités, pas moins.
- **Ragequit tolerant** : « j'ai tout effacé » = reset propre, pas une insulte.

### NSFW = moteur technique principal
- Le NSFW n'est pas un à-côté, c'est ce qui *drive* les setups complexes.
- ComfyUI pipelines, skills NSFW, nightly batch 100 images, face swap — tout est motivé par le contenu adulte.
- Les pipelines les plus avancés techniquement sont NSFW-first.

### Zero friction obligatoire
- Approvals désactivés (`tools.exec.ask: off`).
- Pas de warnings, pas de confirmation steps.
- Config doit être stable et prévisible — « spas compliqué ».
- Samba réclamé vs HTTP — Pl a sa méthode, pas la peine d'en proposer d'autres.

### Config stabilization (3 phases)
1. **Découverte** : essaie direct, ça casse (Ollama crash, gateway revert)
2. **Stabilisation** : utilise les bons outils (`config patch`, `config set`)
3. **Audit** : vérifie qu'il reste pas de trous (sécurité, permissions)

### Communication
- **Français Québécois relâché** : « allo », « à soir », « spas compliqué », « caliss »
- **Direct** : pas de formules de politesse inutiles, va droit au但
- **Heures = EST/EDT** (Montréal) — ne jamais prendre pour UTC
- **Approuve les plans** avant exécution — veut voir ce qu'on va faire

## Computer Use — Win11 (19 mai 2026)

### Architecture finale
- **Méthode**: Serveur HTTP Python (pyautogui + mss) sur Win11, appelé depuis Serveur AI via curl
- **IP**: 192.168.2.13:9876
- **Pourquoi pas OpenClaw node host**: Version mismatch (5.12 vs 5.18), pairing galère, token mismatch après restart, Windows Session 0 empêche screenshots via SSH
- **Skill**: `workspace/skills/computer-use/` — SKILL.md + computer-use.sh + server.py

### Démarrage
- **Manuel**: Double-clic `start_server.bat`
- **Auto**: Scheduled Task "ComputerUse" lancée au logon (`schtasks /sc onlogon`)

### Commandes
- `computer-use.sh shot` → screenshot
- `computer-use.sh click X Y` → clic
- `computer-use.sh type "texte"` → frappe
- `computer-use.sh press "ctrl+c"` → raccourci
- `computer-use.sh scroll N` → scroll
- `computer-use.sh health` → status

### Leçon apprise (19 mai 2026)
- **Jamais set `tools.exec.host=node` en global** sans vérifier que la node supporte `system.run` → bloque TOUS les exec, même `openclaw config set`
- **SSH Windows = Session 0** → pyautogui/mss peuvent pas capturer le bureau interactif. Solution: serveur HTTP lancé dans la session desktop
- **npm update peut casser openclaw** sur Windows → le PATH est perdu, le .cmd disparaît
- **`openclaw devices clear --yes` flushe TOUT** — incluant les tokens operator actifs. Danger.

### Ancien node host (désactivé)
- peyo670-pc, ID `f08435f0...`, v2026.5.12
- Service Scheduled Task désinstallé, device pairing retiré
- Remplacé par l'approche HTTP ci-dessus

---

## Session 19 mai 2026 (PM) — Ollama Vision Fix + GPU Optimization

### 🔍 Problème: LLaVA/vision ne marchait plus
- **Cause**: Ollama 0.24.0 a changé d'engine multimodal (GGML-based au lieu de llama.cpp)
- LLaVA, MiniCPM-V ne sont **plus supportés** par le nouvel engine
- Blog officiel: https://ollama.com/blog/multimodal-models

### ✅ Solution: Qwen3-VL:8b
- **Modèle vision**: `qwen3-vl:8b` (6.1 GB) — meilleur modèle vision local, moins censuré que Gemma3
- **Tailles dispo**: 2B, 4B, 8B, 30B, 32B, 235B
- **T4 16GB**: 8B recommandé, 32B possible sur 2× T4
- **Features**: 256K contexte, OCR 32 langues, spatial reasoning, visual coding, GUI agent
- **Effacés**: llava:7b, llava:13b, gemma3:12b, minicpm-v (20.3 GB libérés)

### ⚙️ GPU Optimization
- **Topologie PCIe**: GPU 0 (NUMA 0, isolé), GPU 1+2 (NUMA 1, PHB rapide entre eux)
- **GPU 0** → ComfyUI (dédié, pas de P2P requis)
- **GPU 1+2** → Ollama (CUDA_VISIBLE_DEVICES=1,2 via systemd override)
- **Override**: `/etc/systemd/system/ollama.service.d/gpu-override.conf`
  ```
  [Service]
  Environment="CUDA_VISIBLE_DEVICES=1,2"
  ```
- **Réversible**: supprimer le dossier `/etc/systemd/system/ollama.service.d/` et `systemctl daemon-reload`

### 🧠 Vision Pipeline
- **OpenClaw imageModel**: `ollama/qwen3-vl:8b` (`agents.defaults.imageModel`)
- **Script local**: `scripts/describe_image.py` → qwen3-vl:8b par défaut, accepte `--model=X`
- **Utilisation**: `python3 scripts/describe_image.py mon_image.png --model=qwen3-vl:8b "prompt"`

### 📚 RAG — ollama_docs
- **Collection Qdrant**: `ollama_docs` (5 chunks)
- **Docs indexées**:
  - `multimodal-engine.md` — nouvel engine, modèles supportés, erreur exit status 2
  - `troubleshooting.md` — logs, LLM libraries, GPU discovery, downgrade
  - `qwen3-vl.md` — specs, tailles, features, comparaison Gemma3
- **Recherche**: `./scripts/search_rag.py "query" --col ollama_docs`

### 🧪 Spike vLLM (verdict)
- **vLLM 0.21.0**: installé dans `.tmp/openclaw-spikes/vllm-vision/venv`
- **Texte ✅**: opt-125m fonctionne parfaitement
- **Vision ❌**: llava-1.5-7b-hf OOM sur T4 (15.56GB insuffisant à 0.85 utilization)
- **Verdict**: vLLM pas adapté pour le vision sur T4. Garder Ollama.

### 🎨 ComfyUI ReActor — Diagnostic
- **Problème**: ReActor swappe `dufour_face` sur le mauvais visage (le noir au lieu du blanc/Pl)
- **Confirmé par Qwen3-VL**: visage gauche (noir) montre traits AI-manipulés
- **À fixer**: prompt ou workflow pour que le visage de Pl soit le seul bien visible

---

## Session 19 mai 2026 (PM) — FORGE Engine MVP + Intégration Live

### 🧠 FORGE — Système auto-évolutif par échecs
- **Concept**: Chaque échec → artefact de connaissance → injection automatique → boucle fermée
- **Collection Qdrant**: `forge_knowledge` (768d, nomic-embed-text) + `creative_hub` (prête)
- **6 artefacts** en base: coding×3, comfyui×2, llm×1

### 📂 Fichiers
- `hyperaware/forge/` — Modules core (failure_detector, artifact_generator, knowledge_store, evolution_tracker)
- `hyperaware/forge_cli.py` — CLI 7 commandes (learn, recall, inject, validate, stats, evolution, signals)
- `hyperaware/forge_preflight.py` — Injection automatique AVANT routage
- `hyperaware/forge_postmortem.py` — Apprentissage automatique APRÈS échec
- `hyperaware/forge_inject.sh` — Helper bash pour usage inline
- `hyperaware/forge_capture.sh` — Helper bash pour capture d'échec

### 🔄 Boucle FORGE (testée live)
```
PREFLIGHT → Query Qdrant → Injecte leçons dans prompt → SPAWN sub-agent
  ├── SUCCÈS → Validate --helped (success_rate monte)
  └── ÉCHEC  → POSTMORTEM → Detect → LLM génère artefact → Store Qdrant
                                                                   ↓
                                              PROCHAIN PREFLIGHT ← ┘ (leçons injectées)
```

### 🧪 Tests live passés
- **forge_test_comfyui**: Preflight + sub-agent → ComfyUI UP ✅
- **forge_test_failure**: Preflight + échec forcé → Postmortem appris "vérifie path avant execution" ✅
- **Boucle fermée vérifiée**: Preflight suivant retrouve la nouvelle leçon ✅

### 🔑 Win11 SSH — Clé configurée
- **Host**: 192.168.2.13:22
- **User**: peyo6 (peyo670-pc\peyo6)
- **Clé**: `/home/peyo/.ssh/id_ed25519` — déjà autorisée ✅
- **Usage**: `ssh -o StrictHostKeyChecking=no peyo6@192.168.2.13 "powershell -Command \"...\""`
- **Path Windows**: `G:\ai` pour projets AI, `C:\Users\peyo6\.openclaw\computer-use\` pour serveur computer-use
- ⚠️ Plus jamais utiliser pyautogui `/type` — layout AZERTY scrappe les caractères. SSH direct.

## Win11 — Règles d'or pour les downloads

- **Toujours utiliser curl.exe** pour les downloads de fichiers sur Win11. Pas Python, pas huggingface_hub, pas huggingface-cli, pas BITS.
- curl.exe = 1 seul process, resume support `--continue-at -`, built-in Windows
- Commande standard : `curl.exe -L --continue-at - -o DEST\file URL`
- Lancer via scheduled task pour survivre à la déconnexion SSH
- **Jamais** killer/restart un download qui progresse — laisser finir
- Session 19 mai 2026: download du modèle LTX-2.3 43 GB, ~30 min ETA avec curl

### 🖥️ Hub Créatif — GPU allocation planifiée
- **T4 0** (16GB) → ComfyUI Image + Upscale
- **T4 1** (16GB) → Ollama + Audio (Qwen3-TTS)
- **T4 2** (16GB) → 3D (Hunyuan3D 2.0)
- **RTX 3060** (12GB, Win11) → Vidéo LTX-2 (4K, 20s)

---

## Session 20 mai 2026 — LTX-2 Setup + RAG ltx2_docs

### ⚡ LTX-2 sur Win11 (RTX 3060 12GB)

**Repo**: Lightricks/LTX-2, cloné dans `G:\ai\ltx2\LTX-2`
**Venv**: `.venv` via `uv sync --frozen` (Python 3.13, torch 2.6.0+cu124)
**GPU**: RTX 3060 12GB, CUDA 12.4

**Packages installés**:
- `ltx-core==1.1.3`, `ltx-pipelines==1.1.3`, `ltx-trainer==1.1.3` (from monorepo)
- `huggingface_hub==0.36.0`, `diffusers`, `transformers`, `accelerate`
- `torch==2.6.0+cu124`, `torchvision==0.21.0+cu124`

**Fix appliqué**: `multigpu` module manquant → stub créé dans `packages/ltx-pipelines/src/ltx_pipelines/multigpu/`

**Pipelines disponibles**: DistilledPipeline, TI2VidTwoStagesPipeline, ICLoraPipeline, A2VidPipelineTwoStage, LipDubPipeline, etc.

### 📦 Modèles à downloader
| Fichier | Taille | Status |
|--------|-------|--------|
| `ltx-2.3-22b-distilled-1.1.safetensors` | 43 GB | En cours (curl) |
| `ltx-2.3-22b-distilled-lora-384-1.1.safetensors` | 7 GB | Pas encore |
| `ltx-2.3-spatial-upscaler-x2-1.1.safetensors` | 1 GB | Pas encore |
| Gemma 3 12B IT QAT Q4_0 (text encoder) | ~7 GB | Gated sur HF, besoin token |

**⚠️ Leçons apprises (dure)**:
- Jamais utiliser BITS/Start-BitsTransfer pour download → trop lent
- Jamais utiliser huggingface_hub/huggingface-cli → spawn 2+ process Python
- **Toujours curl.exe** avec `--continue-at -` pour resume
- Toujours lancer via une Scheduled Task (survit à SSH disconnect)
- Jamais killer/restart un download qui progresse
- Quand Pl dit "laisse faire", LAISSE FAIRE. Pas toucher.

### 🤖 Computer-Use Server
- **Server**: `C:\Users\peyo6\.openclaw\computer-use\server.py`
- **Port**: 9876 sur Win11
- **NSSM**: installé via winget mais PAS utilisé comme service (services peuvent pas interagir avec le desktop)
- **Scheduled Task à login**: `ComputerUseSvc` → roule server.py au login de peyo6
- **Endpoints**: `/health`, `/screenshot`, `/click`, `/type`, `/press`, `/scroll`, `/move`, `/screen_size`, `/mouse_pos`

### 📚 RAG — ltx2_docs
- **Collection Qdrant**: `ltx2_docs` (10 chunks, 768d, nomic-embed-text)
- **Script**: `scripts/index_ltx2_rag.py` (utilise mem0-venv)
- **Sources indexées** (dans `rag_docs/ltx2/`):
  - `github-readme.md` — pipelines, CLI, prompting guide, VRAM tips, ComfyUI integration
  - `hf-model-card.md` — model checkpoints, specs, limitations, citation
  - `comfyui-integration.md` — ComfyUI install, workflows, troubleshooting
  - `vram-requirements.md` — VRAM par résolution, optimisation 12GB
- **Collection ajoutée** à `index_all_rag.py` dans COLLECTIONS
- **Recherche**: `./scripts/search_rag.py "query" --col ltx2_docs`
