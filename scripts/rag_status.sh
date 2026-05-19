#!/bin/bash
# RAG Status — Quick health check
echo "🧠 RAG Status"
echo "============"
echo ""

# Qdrant
echo -n "Qdrant (6333): "
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "🟢 UP"
    curl -s http://localhost:6333/collections | python3 -c "
import json,sys
d=json.load(sys.stdin)
for c in d['result']['collections']:
    name=c['name']
    info=__import__('json').loads(__import__('subprocess').check_output(['curl','-s',f'http://localhost:6333/collections/{name}']))
    pts=info['result'].get('points_count',0)
    dim=info['result']['config']['params'].get('vectors',{}).get('size','?')
    print(f'  {name}: {pts} points, dim={dim}')
" 2>/dev/null
else
    echo "🔴 DOWN"
fi

# Ollama
echo -n "Ollama (11434): "
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "🟢 UP"
    curl -s http://localhost:11434/api/tags | python3 -c "
import json,sys
d=json.load(sys.stdin)
models=[m['name'] for m in d.get('models',[])]
print(f'  Models: {len(models)}')
embed='nomic-embed-text' in str(models)
print(f'  nomic-embed-text: {\"🟢\" if embed else \"🔴\"} ')
" 2>/dev/null
else
    echo "🔴 DOWN"
fi

# Venv
echo -n "mem0-venv: "
if [ -f /home/peyo/mem0-venv/bin/python3 ]; then
    echo "🟢 OK ($(/home/peyo/mem0-venv/bin/python3 --version))"
else
    echo "🔴 MISSING"
fi

# Scripts
echo "Scripts:"
for s in search_rag.py index_all_rag.py index_docs.py search_docs.py; do
    p="/home/peyo/.openclaw/workspace/scripts/$s"
    if [ -f "$p" ] && [ -x "$p" ]; then
        echo "  $s: 🟢"
    elif [ -f "$p" ]; then
        echo "  $s: 🟡 (not exec)"
    else
        echo "  $s: 🔴"
    fi
done

echo ""
echo "Collections:"
curl -s http://localhost:6333/collections | python3 -c "
import json,sys,subprocess
d=json.load(sys.stdin)
total=0
for c in d['result']['collections']:
    info=json.loads(subprocess.check_output(['curl','-s',f'http://localhost:6333/collections/{c[\"name\"]}']))
    pts=info['result'].get('points_count',0)
    total+=pts
print(f'  TOTAL points: {total} across {len(d[\"result\"][\"collections\"])} collections')
" 2>/dev/null

echo ""
echo "Ready for /new ✅"
