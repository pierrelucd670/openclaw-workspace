#!/usr/bin/env python3
"""
EvolutionTracker — Suit l'évolution des artefacts de connaissance dans le temps.
Détecte les patterns d'amélioration, versionne les mutations, 
fournit des métriques pour le Meta-Improver.
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field, asdict

from .artifact_generator import KnowledgeArtifact
from .knowledge_store import KnowledgeStore


@dataclass
class EvolutionEvent:
    """An event in an artifact's evolution timeline."""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str = ""  # created, mutated, merged, deprecated, promoted, demoted
    artifact_id: str = ""
    description: str = ""
    previous_confidence: float = 0.0
    new_confidence: float = 0.0
    trigger: str = ""  # What triggered this evolution
    session_id: str = ""


@dataclass
class DomainEvolution:
    """Evolution summary for a domain."""
    domain: str = ""
    total_artifacts: int = 0
    avg_confidence: float = 0.0
    avg_success_rate: float = 0.0
    top_heuristics: list = field(default_factory=list)
    recent_mutations: int = 0
    last_evolution: Optional[str] = None


class EvolutionTracker:
    """
    Tracks artifact evolution over time.
    
    Responsibilities:
    - Log evolution events
    - Detect improvement patterns per domain
    - Compute evolution metrics
    - Signal Meta-Improver when patterns emerge
    """
    
    LOG_PATH = os.path.expanduser("~/.openclaw/workspace/hyperaware/evolution_log.jsonl")
    
    def __init__(self, knowledge_store: Optional[KnowledgeStore] = None):
        self.store = knowledge_store or KnowledgeStore()
        self._ensure_log()
    
    def _ensure_log(self):
        """Ensure evolution log file exists."""
        os.makedirs(os.path.dirname(self.LOG_PATH), exist_ok=True)
        if not os.path.exists(self.LOG_PATH):
            with open(self.LOG_PATH, "w") as f:
                f.write("")
    
    def log_event(self, event: EvolutionEvent):
        """Append an evolution event to the log."""
        with open(self.LOG_PATH, "a") as f:
            f.write(json.dumps(asdict(event)) + "\n")
    
    def get_history(self, artifact_id: str, limit: int = 20) -> list[EvolutionEvent]:
        """Get evolution history for a specific artifact."""
        events = []
        try:
            with open(self.LOG_PATH) as f:
                for line in f:
                    try:
                        evt = EvolutionEvent(**json.loads(line.strip()))
                        if evt.artifact_id == artifact_id:
                            events.append(evt)
                    except:
                        continue
        except FileNotFoundError:
            pass
        return events[-limit:]
    
    def track_creation(self, artifact: KnowledgeArtifact):
        """Log artifact creation."""
        event = EvolutionEvent(
            event_type="created",
            artifact_id=artifact.id,
            description=f"Artifact created: {artifact.type} for {artifact.domain}",
            new_confidence=artifact.confidence,
            trigger=artifact.trigger[:200],
            session_id=artifact.source_session,
        )
        self.log_event(event)
    
    def track_mutation(self, original: KnowledgeArtifact, mutated: KnowledgeArtifact, 
                       reason: str = "", session_id: str = ""):
        """Log when an artifact is mutated/improved."""
        mutated.parent_artifact_id = original.id
        mutated.evolution_generation = original.evolution_generation + 1
        
        event = EvolutionEvent(
            event_type="mutated",
            artifact_id=mutated.id,
            description=f"Artifact evolved (gen {mutated.evolution_generation}): {reason}",
            previous_confidence=original.confidence,
            new_confidence=mutated.confidence,
            trigger=reason,
            session_id=session_id,
        )
        self.log_event(event)
    
    def track_outcome(self, artifact: KnowledgeArtifact, helped: bool):
        """Log when an artifact's effectiveness is validated."""
        event_type = "promoted" if helped else "demoted"
        event = EvolutionEvent(
            event_type=event_type,
            artifact_id=artifact.id,
            description=f"Artifact {'helped' if helped else 'did not help'} (success_rate: {artifact.success_rate:.2f})",
            previous_confidence=artifact.confidence,
            new_confidence=artifact.success_rate,
        )
        self.log_event(event)
    
    def get_domain_evolution(self, domain: str) -> DomainEvolution:
        """Get evolution summary for a specific domain."""
        artifacts = self.store.get_top_performers(domain=domain, limit=50)
        
        if not artifacts:
            return DomainEvolution(domain=domain)
        
        confidences = [a.confidence for a in artifacts]
        success_rates = [a.success_rate for a in artifacts if a.times_used > 0]
        
        # Count recent mutations from log
        recent_mutations = 0
        try:
            with open(self.LOG_PATH) as f:
                lines = f.readlines()
                # Check last 1000 events
                for line in lines[-1000:]:
                    try:
                        evt = json.loads(line.strip())
                        if evt.get("event_type") == "mutated":
                            recent_mutations += 1
                    except:
                        continue
        except:
            pass
        
        top = artifacts[:5]
        
        return DomainEvolution(
            domain=domain,
            total_artifacts=len(artifacts),
            avg_confidence=sum(confidences) / len(confidences) if confidences else 0,
            avg_success_rate=sum(success_rates) / len(success_rates) if success_rates else 0,
            top_heuristics=[
                {"id": a.id, "type": a.type, "solution": a.solution[:100], "confidence": a.confidence}
                for a in top
            ],
            recent_mutations=recent_mutations,
            last_evolution=artifacts[0].last_updated if artifacts else None,
        )
    
    def detect_improvement_patterns(self) -> list[dict]:
        """
        Detect patterns in evolution that could trigger Meta-Improver.
        
        Returns list of pattern signals like:
        - Domain has >3 artifacts with similar trigger but different solutions
        - Confidence improving over time for a domain
        - Recurring failure patterns not yet captured
        """
        signals = []
        stats = self.store.stats()
        
        for domain, count in stats.get("by_domain", {}).items():
            domain_ev = self.get_domain_evolution(domain)
            
            # Signal: Domain has enough artifacts to find patterns
            if count >= 5 and domain_ev.avg_confidence < 0.6:
                signals.append({
                    "type": "low_confidence_domain",
                    "domain": domain,
                    "count": count,
                    "avg_confidence": domain_ev.avg_confidence,
                    "action": "Review artifacts, merge similar ones, prune low-confidence",
                })
            
            # Signal: Domain with many mutations may need a rule upgrade
            if domain_ev.recent_mutations > 5:
                signals.append({
                    "type": "high_mutation_domain",
                    "domain": domain,
                    "recent_mutations": domain_ev.recent_mutations,
                    "action": "Consider promoting best heuristic to a RULE",
                })
            
            # Signal: Domain evolving fast = good
            if domain_ev.avg_success_rate > 0.7 and count >= 3:
                signals.append({
                    "type": "evolving_domain",
                    "domain": domain,
                    "avg_success_rate": domain_ev.avg_success_rate,
                    "action": "This domain is healthy. Consider cross-pollinating to other domains.",
                })
        
        return signals
    
    def get_evolution_summary(self) -> dict:
        """Get full evolution summary across all domains."""
        all_signals = self.detect_improvement_patterns()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_artifacts": self.store.count(),
            "signals": all_signals,
            "top_domains": [
                {
                    "domain": d,
                    "avg_confidence": self.get_domain_evolution(d).avg_confidence,
                    "count": self.get_domain_evolution(d).total_artifacts,
                }
                for d, _ in sorted(
                    self.store.stats().get("by_domain", {}).items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            ],
        }


# ── CLI test ────────────────────────────────────────────────────
if __name__ == "__main__":
    tracker = EvolutionTracker()
    summary = tracker.get_evolution_summary()
    print(json.dumps(summary, indent=2))
