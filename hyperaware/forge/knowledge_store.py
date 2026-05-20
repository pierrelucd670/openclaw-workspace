#!/usr/bin/env python3
"""
KnowledgeStore — Qdrant CRUD pour les artefacts de connaissance FORGE.

Collection: forge_knowledge (768d vectors via nomic-embed-text)
"""

import json
import uuid
import time
from datetime import datetime, timezone
from typing import Optional, Literal
from dataclasses import asdict

import requests

from .artifact_generator import KnowledgeArtifact


class KnowledgeStore:
    """
    Stores, searches, and manages FORGE knowledge artifacts in Qdrant.
    
    Uses nomic-embed-text (Ollama) for 768-dimensional embeddings.
    """
    
    QDRANT_URL = "http://127.0.0.1:6333"
    COLLECTION_NAME = "forge_knowledge"
    EMBED_MODEL = "nomic-embed-text:latest"
    OLLAMA_URL = "http://127.0.0.1:11434"
    
    def __init__(self):
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            resp = requests.get(f"{self.QDRANT_URL}/collections/{self.COLLECTION_NAME}")
            if resp.status_code == 200:
                return  # Already exists
        except:
            pass
        
        requests.put(
            f"{self.QDRANT_URL}/collections/{self.COLLECTION_NAME}",
            json={"vectors": {"size": 768, "distance": "Cosine"}}
        )
    
    def _embed(self, text: str) -> list:
        """Generate embedding vector for a text using Ollama."""
        try:
            resp = requests.post(
                f"{self.OLLAMA_URL}/api/embeddings",
                json={"model": self.EMBED_MODEL, "prompt": text[:2000]},
                timeout=15
            )
            data = resp.json()
            return data.get("embedding", [])
        except Exception as e:
            print(f"[KnowledgeStore] Embedding failed: {e}")
            # Return zero vector as fallback
            return [0.0] * 768
    
    def add(self, artifact: KnowledgeArtifact) -> str:
        """
        Store an artifact in Qdrant. Returns the point ID.
        """
        vector = self._embed(artifact.text_for_embedding())
        if not vector or len(vector) != 768:
            print("[KnowledgeStore] Invalid embedding, cannot store artifact")
            return ""
        
        payload = asdict(artifact)
        # Remove large fields from payload for storage efficiency
        payload.pop("source_failure", None)
        
        point = {
            "id": artifact.id,
            "vector": vector,
            "payload": payload,
        }
        
        try:
            resp = requests.put(
                f"{self.QDRANT_URL}/collections/{self.COLLECTION_NAME}/points",
                json={"points": [point]},
                timeout=10
            )
            if resp.status_code == 200:
                return artifact.id
            else:
                print(f"[KnowledgeStore] Failed to store: {resp.status_code} {resp.text[:200]}")
                return ""
        except Exception as e:
            print(f"[KnowledgeStore] Error storing artifact: {e}")
            return ""
    
    def get(self, artifact_id: str) -> Optional[KnowledgeArtifact]:
        """Retrieve a single artifact by ID."""
        try:
            resp = requests.post(
                f"{self.QDRANT_URL}/collections/{self.COLLECTION_NAME}/points",
                json={"ids": [artifact_id], "with_payload": True, "with_vector": False},
                timeout=10
            )
            result = resp.json().get("result", [])
            if result:
                return KnowledgeArtifact(**result[0]["payload"])
        except Exception as e:
            print(f"[KnowledgeStore] Error retrieving artifact: {e}")
        return None
    
    def update(self, artifact: KnowledgeArtifact) -> bool:
        """Update artifact metadata (success rate, times used, etc.)."""
        artifact.last_updated = datetime.now(timezone.utc).isoformat()
        
        try:
            resp = requests.post(
                f"{self.QDRANT_URL}/collections/{self.COLLECTION_NAME}/points/payload",
                json={
                    "points": [artifact.id],
                    "payload": {
                        "times_used": artifact.times_used,
                        "times_helped": artifact.times_helped,
                        "success_rate": artifact.success_rate,
                        "confidence": artifact.confidence,
                        "last_updated": artifact.last_updated,
                        "last_validated": artifact.last_validated,
                    }
                },
                timeout=10
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"[KnowledgeStore] Error updating artifact: {e}")
            return False
    
    def record_outcome(self, artifact_id: str, helped: bool) -> bool:
        """Record whether an injected artifact helped or not."""
        artifact = self.get(artifact_id)
        if not artifact:
            return False
        
        artifact.times_used += 1
        if helped:
            artifact.times_helped += 1
        artifact.success_rate = artifact.compute_effectiveness()
        artifact.last_validated = datetime.now(timezone.utc).isoformat()
        
        return self.update(artifact)
    
    def search(self, query: str, domain: Optional[str] = None, 
               limit: int = 5, min_confidence: float = 0.3) -> list[KnowledgeArtifact]:
        """
        Search for relevant artifacts by semantic similarity.
        Optionally filter by domain and minimum confidence.
        """
        vector = self._embed(query)
        if not vector or len(vector) != 768:
            return []
        
        search_body = {
            "vector": vector,
            "limit": limit * 2,  # Get more then filter
            "with_payload": True,
            "with_vector": False,
        }
        
        # Domain filter
        if domain and domain != "unknown":
            search_body["filter"] = {
                "must": [
                    {"key": "domain", "match": {"value": domain}}
                ]
            }
        
        try:
            resp = requests.post(
                f"{self.QDRANT_URL}/collections/{self.COLLECTION_NAME}/points/search",
                json=search_body,
                timeout=10
            )
            results = resp.json().get("result", [])
            
            artifacts = []
            for r in results:
                try:
                    art = KnowledgeArtifact(**r["payload"])
                    art._qdrant_score = r["score"]  # Inject score
                    if art.confidence >= min_confidence:
                        artifacts.append(art)
                except Exception:
                    continue
            
            return artifacts[:limit]
        except Exception as e:
            print(f"[KnowledgeStore] Search error: {e}")
            return []
    
    def search_by_tags(self, tags: list[str], limit: int = 10) -> list[KnowledgeArtifact]:
        """Search artifacts by tags (exact match)."""
        try:
            resp = requests.post(
                f"{self.QDRANT_URL}/collections/{self.COLLECTION_NAME}/points/scroll",
                json={
                    "limit": limit,
                    "with_payload": True,
                    "with_vector": False,
                    "filter": {
                        "must": [
                            {"key": "tags", "match": {"any": tags}}
                        ]
                    }
                },
                timeout=10
            )
            results = resp.json().get("result", {}).get("points", [])
            return [KnowledgeArtifact(**r["payload"]) for r in results]
        except Exception as e:
            print(f"[KnowledgeStore] Tag search error: {e}")
            return []
    
    def get_top_performers(self, domain: Optional[str] = None, limit: int = 10) -> list[KnowledgeArtifact]:
        """Get highest-performing artifacts (by success rate or confidence)."""
        try:
            scroll_body = {
                "limit": 100,  # Get many, sort client-side
                "with_payload": True,
                "with_vector": False,
            }
            if domain:
                scroll_body["filter"] = {
                    "must": [{"key": "domain", "match": {"value": domain}}]
                }
            
            resp = requests.post(
                f"{self.QDRANT_URL}/collections/{self.COLLECTION_NAME}/points/scroll",
                json=scroll_body,
                timeout=10
            )
            results = resp.json().get("result", {}).get("points", [])
            artifacts = [KnowledgeArtifact(**r["payload"]) for r in results]
            
            # Sort by success_rate if available, otherwise confidence
            artifacts.sort(key=lambda a: a.success_rate if a.times_used > 0 else a.confidence, reverse=True)
            return artifacts[:limit]
        except Exception as e:
            print(f"[KnowledgeStore] Top performers error: {e}")
            return []
    
    def get_evolution_chain(self, artifact_id: str) -> list[KnowledgeArtifact]:
        """Get the full evolution chain of an artifact (parent → children)."""
        chain = []
        current_id = artifact_id
        
        while current_id:
            art = self.get(current_id)
            if not art:
                break
            chain.append(art)
            current_id = art.parent_artifact_id
        
        return chain
    
    def count(self, domain: Optional[str] = None) -> int:
        """Count artifacts, optionally filtered by domain."""
        try:
            body = {"exact": True}
            if domain:
                body["filter"] = {"must": [{"key": "domain", "match": {"value": domain}}]}
            
            resp = requests.post(
                f"{self.QDRANT_URL}/collections/{self.COLLECTION_NAME}/points/count",
                json=body,
                timeout=10
            )
            return resp.json().get("result", {}).get("count", 0)
        except:
            return 0
    
    def stats(self) -> dict:
        """Get collection statistics."""
        total = self.count()
        domains = {}
        types = {}
        
        try:
            resp = requests.post(
                f"{self.QDRANT_URL}/collections/{self.COLLECTION_NAME}/points/scroll",
                json={"limit": 1000, "with_payload": True, "with_vector": False},
                timeout=10
            )
            points = resp.json().get("result", {}).get("points", [])
            
            for p in points:
                d = p["payload"].get("domain", "unknown")
                t = p["payload"].get("type", "unknown")
                domains[d] = domains.get(d, 0) + 1
                types[t] = types.get(t, 0) + 1
        except:
            pass
        
        return {
            "total_artifacts": total,
            "by_domain": domains,
            "by_type": types,
        }


# ── CLI test ────────────────────────────────────────────────────
if __name__ == "__main__":
    store = KnowledgeStore()
    print(f"Collection: {store.COLLECTION_NAME}")
    print(f"Stats: {json.dumps(store.stats(), indent=2)}")
    
    # Test search
    results = store.search("CUDA out of memory GPU", limit=3)
    print(f"\nSearch 'CUDA OOM': {len(results)} results")
    for r in results:
        print(f"  [{r.domain}] {r.type}: {r.solution[:80]}...")
