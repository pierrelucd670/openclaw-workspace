#!/home/peyo/mem0-venv/bin/python3
"""
Mem0 Memory CLI — SpicyClaw Persistent Memory
Usage:
  ./memory.py recall              # Session start: auto-recall memories
  ./memory.py add <text> [--cat x] [--user pl]
  ./memory.py search <q> [--user pl] [--limit 5]
  ./memory.py list [--user pl]
  ./memory.py learn <text>        # Learn from conversation
  ./memory.py init                # Test that everything works
"""
import sys, json, os, time

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "mem0_config.yaml")

def get_memory():
    from mem0 import Memory
    try:
        import yaml
        with open(CONFIG_PATH) as f:
            cfg = yaml.safe_load(f)
    except:
        cfg = {
            "vector_store": {"provider": "qdrant", "config": {"host": "127.0.0.1", "port": 6333, "collection_name": "mem0_memory"}},
            "embedder": {"provider": "ollama", "config": {"model": "nomic-embed-text:latest", "ollama_base_url": "http://127.0.0.1:11434"}},
            "llm": {"provider": "ollama", "config": {"model": "dolphin-llama3:latest", "ollama_base_url": "http://127.0.0.1:11434", "temperature": 0.1}},
            "reranker": {"provider": "sentence_transformer", "config": {"model": "cross-encoder/ms-marco-MiniLM-L-6-v2", "device": "cuda", "max_length": 512}}
        }
    return Memory.from_config(cfg)

def parse_args(argv):
    args = {"_": []}
    i = 1
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            if "=" in a:
                k, v = a.split("=", 1)
                args[k] = v
            elif i + 1 < len(argv) and not argv[i+1].startswith("--"):
                args[a] = argv[i+1]
                i += 1
            else:
                args[a] = True
        else:
            args["_"].append(a)
        i += 1
    return args

def json_out(data):
    print(json.dumps(data, ensure_ascii=False))

def cmd_init(args):
    t0 = time.time()
    try:
        m = get_memory()
        r = m.get_all(filters={"user_id": "pl"})
        count = len(r.get("results", []))
        elapsed = time.time() - t0
        json_out({"ok": True, "memories": count, "time_s": round(elapsed, 2), "status": "Mem0 ready"})
    except Exception as e:
        json_out({"ok": False, "error": str(e)})

def cmd_recall(args):
    t0 = time.time()
    try:
        m = get_memory()
        queries = [
            "who is Pl preferences identity",
            "server hardware GPU configuration",
            "nightly NSFW image generation schedule",
            "memory system tools setup",
            "cron jobs scheduled tasks",
            "Telegram communication rules",
            "Docker containers services",
            "TTS voice settings",
        ]
        seen = set()
        results = []
        for q in queries:
            r = m.search(q, filters={"user_id": "pl"}, limit=3)
            for mem in r.get("results", []):
                mem_text = mem.get("memory", "")
                if mem_text and mem_text not in seen:
                    seen.add(mem_text)
                    results.append({
                        "memory": mem_text,
                        "score": round(mem.get("score", 0), 3),
                        "cat": mem.get("metadata", {}).get("category", "")
                    })
        # Sort by score desc
        results.sort(key=lambda x: x["score"], reverse=True)
        elapsed = time.time() - t0
        json_out({"ok": True, "count": len(results), "time_s": round(elapsed, 2), "results": results})
    except Exception as e:
        json_out({"ok": False, "error": str(e)})

def cmd_add(args):
    text = " ".join(args["_"])
    if not text:
        json_out({"ok": False, "error": "No text provided"})
        return
    user = args.get("--user", "pl")
    cat = args.get("--cat", None)
    try:
        m = get_memory()
        meta = {"category": cat} if cat else {}
        r = m.add(text, user_id=user, metadata=meta)
        mem = r["results"][0]
        json_out({"ok": True, "id": mem["id"][:8], "memory": mem["memory"]})
    except Exception as e:
        json_out({"ok": False, "error": str(e)})

def cmd_search(args):
    query = " ".join(args["_"])
    if not query:
        json_out({"ok": False, "error": "No query"})
        return
    user = args.get("--user", "pl")
    limit = min(int(args.get("--limit", 5)), 20)
    try:
        m = get_memory()
        r = m.search(query, filters={"user_id": user}, limit=limit)
        results = []
        for mem in r.get("results", []):
            results.append({
                "id": mem["id"][:8],
                "memory": mem["memory"],
                "score": round(mem.get("score", 0), 3),
                "cat": mem.get("metadata", {}).get("category", "")
            })
        json_out({"ok": True, "count": len(results), "results": results})
    except Exception as e:
        json_out({"ok": False, "error": str(e)})

def cmd_list(args):
    user = args.get("--user", "pl")
    try:
        m = get_memory()
        r = m.get_all(filters={"user_id": user})
        results = []
        for mem in r.get("results", []):
            results.append({
                "id": mem["id"][:8],
                "memory": mem["memory"],
                "cat": mem.get("metadata", {}).get("category", ""),
                "created": mem.get("created_at", "")
            })
        json_out({"ok": True, "count": len(results), "results": results})
    except Exception as e:
        json_out({"ok": False, "error": str(e)})

def cmd_learn(args):
    text = " ".join(args["_"])
    if not text:
        json_out({"ok": False, "error": "No text"})
        return
    user = args.get("--user", "pl")
    try:
        m = get_memory()
        r = m.add(text, user_id=user, metadata={"source": "conversation"})
        mem = r["results"][0]
        json_out({"ok": True, "id": mem["id"][:8], "learned": mem["memory"]})
    except Exception as e:
        json_out({"ok": False, "error": str(e)})

COMMANDS = {
    "init": cmd_init,
    "recall": cmd_recall,
    "add": cmd_add,
    "search": cmd_search,
    "list": cmd_list,
    "learn": cmd_learn,
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./memory.py {init|recall|add|search|list|learn} [...]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd in COMMANDS:
        COMMANDS[cmd](parse_args(sys.argv[1:]))
    else:
        print(f"Unknown: {cmd}")
        sys.exit(1)
