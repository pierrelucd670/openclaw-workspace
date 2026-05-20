#!/bin/bash
# ─── FORGE Inject ───────────────────────────────────────────
# Helper: injecte les leçons FORGE dans un prompt avant routage.
#
# Usage:
#   source hyperaware/forge_inject.sh
#   TASK=$(forge_inject comfyui "Generate NSFW images with JuggernautXL")
#   # → $TASK contient le prompt enrichi avec les leçons FORGE
#
#   # Avec un fallback si aucune injection:
#   TASK=$(forge_inject coding "Fix the import error")
#
# Intégration sessions_spawn:
#   sessions_spawn(task="$(forge_inject comfyui 'Generate images')", taskName="img_gen")
# ─────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORGE_PREFLIGHT="$SCRIPT_DIR/forge_preflight.py"
PYTHON="/home/peyo/mem0-venv/bin/python3"

forge_inject() {
    local domain="$1"
    local task="$2"
    
    if [ -z "$domain" ] || [ -z "$task" ]; then
        echo "Usage: forge_inject <domain> <task_description>" >&2
        echo "$task"  # Return task as-is on error
        return 1
    fi
    
    local result
    result=$("$PYTHON" "$FORGE_PREFLIGHT" "$domain" "$task" 2>/dev/null)
    
    if [ -n "$result" ]; then
        echo "$result"
    else
        echo "$task"  # Fallback: return original task
    fi
}

# If executed directly (not sourced), run with args
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    forge_inject "$1" "$2"
fi
