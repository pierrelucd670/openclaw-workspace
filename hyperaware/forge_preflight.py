#!/home/peyo/mem0-venv/bin/python3
"""
FORGE Preflight — Injection automatique avant routage d'une tâche.

À appeler AVANT chaque sessions_spawn pour enrichir le prompt de l'agent
avec les leçons apprises des échecs précédents dans le même domaine.

Usage:
  forge_preflight.py <domain> "<task_description>"
  → Retourne le prompt original + injections FORGE

  forge_preflight.py <domain> "<task_description>" --json
  → Retourne JSON avec prompt enrichi + métadonnées

Intégration dans OpenClaw:
  INJECTION=$(./forge_preflight.py comfyui "Generate NSFW images")
  sessions_spawn(task="$INJECTION", taskName="comfyui_gen")
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from forge.knowledge_store import KnowledgeStore
from forge.evolution_tracker import EvolutionTracker


def preflight(domain: str, task: str, min_confidence: float = 0.3, 
              max_injections: int = 5, mode: str = "inject") -> dict:
    """
    Pre-flight check: query FORGE knowledge base for relevant lessons
    and inject them into the task prompt.
    
    Args:
        domain: Target domain (comfyui, coding, infra, llm, audio, video, 3d)
        task: Original task description
        min_confidence: Minimum artifact confidence to inject
        max_injections: Max number of injections
        mode: "inject" (return enriched prompt) or "query" (return raw artifacts)
    
    Returns:
        dict with enriched_prompt, artifacts_used, warnings
    """
    store = KnowledgeStore()
    
    # Phase 1: Search for relevant artifacts in this domain
    artifacts_domain = store.search(task, domain=domain, limit=max_injections, 
                                     min_confidence=min_confidence)
    # Filter out artifacts with empty context_injections
    artifacts_domain = [a for a in artifacts_domain if a.context_injection.strip()]
    
    # Phase 2: Cross-domain (only inject if highly confident AND semantically relevant)
    # Higher bar for cross-domain to avoid noise
    artifacts_cross = store.search(task, limit=5, min_confidence=0.75)
    artifacts_cross = [
        a for a in artifacts_cross 
        if a.domain != domain 
        and a.domain != "unknown"
        and a.context_injection.strip()  # Must have actual injection text
    ]
    
    all_artifacts = artifacts_domain + artifacts_cross
    
    # Deduplicate by id
    seen = set()
    unique_artifacts = []
    for a in all_artifacts:
        if a.id not in seen:
            seen.add(a.id)
            unique_artifacts.append(a)
    
    # Phase 3: Build context injection
    injections = []
    rules = []
    heuristics = []
    warnings = []
    
    for a in unique_artifacts[:max_injections]:
        if a.type == "rule":
            rules.append(a)
        elif a.type == "heuristic":
            heuristics.append(a)
        
        if a.context_injection:
            confidence_pct = int(a.confidence * 100)
            success_info = ""
            if a.times_used > 0:
                success_info = f" [validated {a.times_used}×, {int(a.success_rate*100)}% success]"
            
            injections.append(
                f"⚠️  [{a.domain}] {a.context_injection} (confiance: {confidence_pct}%{success_info})"
            )
    
    # Build warnings for high-risk patterns
    failure_domains = set()
    for a in unique_artifacts:
        if a.severity in ("critical", "high"):
            failure_domains.add(a.domain)
    
    if failure_domains:
        warnings.append(f"Domaines à risque: {', '.join(failure_domains)} — voir règles FORGE")
    
    # Phase 4: Build enriched prompt
    if injections:
        header = "╔══════════════════════════════════════════════════════════╗\n"
        header += "║  🧠 FORGE — Leçons apprises (injection automatique)    ║\n"
        header += "╚══════════════════════════════════════════════════════════╝"
        
        body = "\n".join(f"  {inj}" for inj in injections)
        
        footer = "─" * 58
        footer += "\n⚠️  Tiens compte de ces règles AVANT d'exécuter la tâche.\n"
        
        enriched = f"{header}\n\n{body}\n\n{footer}\n\n─── TÂCHE ORIGINALE ───\n{task}"
    else:
        enriched = task  # No injections, pass task as-is
    
    return {
        "enriched_prompt": enriched,
        "original_task": task,
        "domain": domain,
        "artifacts_used": [
            {
                "id": a.id,
                "type": a.type,
                "domain": a.domain,
                "injection": a.context_injection,
                "confidence": a.confidence,
                "success_rate": a.success_rate,
            }
            for a in unique_artifacts[:max_injections]
        ],
        "rules_count": len(rules),
        "heuristics_count": len(heuristics),
        "cross_domain_count": len(artifacts_cross),
        "warnings": warnings,
        "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
    }


def main():
    args = sys.argv[1:]
    json_mode = "--json" in args
    if json_mode:
        args.remove("--json")
    
    if len(args) < 2:
        print("Usage: forge_preflight.py <domain> <task_description> [--json]")
        print("  domain: comfyui | coding | infra | llm | audio | video | 3d")
        print("  --json: output JSON with metadata")
        sys.exit(1)
    
    domain = args[0]
    task = " ".join(args[1:])
    
    result = preflight(domain, task)
    
    if json_mode:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Output just the enriched prompt (for direct use in sessions_spawn)
        print(result["enriched_prompt"])


if __name__ == "__main__":
    main()
