#!/home/peyo/mem0-venv/bin/python3
"""
Index all RAG documents into Qdrant — ComfyUI docs, OpenClaw docs, all in one.
Each source gets its own collection for clean separation.
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

# Define collections and their doc dirs
COLLECTIONS = {
    "openclaw_docs": "/home/peyo/.npm-global/lib/node_modules/openclaw/docs",
    "comfyui_docs": "/home/peyo/.openclaw/workspace/rag_docs/comfyui",
}

# Only index these openclaw subdirs
OC_INCLUDE = {"gateway", "channels", "cli", "concepts", "debug", "diagnostics", "automation", "clawhub"}
OC_ROOT_FILES = {"AGENTS.md", "auth-credential-semantics.md", "brave-search.md", "date-time.md"}

client = QdrantClient(url=QDRANT_URL)

# Get embedding dims
resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json={"model": EMBED_MODEL, "prompt": "test"})
resp.raise_for_status()
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

def index_dir(collection_name, base_dir, file_filter=None):
    print(f"\n{'='*60}")
    print(f"Indexing: {base_dir} → {collection_name}")
    print(f"{'='*60}")
    
    # Recreate collection
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
    client.create_collection(collection_name, vectors_config=VectorParams(size=dim, distance=Distance.COSINE))
    
    # Gather files
    files_data = []
    total_chars = 0
    
    for root, dirs, files in os.walk(base_dir):
        rel_root = os.path.relpath(root, base_dir)
        
        if collection_name == "openclaw_docs":
            parts = rel_root.split(os.sep)
            if parts[0] not in OC_INCLUDE and rel_root != ".":
                continue
        
        for f in files:
            if not f.endswith('.md') and not f.endswith('.txt'):
                continue
            
            if collection_name == "openclaw_docs":
                if rel_root == "." and f not in OC_ROOT_FILES:
                    continue
            
            fpath = os.path.join(root, f)
            rel = os.path.relpath(fpath, base_dir)
            
            if file_filter and not file_filter(rel):
                continue
                
            try:
                with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
                    text = fh.read()
            except:
                continue
            if not text.strip():
                continue
            total_chars += len(text)
            files_data.append((rel, fpath, text))
    
    print(f"  {len(files_data)} files, {total_chars/1024:.0f} KB")
    
    # Chunk
    all_chunks = []
    for rel, fpath, text in files_data:
        chunks = chunk_text(text)
        for c in chunks:
            all_chunks.append({"text": c, "source": rel, "path": fpath})
    print(f"  {len(all_chunks)} chunks")
    
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
        resp.raise_for_status()
        vectors.append(resp.json()["embedding"])
        time.sleep(0.02)
    
    print(f"    done: {len(vectors)} vectors")
    
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
                "chunk_hash": hashlib.md5(chunk["text"].encode()).hexdigest()
            }
        ))
    
    for i in range(0, len(points), 50):
        client.upsert(collection_name=collection_name, points=points[i:i+50])
    
    count = client.count(collection_name=collection_name).count
    print(f"  ✓ {count} points in '{collection_name}'")
    return count

# ── Run ─────────────────────────────────────────────────
totals = {}
for col_name, doc_dir in COLLECTIONS.items():
    if os.path.isdir(doc_dir):
        totals[col_name] = index_dir(col_name, doc_dir)
    else:
        print(f"\n⚠ Skipping {col_name}: dir not found: {doc_dir}")

print(f"\n{'='*60}")
print("SUMMARY")
for col, count in totals.items():
    print(f"  {col}: {count} points")
print(f"  TOTAL: {sum(totals.values())} points")
