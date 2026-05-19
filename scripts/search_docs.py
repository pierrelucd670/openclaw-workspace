#!/home/peyo/mem0-venv/bin/python3
"""
Query the OpenClaw docs RAG.
Usage:
  ./scripts/search_docs.py "How do I configure cron jobs?"
  ./scripts/search_docs.py "telegram channel setup" --limit 5
"""
import sys, requests, json

OLLAMA = "http://127.0.0.1:11434"
QDRANT = "http://127.0.0.1:6333"
COLLECTION = "openclaw_docs"
EMBED_MODEL = "nomic-embed-text:latest"

def search(query, limit=3):
    # Embed
    resp = requests.post(f"{OLLAMA}/api/embeddings", json={
        "model": EMBED_MODEL, "prompt": query
    })
    resp.raise_for_status()
    qv = resp.json()["embedding"]

    # Search Qdrant
    from qdrant_client import QdrantClient
    client = QdrantClient(url=QDRANT)
    results = client.query_points(
        collection_name=COLLECTION,
        query=qv,
        limit=limit
    )

    print(f"🔍 \"{query}\"\n")
    for i, r in enumerate(results.points, 1):
        print(f"  #{i}  score={r.score:.3f}  source={r.payload['source']}")
        print(f"      {r.payload['text'][:500]}")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: search_docs.py <query> [--limit N]")
        sys.exit(1)

    query = sys.argv[1]
    limit = 3
    for i, arg in enumerate(sys.argv):
        if arg == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])

    search(query, limit)
