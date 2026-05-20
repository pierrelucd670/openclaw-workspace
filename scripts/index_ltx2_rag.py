"""
Index LTX-2 documentation into Qdrant.
"""
import os, sys, time, re, hashlib
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import requests

OLLAMA_URL = "http://127.0.0.1:11434"
EMBED_MODEL = "nomic-embed-text:latest"
QDRANT_URL = "http://127.0.0.1:6333"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300

client = QdrantClient(url=QDRANT_URL)

# Get embedding dims
resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json={"model": EMBED_MODEL, "prompt": "test"})
dim = len(resp.json()["embedding"])
print(f"Embedding: {EMBED_MODEL}, dims={dim}")

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
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
    final = []
    for c in chunks:
        if len(c) <= size * 1.5:
            final.append(c)
        else:
            for i in range(0, len(c), size - overlap):
                final.append(c[i:i + size])
    return final

collection_name = "ltx2_docs"
doc_dir = "/home/peyo/.openclaw/workspace/rag_docs/ltx2"

print(f"Scanning: {doc_dir}")
files_data = []
for root, dirs, files in os.walk(doc_dir):
    for f in files:
        if not f.endswith(('.md', '.txt')):
            continue
        fpath = os.path.join(root, f)
        rel = os.path.relpath(fpath, doc_dir)
        with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
            text = fh.read()
        if not text.strip():
            continue
        files_data.append((rel, fpath, text))

print(f"  {len(files_data)} files")

if not files_data:
    print("No files found. Create files in rag_docs/ltx2/ first.")
    sys.exit(1)

# Chunk
all_chunks = []
for rel, fpath, text in files_data:
    chunks = chunk_text(text)
    for c in chunks:
        all_chunks.append({"text": c, "source": rel, "path": fpath})
print(f"  {len(all_chunks)} chunks")

# Recreate collection
if client.collection_exists(collection_name):
    client.delete_collection(collection_name)
client.create_collection(collection_name, vectors_config=VectorParams(size=dim, distance=Distance.COSINE))

# Embed
print(f"  Embedding...")
vectors = []
for i, chunk in enumerate(all_chunks):
    if i % 50 == 0 and i > 0:
        print(f"    {i}/{len(all_chunks)}...")
    prompt = chunk["text"][:3000]
    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json={
        "model": EMBED_MODEL, "prompt": prompt
    })
    vectors.append(resp.json()["embedding"])
    time.sleep(0.02)

# Upload
print(f"  Uploading to Qdrant...")
points = []
for i, (chunk, vec) in enumerate(zip(all_chunks, vectors)):
    points.append(PointStruct(
        id=i, vector=vec,
        payload={
            "text": chunk["text"][:8000],
            "source": chunk["source"],
            "path": chunk["path"],
            "chunk_index": i,
        }
    ))

for i in range(0, len(points), 50):
    client.upsert(collection_name=collection_name, points=points[i:i+50])

count = client.count(collection_name=collection_name).count
print(f"\n✓ '{collection_name}': {count} points indexed")
