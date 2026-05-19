#!/bin/bash
# tts.sh - Synthèse vocale via Edge TTS (Microsoft)
# Usage: ./tts.sh "texte à dire" [voix] [langue]
#   voix par défaut : fr-CA-AntoineNeural (Français Québec)
#   langue par défaut : fr-CA

TEXT="${1:?Usage: tts.sh \"texte\" [voix] [langue]}"
VOICE="${2:-fr-CA-AntoineNeural}"
LANG="${3:-fr-CA}"
TIMESTAMP=$(date +%s)_$$
OUTFILE="/home/peyo/.openclaw/media/outgoing/originals/tts_${TIMESTAMP}.mp3"

source /home/peyo/tts-venv/bin/activate
edge-tts --voice "$VOICE" --text "$TEXT" --write-media "$OUTFILE" 2>/dev/null

if [ $? -ne 0 ] || [ ! -f "$OUTFILE" ]; then
    echo "Erreur edge-tts" >&2
    exit 1
fi

echo "$OUTFILE"
