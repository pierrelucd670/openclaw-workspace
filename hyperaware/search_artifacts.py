#!/home/peyo/mem0-venv/bin/python3
"""
Helper script: Search FORGE artifacts from anywhere.
Wrapper around KnowledgeStore.search().

Usage:
  python3 hyperaware/search_artifacts.py "query" [--domain comfyui] [--limit 5]
  python3 hyperaware/search_artifacts.py --inject "task description"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from forge.knowledge_store import KnowledgeStore


def main():
    store = KnowledgeStore()
    
    args = sys.argv[1:]
    inject_mode = "--inject" in args
    if inject_mode:
        args.remove("--inject")
    
    domain = None
    limit = 5
    
    i = 0
    cleaned = []
    while i < len(args):
        if args[i] == "--domain" and i + 1 < len(args):
            domain = args[i + 1]
            i += 2
        elif args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        else:
            cleaned.append(args[i])
            i += 1
    
    query = " ".join(cleaned)
    if not query:
        # Show stats instead
        import json
        print(json.dumps(store.stats(), indent=2))
        return
    
    results = store.search(query, domain=domain, limit=limit)
    
    if inject_mode:
        # Output context injection format
        lines = ["\n─── FORGE KNOWLEDGE ───"]
        for a in results:
            if a.context_injection:
                lines.append(f"• [{a.type.upper()}] {a.context_injection}")
        lines.append("─── END FORGE ───\n")
        print("\n".join(lines))
    else:
        # Output JSON
        import json
        print(json.dumps([
            {
                "id": a.id,
                "type": a.type,
                "domain": a.domain,
                "solution": a.solution,
                "context_injection": a.context_injection,
                "confidence": a.confidence,
                "success_rate": a.success_rate,
                "tags": a.tags,
            }
            for a in results
        ], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
