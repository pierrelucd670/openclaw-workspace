#!/bin/bash
# Force Samba à notifier Windows - après chaque génération
DIR="/mnt/usb/outputs/comfyui"
MARKER="$DIR/.samba_refresh_$$"
touch "$MARKER" 2>/dev/null
sleep 0.3
rm -f "$MARKER" 2>/dev/null
