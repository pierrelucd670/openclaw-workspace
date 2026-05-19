#!/bin/bash
# Computer Use CLI — contrôle le PC Win11 de Pl
# Usage: ./computer-use.sh <action> [args...]

WIN11="192.168.2.13:9876"
OUTDIR="$HOME/.openclaw/workspace/outputs"

screenshot() {
    local out="${1:-$OUTDIR/win11_$(date +%Y%m%d_%H%M%S).png}"
    curl -s "http://$WIN11/screenshot" | python3 -c "
import json, sys, base64
data = json.load(sys.stdin)
b64 = data['screenshot_base64']
with open('$out', 'wb') as f:
    f.write(base64.b64decode(b64))
print('MEDIA:$out')
"
}

click() { curl -s -X POST "http://$WIN11/click" -H "Content-Type: application/json" -d "{\"x\":$1,\"y\":$2,\"button\":\"${3:-left}\"}" ; echo; }
type_text() { curl -s -X POST "http://$WIN11/type" -H "Content-Type: application/json" -d "{\"text\":\"$*\"}" ; echo; }
press() { curl -s -X POST "http://$WIN11/press" -H "Content-Type: application/json" -d "{\"keys\":\"$1\"}" ; echo; }
scroll() { curl -s -X POST "http://$WIN11/scroll" -H "Content-Type: application/json" -d "{\"amount\":${1:-3}}" ; echo; }
move() { curl -s -X POST "http://$WIN11/move" -H "Content-Type: application/json" -d "{\"x\":$1,\"y\":$2}" ; echo; }
health() { curl -s "http://$WIN11/health" ; echo; }
size() { curl -s "http://$WIN11/screen_size" ; echo; }

case "${1:-}" in
    shot|screenshot) screenshot "$2" ;;
    click) click "$2" "$3" "$4" ;;
    type) shift; type_text "$@" ;;
    press) press "$2" ;;
    scroll) scroll "$2" ;;
    move) move "$2" "$3" ;;
    health) health ;;
    size) size ;;
    *) echo "Usage: $0 {shot|click X Y|type TEXT|press KEYS|scroll N|move X Y|health|size}" ;;
esac
