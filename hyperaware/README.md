# 🧠 Hyperaware — FORGE Engine v0.1

Système auto-évolutif qui convertit les échecs en connaissances injectables.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR (SpicyClaw)                    │
│                                                             │
│  Avant chaque tâche:                     Après chaque échec:│
│  forge_preflight.py ──→ Qdrant          error ──→ postmortem│
│  (injecte leçons)        (forge_knowledge)    (apprend)     │
└─────────────────────────────────────────────────────────────┘
```

## Boucle FORGE complète

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│ PREFLIGHT │────→│  EXÉCUTION   │────→│  POSTMORTEM  │
│ (injecte) │     │  (sub-agent) │     │  (apprend)   │
└──────────┘     └──────┬───────┘     └──────┬───────┘
       ↑                 │                    │
       │          succès │         échec      │
       │                 ↓                    ↓
       │         ┌──────────────┐    ┌──────────────┐
       └─────────│  VALIDATE    │    │ FORGE ENGINE  │
  (prochain run) │  --helped    │    │ detect→gen→   │
                 └──────────────┘    │ store→track   │
                                     └──────────────┘
```

## Utilisation rapide

```bash
# Avant une tâche: injecter les leçons
./forge_preflight.py comfyui "Generate images with JuggernautXL"

# Après un échec: apprendre
./forge_postmortem.py coding "SyntaxError: invalid syntax" --context "Fixing pipeline"

# Pipeline manuel
./forge_cli.py learn "<error>" --context "<ctx>" --domain <d>
./forge_cli.py recall "<query>" --domain <d>
./forge_cli.py inject "<task>" --domain <d>
./forge_cli.py stats
./forge_cli.py validate <id> --helped|--failed
```

## Collections Qdrant

| Collection | Usage |
|-----------|-------|
| `forge_knowledge` | Artefacts FORGE (règles, heuristiques) |
| `creative_hub` | Docs modèles créatifs (LTX-2, OmniVoice, etc.) |
| `mem0_memory` | Mémoire long-terme |
