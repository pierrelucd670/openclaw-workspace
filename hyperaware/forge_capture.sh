#!/bin/bash
# ─── FORGE Capture ─────────────────────────────────────────
# Helper: capture un échec et le store dans FORGE.
#
# Usage:
#   source hyperaware/forge_capture.sh
#   forge_capture comfyui "CUDA out of memory..." "Running KSampler" "session-123"
#
#   # Ou avec le dernier code d'erreur:
#   some_command || forge_capture coding "$(cat /tmp/error.log)" "Fixing pipeline"
# ─────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORGE_POSTMORTEM="$SCRIPT_DIR/forge_postmortem.py"
PYTHON="/home/peyo/mem0-venv/bin/python3"

forge_capture() {
    local domain="$1"
    local error_text="$2"
    local context="${3:-}"
    local session_id="${4:-}"
    
    if [ -z "$domain" ] || [ -z "$error_text" ]; then
        echo "Usage: forge_capture <domain> <error_text> [context] [session_id]" >&2
        return 1
    fi
    
    local cmd=("$PYTHON" "$FORGE_POSTMORTEM" "$domain" "$error_text")
    [ -n "$context" ] && cmd+=(--context "$context")
    [ -n "$session_id" ] && cmd+=(--session "$session_id")
    
    "${cmd[@]}" 2>/dev/null
    return 0
}

# If executed directly, run with args
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    forge_capture "$1" "$2" "$3" "$4"
fi
