---
name: computer-use
description: Contrôle le bureau Windows 11 de Pl (peyo670-pc) via screenshot, clic, frappe, scroll. Utilise le serveur HTTP Python sur Win11.
---

# Computer Use — Contrôle du PC Windows 11

## Architecture

```
Serveur AI (192.168.2.21)          Win11 Pl (192.168.2.13)
┌──────────────────────┐          ┌──────────────────────────┐
│ SpicyClaw            │──HTTP──▶│ server.py (port 9876)     │
│ computer-use.sh      │          │ pyautogui + mss          │
│                      │◀──JSON──│ screenshots, clicks, type │
└──────────────────────┘          └──────────────────────────┘
```

## Endpoints

### GET
| Endpoint | Retour |
|----------|--------|
| `/health` | `{"status":"ok","host":"PEYO670-PC"}` |
| `/screenshot` | `{"screenshot_base64":"...","width":2560,"height":1440}` |
| `/screen_size` | `{"width":2560,"height":1440}` |
| `/mouse_pos` | `{"x":0,"y":0}` |

### POST (JSON body)
| Endpoint | Body | Action |
|----------|------|--------|
| `/click` | `{"x":500,"y":300,"button":"left"}` | Clic |
| `/type` | `{"text":"salut"}` | Écrire |
| `/press` | `{"keys":"ctrl+c"}` | Raccourci |
| `/scroll` | `{"amount":3,"x":500,"y":300}` | Scroll |
| `/move` | `{"x":500,"y":300}` | Bouger souris |

## Usage rapide

```bash
# Screenshot + sauvegarde
curl -s http://192.168.2.13:9876/screenshot | jq -r '.screenshot_base64' | base64 -d > shot.png

# Clic
curl -s -X POST http://192.168.2.13:9876/click -H "Content-Type: application/json" -d '{"x":500,"y":300}'

# Taper
curl -s -X POST http://192.168.2.13:9876/type -H "Content-Type: application/json" -d '{"text":"bonjour"}'
```

## Démarrage Windows

Le serveur doit rouler dans la session desktop (pas en SSH Session 0).
- Manuel: double-clic `C:\Users\peyo6\.openclaw\computer-use\start_server.bat`
- Auto: Scheduled Task "ComputerUse" lancée au login

## Fichiers

- `server.py` — Serveur HTTP sur Win11 (dans `~\.openclaw\computer-use\`)
- `computer-use.sh` — Wrapper CLI sur Serveur AI
- `start_server.bat` — Lancement Windows
