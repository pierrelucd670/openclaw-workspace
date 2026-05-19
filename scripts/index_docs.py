#!/home/peyo/mem0-venv/bin/python3
"""
Index OpenClaw docs into Qdrant — filtered, fast.
"""
import os, sys, time, json, re, hashlib
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import requests

DOCS_DIR = "/home/peyo/.npm-global/lib/node_modules/openclaw/docs"
COLLECTION = "openclaw_docs"
OLLAMA_URL = "http://127.0.0.1:11434"
EMBED_MODEL = "nomic-embed-text:latest"
QDRANT_URL = "http://127.0.0.1:6333"

# Only index these subdirs (skip assets, .i18n, announcements, ci.md, docs.json)
INCLUDE_DIRS = {"gateway", "channels", "cli", "concepts", "debug", "diagnostics",
                "automation", "clawhub"}
INCLUDE_ROOT = {"AGENTS.md", "auth-credential-semantics.md", "brave-search.md",
                "date-time.md"}
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300

# ── Qdrant ──────────────────────────────────────────────
client = QdrantClient(url=QDRANT_URL)
resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json={"model": EMBED_MODEL, "prompt": "test"})
resp.raise_for_status()
dim = len(resp.json()["embedding"])
print(f"Embedding dims: {dim}")

if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)
client.create_collection(COLLECTION, vectors_config=VectorParams(size=dim, distance=Distance.COSINE))
print(f"Collection '{COLLECTION}' ready")

# ── Gather ───────────────────────────────────────────────
print("Gathering files...")
files_data = []
total_chars = 0

for root, dirs, files in os.walk(DOCS_DIR):
    rel_root = os.path.relpath(root, DOCS_DIR)
    parts = rel_root.split(os.sep)
    # Skip excluded dirs unless root level
    if parts[0] not in INCLUDE_DIRS and rel_root != ".":
        continue
    for f in files:
        if not f.endswith('.md'):
            continue
        # At root, only include whitelisted files
        if rel_root == "." and f not in INCLUDE_ROOT:
            continue
        fpath = os.path.join(root, f)
        rel = os.path.relpath(fpath, DOCS_DIR)
        try:
            with open(fpath, 'r') as fh:
                text = fh.read()
        except:
            continue
        if not text.strip():
            continue
        total_chars += len(text)
        files_data.append((rel, fpath, text))

print(f"  {len(files_data)} files, {total_chars/1024:.0f} KB")

# ── Chunk ────────────────────────────────────────────────
def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    # Split on headings preferentially
    sections = re.split(r'\n(?=#{1,4}\s)', text)
    chunks = []
    buf = ""
    for sec in sections:
        if len(buf) + len(sec) > size and buf:
            chunks.append(buf.strip())
            buf = sec
        else:
            buf += ("\n" + sec) if buf else sec
    if buf.strip():
        chunks.append(buf.strip())
    # Split oversized
    final = []
    for c in chunks:
        if len(c) <= size * 1.5:
            final.append(c)
        else:
            for i in range(0, len(c), size - overlap):
                final.append(c[i:i + size])
    return final

all_chunks = []
for rel, fpath, text in files_data:
    chunks = chunk_text(text)
    for c in chunks:
        all_chunks.append({"text": c, "source": rel, "path": fpath})
    print(f"  {rel}: {len(chunks)} chunks")

print(f"Total: {len(all_chunks)} chunks")

# ── Embed ────────────────────────────────────────────────
print("Embedding...")
vectors = []
for i, chunk in enumerate(all_chunks):
    if i % 20 == 0:
        print(f"  {i+1}/{len(all_chunks)}...")
    # Truncate for embedding limits
    prompt = chunk["text"][:3000]
    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json={
        "model": EMBED_MODEL, "prompt": prompt
    })
    resp.raise_for_status()
    vectors.append(resp.json()["embedding"])
    time.sleep(0.02)

print(f"  done: {len(vectors)} vectors")

# ── Upload ───────────────────────────────────────────────
print("Uploading to Qdrant...")
points = []
for i, (chunk, vec) in enumerate(zip(all_chunks, vectors)):
    points.append(PointStruct(
        id=i, vector=vec,
        payload={
            "text": chunk["text"][:8000],
            "source": chunk["source"],
            "path": chunk["path"],
            "chunk_index": i,
            "chunk_hash": hashlib.md5(chunk["text"].encode()).hexdigest()
        }
    ))

for i in range(0, len(points), 50):
    client.upsert(collection_name=COLLECTION, points=points[i:i+50])
    if i % 200 == 0:
        print(f"  {min(i+50, len(points))}/{len(points)}")

print(f"\n✓ Done! {len(points)} points in '{COLLECTION}'")

# ── Verify ───────────────────────────────────────────────
count = client.count(collection_name=COLLECTION)
print(f"Count confirms: {count.count}")

# Test search
test_queries = [
    "How do I configure Telegram channel?",
    "What are cron jobs and how do I schedule them?",
    "How does memory-lancedb work?",
    "What is the Gateway configuration?",
    "How to set up skills?"
]
for q in test_queries:
    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json={"model": EMBED_MODEL, "prompt": q})
    qv = resp.json()["embedding"]
    results = client.search(collection_name=COLLECTION, query_vector=qv, limit=2)
    print(f"\n🔍 '{q}'")
    for r in results:
        print(f"  {r.score:.3f} | {r.payload['source']}")
        print(f"    {r.payload['text'][:150]}...")
