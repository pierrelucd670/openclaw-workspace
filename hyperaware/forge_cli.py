#!/home/peyo/mem0-venv/bin/python3
"""
FORGE CLI — Pipeline complet d'auto-évolution basé sur les échecs.

Usage:
  ./forge_cli.py learn "<error>" --context "<context>" [--domain <domain>] [--deep]
  ./forge_cli.py recall "<query>" [--domain <domain>] [--limit 5]
  ./forge_cli.py inject "<task_description>" [--domain <domain>]
  ./forge_cli.py stats [--domain <domain>]
  ./forge_cli.py evolution [--domain <domain>]
  ./forge_cli.py signals
  ./forge_cli.py validate <artifact_id> (--helped | --failed)

Pipeline: Error → Detect → Generate Artifact → Store → Inject in context
"""

import sys
import json
import os
from typing import Optional

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from forge.failure_detector import FailureDetector
from forge.artifact_generator import ArtifactGenerator
from forge.knowledge_store import KnowledgeStore
from forge.evolution_tracker import EvolutionTracker


class ForgeEngine:
    """Main FORGE engine orchestrating the full pipeline."""
    
    def __init__(self, use_deep: bool = False):
        self.detector = FailureDetector()
        self.generator = ArtifactGenerator()
        self.use_deep = use_deep
        self.store = KnowledgeStore()
        self.tracker = EvolutionTracker(knowledge_store=self.store)
        self._recent_failures: list = []  # In-memory cache for dedup
    
    def learn(self, error_text: str, context: str = "", domain: str = "unknown",
              source: str = "manual", session_id: str = "", use_deep: bool = False) -> dict:
        """
        Full FORGE learning pipeline:
        1. Detect and classify failure
        2. Check for duplicates
        3. Generate knowledge artifact
        4. Store in Qdrant
        5. Track evolution
        """
        # Step 1: Detect
        failure = self.detector.detect(error_text, context, source, session_id)
        
        # Override domain if specified
        if domain != "unknown":
            failure.domain = domain
        
        # Step 1b: Deep classification for unknowns
        if failure.category == "unknown":
            failure = self.detector.detect_deep(failure)
        
        # Step 2: Dedup check
        if self.detector.is_duplicate(failure, self._recent_failures):
            return {
                "status": "duplicate",
                "message": "Similar failure recently processed, skipping",
                "failure": self.detector.to_dict(failure),
            }
        
        self._recent_failures.append(failure)
        # Keep only last 50 in memory
        if len(self._recent_failures) > 50:
            self._recent_failures = self._recent_failures[-50:]
        
        # Step 3: Generate artifact
        artifact = self.generator.generate(failure, use_deep=self.use_deep or use_deep)
        
        # Step 4: Store
        stored_id = self.store.add(artifact)
        
        if stored_id:
            # Step 5: Track evolution
            self.tracker.track_creation(artifact)
        
        return {
            "status": "learned",
            "artifact_id": stored_id,
            "failure": self.detector.to_dict(failure),
            "artifact": {
                "id": artifact.id,
                "type": artifact.type,
                "domain": artifact.domain,
                "root_cause": artifact.root_cause,
                "solution": artifact.solution,
                "context_injection": artifact.context_injection,
                "confidence": artifact.confidence,
                "tags": artifact.tags,
            },
        }
    
    def recall(self, query: str, domain: Optional[str] = None, 
               limit: int = 5, min_confidence: float = 0.3) -> list[dict]:
        """
        Recall relevant knowledge artifacts for a given query/task.
        Use this before executing a task to inject learned heuristics.
        """
        artifacts = self.store.search(query, domain=domain, limit=limit, min_confidence=min_confidence)
        
        return [
            {
                "id": a.id,
                "type": a.type,
                "domain": a.domain,
                "solution": a.solution,
                "context_injection": a.context_injection,
                "confidence": a.confidence,
                "success_rate": a.success_rate,
                "times_used": a.times_used,
                "score": getattr(a, "_qdrant_score", 0),
            }
            for a in artifacts
        ]
    
    def inject(self, task_description: str, domain: Optional[str] = None) -> str:
        """
        Generate a context injection string for an upcoming task.
        Returns text to prepend to the agent's context to prevent known failures.
        """
        artifacts = self.store.search(task_description, domain=domain, limit=5, min_confidence=0.4)
        
        if not artifacts:
            return ""
        
        lines = ["\n─── FORGE KNOWLEDGE (auto-injected heuristics) ───\n"]
        
        for a in artifacts:
            if a.context_injection:
                lines.append(f"• [{a.type.upper()}] {a.context_injection} (confidence: {a.confidence:.0%})")
        
        lines.append("─── END FORGE ───\n")
        
        return "\n".join(lines)
    
    def stats(self, domain: Optional[str] = None) -> dict:
        """Get FORGE knowledge base statistics."""
        return self.store.stats()
    
    def evolution(self, domain: Optional[str] = None) -> dict:
        """Get evolution summary."""
        if domain:
            ev = self.tracker.get_domain_evolution(domain)
            return {
                "domain": ev.domain,
                "total_artifacts": ev.total_artifacts,
                "avg_confidence": ev.avg_confidence,
                "avg_success_rate": ev.avg_success_rate,
                "recent_mutations": ev.recent_mutations,
                "top_heuristics": ev.top_heuristics,
            }
        else:
            return self.tracker.get_evolution_summary()
    
    def validate(self, artifact_id: str, helped: bool) -> dict:
        """Record whether an artifact helped or not after being injected."""
        success = self.store.record_outcome(artifact_id, helped)
        
        if success:
            artifact = self.store.get(artifact_id)
            if artifact:
                self.tracker.track_outcome(artifact, helped)
        
        return {
            "status": "validated",
            "artifact_id": artifact_id,
            "helped": helped,
            "stored": success,
        }
    
    def signals(self) -> list[dict]:
        """Get Meta-Improver signals."""
        return self.tracker.detect_improvement_patterns()


# ── CLI Interface ───────────────────────────────────────────────

def parse_args():
    args = sys.argv[1:]
    if not args:
        return {"command": "help"}
    
    cmd = args[0]
    parsed = {"command": cmd}
    i = 1
    
    while i < len(args):
        a = args[i]
        if a == "--deep":
            parsed["deep"] = True
        elif a == "--helped":
            parsed["helped"] = True
        elif a == "--failed":
            parsed["helped"] = False
        elif a.startswith("--"):
            key = a[2:]
            if i + 1 < len(args) and not args[i+1].startswith("--"):
                parsed[key] = args[i+1]
                i += 1
            else:
                parsed[key] = True
        else:
            if "query" not in parsed and cmd in ("learn", "recall"):
                parsed["query"] = a
            elif "artifact_id" not in parsed and cmd == "validate":
                parsed["artifact_id"] = a
            else:
                parsed.setdefault("extra", []).append(a)
        i += 1
    
    return parsed


def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    args = parse_args()
    cmd = args.get("command", "help")
    
    use_deep = args.get("deep", False)
    engine = ForgeEngine(use_deep=use_deep)
    
    if cmd == "learn":
        error_text = args.get("query", " ".join(args.get("extra", [])))
        if not error_text:
            print("Usage: forge_cli.py learn '<error text>' [--context '<context>'] [--domain <domain>] [--deep]")
            sys.exit(1)
        
        result = engine.learn(
            error_text=error_text,
            context=args.get("context", ""),
            domain=args.get("domain", "unknown"),
            use_deep=use_deep,
        )
        print_json(result)
    
    elif cmd == "recall":
        query = args.get("query", " ".join(args.get("extra", [])))
        if not query:
            print("Usage: forge_cli.py recall '<query>' [--domain <domain>] [--limit 5]")
            sys.exit(1)
        
        results = engine.recall(
            query=query,
            domain=args.get("domain"),
            limit=int(args.get("limit", 5)),
            min_confidence=float(args.get("min_confidence", 0.3)),
        )
        print_json(results)
    
    elif cmd == "inject":
        task = args.get("query", " ".join(args.get("extra", [])))
        if not task:
            print("Usage: forge_cli.py inject '<task description>' [--domain <domain>]")
            sys.exit(1)
        
        injection = engine.inject(task, domain=args.get("domain"))
        print(injection)
    
    elif cmd == "stats":
        print_json(engine.stats(domain=args.get("domain")))
    
    elif cmd == "evolution":
        print_json(engine.evolution(domain=args.get("domain")))
    
    elif cmd == "validate":
        artifact_id = args.get("artifact_id", "")
        if not artifact_id:
            print("Usage: forge_cli.py validate <artifact_id> (--helped | --failed)")
            sys.exit(1)
        
        if "helped" not in args:
            print("Must specify --helped or --failed")
            sys.exit(1)
        
        print_json(engine.validate(artifact_id, args["helped"]))
    
    elif cmd == "signals":
        print_json(engine.signals())
    
    elif cmd in ("help", "-h", "--help"):
        print("""
FORGE CLI — Failure-Optimized Reflective Graduation and Evolution
===================================================================

  learn    <error> [--context <ctx>] [--domain <d>] [--deep]
           Analyze an error, generate a knowledge artifact, store it.
           
  recall   <query> [--domain <d>] [--limit 5]
           Search for relevant artifacts to prevent known failures.
           
  inject   <task> [--domain <d>]
           Generate context injection text to prepend to a task.
           
  stats    [--domain <d>]
           Show knowledge base statistics.
           
  evolution [--domain <d>]
           Show evolution metrics per domain.
           
  signals
           Detect Meta-Improver signals.
           
  validate <artifact_id> (--helped | --failed)
           Record whether an injected artifact helped or not.

Options:
  --deep      Use DeepSeek v4 for higher-quality artifact generation.
  --domain    Filter by domain (comfyui, coding, infra, llm, etc.)
  --limit     Number of results (default: 5)
""")
    
    else:
        print(f"Unknown command: {cmd}")
        print("Run './forge_cli.py help' for usage.")


if __name__ == "__main__":
    main()
