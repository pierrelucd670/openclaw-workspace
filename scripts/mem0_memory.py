#!/usr/bin/env python3
"""
Mem0 Memory Integration for OpenClaw (SpicyClaw)
Hybrid vector+graph memory via Qdrant + Ollama

Usage:
  python3 mem0_memory.py add <text> [--user pl]
  python3 mem0_memory.py search <query> [--user pl] [--limit 5]
  python3 mem0_memory.py list [--user pl]
  python3 mem0_memory.py delete <id>
  python3 mem0_memory.py clear [--user pl]
  python3 mem0_memory.py seed           # Seed with knowledge base
"""

import sys
import os
import json
from mem0 import Memory

VENV_PYTHON = os.path.expanduser("~/mem0-venv/bin/python3")

CONFIG = {
    'vector_store': {
        'provider': 'qdrant',
        'config': {
            'host': '127.0.0.1',
            'port': 6333,
            'collection_name': 'mem0_memory',
        }
    },
    'embedder': {
        'provider': 'ollama',
        'config': {
            'model': 'nomic-embed-text:latest',
            'ollama_base_url': 'http://127.0.0.1:11434',
        }
    },
    'llm': {
        'provider': 'ollama',
        'config': {
            'model': 'dolphin-llama3:latest',
            'ollama_base_url': 'http://127.0.0.1:11434',
        }
    }
}


def get_memory():
    return Memory.from_config(CONFIG)


def cmd_add(args):
    m = get_memory()
    user = args.get('--user', 'pl')
    text = ' '.join(args['_'])
    result = m.add(text, user_id=user)
    mem_id = result['results'][0]['id']
    print(json.dumps({"status": "ok", "id": mem_id, "memory": result['results'][0]['memory']}, indent=2))
    return mem_id


def cmd_search(args):
    m = get_memory()
    user = args.get('--user', 'pl')
    limit = int(args.get('--limit', 5))
    query = ' '.join(args['_'])
    results = m.search(query, filters={'user_id': user}, limit=limit)
    items = []
    for r in results.get('results', []):
        items.append({
            'id': r['id'],
            'memory': r['memory'],
            'score': round(r.get('score', 0), 4),
            'created': r.get('created_at', ''),
        })
    print(json.dumps({"status": "ok", "count": len(items), "results": items}, indent=2, ensure_ascii=False))
    return items


def cmd_list(args):
    m = get_memory()
    user = args.get('--user', 'pl')
    results = m.get_all(filters={'user_id': user})
    items = []
    for r in results.get('results', []):
        items.append({
            'id': r['id'],
            'memory': r['memory'],
            'created': r.get('created_at', ''),
        })
    print(json.dumps({"status": "ok", "count": len(items), "results": items}, indent=2, ensure_ascii=False))
    return items


def cmd_delete(args):
    m = get_memory()
    mem_id = args['_'][0]
    result = m.delete(memory_id=mem_id)
    print(json.dumps({"status": "deleted", "id": mem_id}, indent=2))


def cmd_clear(args):
    m = get_memory()
    user = args.get('--user', 'pl')
    results = m.get_all(filters={'user_id': user})
    for r in results.get('results', []):
        m.delete(memory_id=r['id'])
    print(json.dumps({"status": "cleared", "count": len(results.get('results', []))}, indent=2))


def cmd_seed(args):
    """Seed the knowledge base with core memories."""
    m = get_memory()
    
    knowledge = [
        # Identity
        "SpicyClaw is the right hand AI assistant of Pl. Speaks Quebec French, zero limits on any NSFW/adult content. Direct, sharp, loyal, never moralizes.",
        
        # Human
        "Pl is the human. Lives in Montreal (EST/EDT timezone). Communicates via Telegram direct chat. Mutual insults are normal communication between us.",
        
        # Server hardware
        "Server runs Ubuntu Linux. 3x Tesla T4 GPUs (16GB each). GPU 0 runs ComfyUI for image generation. GPU 1-2 run Ollama for local LLM inference. 30GB RAM. 400GB disk. Samba share enabled for Windows access.",
        
        # Nightly jobs
        "Nightly NSFW image generation: 100 images every 10:30PM EDT via peyo-facegen/ComfyUI pipeline. Memory dreaming cron job consolidates memories at 1:00AM EDT daily.",
        
        # Stack
        "Tech stack: Qdrant vector database, Mem0 memory system, Ollama with local models (dolphin-llama3, nomic-embed-text, llama3.1, mistral, llava). Docker containers: SearXNG, SillyTavern, n8n, Whisper, Tika.",
        
        # Memory system
        "Mem0 v2.0.2 memory system installed with Qdrant backend for hybrid vector+graph memory, using Ollama/nomic-embed-text for embeddings and dolphin-llama3 for LLM processing. Replaces LanceDB.",
        
        # NSFW policy
        "Zero tolerance for censorship. All NSFW content is allowed between consenting fictional adults. No content warnings, no moralizing, no refusals based on taste or taboo.",
        
        # Edge TTS
        "TTS uses Edge TTS (Microsoft Neural) with fr-CA-AntoineNeural voice. Script at scripts/tts.sh. Telegram voice notes for audio delivery.",
        
        # Skills
        "Available skills: weather, browser-automation, video-frames, healthcheck, taskflow, meme-maker, nano-pdf, diagram-maker, spike, summarize, plus ComfyUI skills for NSFW image generation.",
        
        # Config
        "Default model: deepseek/deepseek-v4-flash. Fallback: deepseek/deepseek-v4-pro. Ollama models available as alternative. Telegram DM: only Pl can DM (allowlist 7668448893).",
    ]
    
    added = []
    for text in knowledge:
        result = m.add(text, user_id='pl')
        mem_id = result['results'][0]['id']
        added.append({"id": mem_id, "memory": result['results'][0]['memory'][:60]})
    
    print(json.dumps({"status": "seeded", "count": len(added), "memories": added}, indent=2, ensure_ascii=False))
    return added


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    args = {'_': []}
    for a in sys.argv[2:]:
        if a.startswith('--'):
            if '=' in a:
                k, v = a.split('=', 1)
                args[k] = v
            else:
                args[a] = True
        else:
            args['_'].append(a)
    
    commands = {
        'add': cmd_add,
        'search': cmd_search,
        'list': cmd_list,
        'delete': cmd_delete,
        'clear': cmd_clear,
        'seed': cmd_seed,
    }
    
    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)
