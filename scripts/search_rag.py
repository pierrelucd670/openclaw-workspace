#!/home/peyo/mem0-venv/bin/python3
"""
Query the RAG knowledge base.
Usage:
  ./scripts/search_rag.py "How do I configure cron jobs?" --col openclaw_docs
  ./scripts/search_rag.py "SDXL KSampler parameters" --col comfyui_docs
  ./scripts/search_rag.py "workflow nodes"  (searches all collections)
"""
import sys, requests
from qdrant_client import QdrantClient

OLLAMA = "http://127.0.0.1:11434"
QDRANT = "http://127.0.0.1:6333"
EMBED_MODEL = "nomic-embed-text:latest"
ALL_COLLECTIONS = ["openclaw_docs", "comfyui_docs"]

def search(query, collections=None, limit=3):
    if collections is None:
        collections = ALL_COLLECTIONS
    
    resp = requests.post(f"{OLLAMA}/api/embeddings", json={
        "model": EMBED_MODEL, "prompt": query
    })
    resp.raise_for_status()
    qv = resp.json()["embedding"]
    
    client = QdrantClient(url=QDRANT)
    
    all_results = []
    for col in collections:
        if not client.collection_exists(col):
            continue
        results = client.query_points(
            collection_name=col,
            query=qv,
            limit=limit
        )
        for r in results.points:
            all_results.append((r.score, col, r.payload))
    
    all_results.sort(key=lambda x: x[0], reverse=True)
    top = all_results[:limit]
    
    print(f'🔍 "{query}"')
    print(f'   Collections: {collections}\n')
    for i, (score, col, payload) in enumerate(top, 1):
        src = payload.get('source', '?')
        text = payload.get('text', '')[:400]
        print(f"  #{i}  {score:.3f}  [{col}]  {src}")
        print(f"      {text}")
        print()
    return top

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: search_rag.py <query> [--col COLLECTION] [--limit N]")
        sys.exit(1)
    
    query = sys.argv[1]
    collections = None
    limit = 3
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--col" and i+1 < len(sys.argv):
            collections = [sys.argv[i+1]]
            i += 2
        elif sys.argv[i] == "--limit" and i+1 < len(sys.argv):
            limit = int(sys.argv[i+1])
            i += 2
        else:
            i += 1
    
    search(query, collections, limit)
