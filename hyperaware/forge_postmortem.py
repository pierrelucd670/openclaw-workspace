#!/home/peyo/mem0-venv/bin/python3
"""
FORGE Postmortem — Capture automatique après échec d'un sub-agent.

À appeler APRÈS un échec de sessions_spawn pour apprendre de l'erreur.

Usage:
  forge_postmortem.py <domain> "<error_text>" [--context "<context>"] [--session <id>] [--deep]
  → Analyse l'erreur, génère un artefact, stocke dans Qdrant

Intégration dans OpenClaw:
  Après un sub-agent failed:
    ERROR_OUTPUT=$(cat /tmp/last_error.log)
    ./forge_postmortem.py comfyui "$ERROR_OUTPUT" --context "KSampler workflow" --session "$SESSION_ID"
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from forge.failure_detector import FailureDetector
from forge.artifact_generator import ArtifactGenerator
from forge.knowledge_store import KnowledgeStore
from forge.evolution_tracker import EvolutionTracker


def postmortem(domain: str, error_text: str, context: str = "", 
               session_id: str = "", source: str = "subagent",
               use_deep: bool = False) -> dict:
    """
    Post-mortem analysis: learn from a failure and store the artifact.
    
    Args:
        domain: Domain where the failure occurred
        error_text: Raw error output
        context: What the agent was trying to do
        session_id: OpenClaw session ID for traceability
        source: Where the error came from (subagent, exec, api)
        use_deep: Use DeepSeek v4 for artifact generation
    
    Returns:
        dict with failure analysis, artifact, and next-step recommendation
    """
    detector = FailureDetector()
    generator = ArtifactGenerator()
    store = KnowledgeStore()
    tracker = EvolutionTracker(knowledge_store=store)
    
    # Step 1: Detect and classify
    failure = detector.detect(error_text, context=context, source=source, session_id=session_id)
    
    if domain and domain != "unknown":
        failure.domain = domain
    
    # Deep classification for unknown failures
    if failure.category == "unknown":
        failure = detector.detect_deep(failure)
    
    # Step 2: Check for similar existing artifacts
    existing = store.search(failure.message[:300], domain=failure.domain, limit=3, min_confidence=0.0)
    
    if existing:
        similar = existing[0]
        # If very similar artifact exists, update it instead of creating new
        if similar.failure_signature == failure.signature_hash:
            similar.times_used += 1
            store.update(similar)
            tracker.track_outcome(similar, helped=False)
            
            return {
                "status": "updated_existing",
                "artifact_id": similar.id,
                "failure": detector.to_dict(failure),
                "message": "Similar failure already recorded. Updated existing artifact.",
                "existing_confidence": similar.confidence,
            }
    
    # Step 3: Generate new artifact
    artifact = generator.generate(failure, use_deep=use_deep)
    
    # Step 4: Store
    stored_id = store.add(artifact)
    tracker.track_creation(artifact)
    
    # Step 5: Find related artifacts for cross-reference
    related = store.search(failure.message[:200], limit=3, min_confidence=0.5)
    related_ids = [a.id for a in related if a.id != artifact.id]
    
    return {
        "status": "learned",
        "artifact_id": stored_id,
        "failure": detector.to_dict(failure),
        "artifact": {
            "id": artifact.id,
            "type": artifact.type,
            "domain": artifact.domain,
            "root_cause": artifact.root_cause,
            "solution": artifact.solution,
            "context_injection": artifact.context_injection,
            "confidence": artifact.confidence,
            "severity": artifact.severity,
            "tags": artifact.tags,
        },
        "related_artifacts": related_ids,
        "suggested_action": (
            f"Next time for domain '{artifact.domain}', "
            f"preflight will inject: '{artifact.context_injection[:100]}'"
        ),
    }


def main():
    args = sys.argv[1:]
    
    if len(args) < 2:
        print("Usage: forge_postmortem.py <domain> '<error_text>' [--context '<ctx>'] [--session <id>] [--deep]")
        sys.exit(1)
    
    domain = args[0]
    error_text = args[1]
    
    context = ""
    session_id = ""
    use_deep = False
    
    i = 2
    while i < len(args):
        if args[i] == "--context" and i + 1 < len(args):
            context = args[i + 1]
            i += 2
        elif args[i] == "--session" and i + 1 < len(args):
            session_id = args[i + 1]
            i += 2
        elif args[i] == "--deep":
            use_deep = True
            i += 1
        else:
            i += 1
    
    result = postmortem(domain, error_text, context, session_id, use_deep=use_deep)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
