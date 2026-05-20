#!/usr/bin/env python3
"""
ArtifactGenerator — Convertit les échecs détectés en artefacts de connaissance 
structurés via LLM (Ollama / DeepSeek).

Génère: heuristiques, règles, exemples, prompt patches.
"""

import json
import hashlib
import uuid
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional, Literal
from .failure_detector import DetectedFailure

# ── Artifact Types ──────────────────────────────────────────────
ArtifactType = Literal["heuristic", "rule", "example", "prompt_patch", "checklist"]

@dataclass
class KnowledgeArtifact:
    """Structured knowledge artifact generated from a failure."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: ArtifactType = "heuristic"
    domain: str = "unknown"
    
    # Core content
    trigger: str = ""           # Pattern that caused failure
    failure_signature: str = "" # Hash of the failure pattern
    root_cause: str = ""         # Why it failed
    solution: str = ""          # What to do instead
    context_injection: str = "" # Text to inject in next prompt/context
    
    # Metadata
    confidence: float = 0.5     # 0.0-1.0, how confident we are this will help
    severity: str = "medium"    # low, medium, high, critical
    tags: list = field(default_factory=list)
    
    # Evolution tracking
    times_used: int = 0
    times_helped: int = 0
    success_rate: float = 0.0
    parent_artifact_id: Optional[str] = None
    evolution_generation: int = 0
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_validated: Optional[str] = None
    
    # Source trace
    source_failure: Optional[dict] = None
    source_session: str = ""
    
    def text_for_embedding(self) -> str:
        """Generate text representation for vector embedding."""
        return f"{self.type} {self.domain} {self.trigger[:200]} {self.root_cause[:200]} {self.solution[:200]} {' '.join(self.tags)}"
    
    def compute_effectiveness(self) -> float:
        """Bayesian-like effectiveness score."""
        if self.times_used == 0:
            return self.confidence
        return self.times_helped / max(self.times_used, 1)


class ArtifactGenerator:
    """
    Generates structured knowledge artifacts from detected failures.
    
    Uses LLM (Ollama dolphin-llama3) by default, fallback to template-based.
    DeepSeek v4 can be used for high-severity/critical failures.
    """
    
    ARTIFACT_PROMPT = """You are a knowledge extraction system. Given a failure, generate a structured artifact that will PREVENT this failure from happening again.

FAILURE:
- Category: {category} / {subcategory}
- Domain: {domain}
- Severity: {severity}
- Error Message: {message}
- Context: {context}

Return ONLY a valid JSON object with these fields:
{{
  "type": "heuristic|rule|example|prompt_patch|checklist",
  "root_cause": "WHY this failed — be specific, under 300 chars",
  "solution": "WHAT to do instead — step by step, under 500 chars",
  "context_injection": "EXACT text to inject into next agent prompt/context to prevent this — imperative, clear, under 300 chars",
  "confidence": 0.0-1.0 number estimating how likely this solution is to work,
  "tags": ["tag1", "tag2", "tag3"]
}}

Choose type:
- "heuristic": general rule of thumb
- "rule": hard constraint / MUST DO
- "example": concrete before/after example
- "prompt_patch": exact text change to a system prompt
- "checklist": verification steps

Confidence guidelines:
- 0.9+: Clear root cause, obvious fix, tested pattern
- 0.7-0.9: Likely cause, good fix, seen before
- 0.5-0.7: Probable cause, reasonable fix
- 0.3-0.5: Speculative cause, experimental fix
- <0.3: Wild guess, needs validation"""

    def __init__(self, llm_model: str = "dolphin-llama3:latest", 
                 deep_model: str = "deepseek/deepseek-v4-pro",
                 ollama_url: str = "http://127.0.0.1:11434"):
        self.llm_model = llm_model
        self.deep_model = deep_model
        self.ollama_url = ollama_url
    
    def generate(self, failure: DetectedFailure, use_deep: bool = False) -> KnowledgeArtifact:
        """
        Generate a KnowledgeArtifact from a DetectedFailure.
        
        Args:
            failure: The detected failure
            use_deep: If True, use DeepSeek v4 for high-quality artifact generation
        """
        # Build prompt
        prompt = self.ARTIFACT_PROMPT.format(
            category=failure.category,
            subcategory=failure.subcategory,
            domain=failure.domain,
            severity=failure.severity,
            message=failure.message[:1500],
            context=failure.context[:1000],
        )
        
        # Choose model
        model = self.deep_model if use_deep else self.llm_model
        
        if model.startswith("deepseek/"):
            llm_response = self._call_deepseek(prompt)
        else:
            llm_response = self._call_ollama(prompt)
        
        return self._build_artifact(llm_response, failure)
    
    def _call_ollama(self, prompt: str) -> dict:
        """Call local Ollama model for artifact generation."""
        try:
            import requests
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.llm_model, "prompt": prompt, "stream": False, "temperature": 0.2},
                timeout=60
            )
            text = resp.json().get("response", "{}")
            # Extract JSON from response
            return self._parse_json(text)
        except Exception as e:
            return {"_error": str(e)}
    
    def _call_deepseek(self, prompt: str) -> dict:
        """
        Call DeepSeek v4 via OpenRouter for high-quality artifact generation.
        This is used for critical/high-severity failures.
        """
        try:
            import requests
            import os
            
            # Read API key from OpenClaw config or env
            api_key = os.environ.get("OPENROUTER_API_KEY", "")
            if not api_key:
                # Try to read from OpenClaw config
                config_path = os.path.expanduser("~/.openclaw/openclaw.json")
                try:
                    with open(config_path) as f:
                        config = json.load(f)
                    providers = config.get("models", {}).get("providers", {})
                    for pname, pcfg in providers.items():
                        if "openrouter" in pname.lower():
                            api_key = pcfg.get("apiKey", "")
                            break
                except:
                    pass
            
            if not api_key:
                return self._call_ollama(prompt)  # Fallback
            
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.deep_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 800,
                },
                timeout=30
            )
            text = resp.json()["choices"][0]["message"]["content"]
            return self._parse_json(text)
        except Exception as e:
            return {"_error": str(e), "_fallback": True}
    
    def _parse_json(self, text: str) -> dict:
        """Extract JSON object from LLM response text."""
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract from code blocks
        import re
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        
        # Try to find first { ... } pair
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        
        return {"_parse_error": True, "_raw": text[:500]}
    
    def _build_artifact(self, llm_response: dict, failure: DetectedFailure) -> KnowledgeArtifact:
        """Build KnowledgeArtifact from LLM response and failure data."""
        artifact = KnowledgeArtifact(
            type=llm_response.get("type", "heuristic"),
            domain=failure.domain,
            trigger=failure.message[:500],
            failure_signature=failure.signature_hash,
            root_cause=llm_response.get("root_cause", "Unknown root cause"),
            solution=llm_response.get("solution", "No solution generated"),
            context_injection=llm_response.get("context_injection", ""),
            confidence=float(llm_response.get("confidence", 0.5)),
            severity=failure.severity,
            tags=llm_response.get("tags", []),
            source_failure={
                "category": failure.category,
                "subcategory": failure.subcategory,
                "signature": failure.signature_hash,
                "timestamp": failure.timestamp,
            },
            source_session=failure.session_id,
        )
        
        # If LLM failed, use template fallback
        if "_error" in llm_response or "_parse_error" in llm_response:
            artifact = self._template_fallback(failure)
        
        # Auto-generate context_injection if LLM returned empty
        if not artifact.context_injection.strip() and artifact.solution.strip():
            artifact.context_injection = self._derive_injection(artifact)
        
        return artifact
    
    def _derive_injection(self, artifact: KnowledgeArtifact) -> str:
        """Derive a context_injection from the solution when LLM didn't provide one."""
        sol = artifact.solution[:200]
        domain = artifact.domain.upper()
        
        # Map domain to a short prefix
        prefixes = {
            "coding": "CODE",
            "comfyui": "COMFYUI",
            "llm": "LLM",
            "infra": "INFRA",
            "audio": "AUDIO",
            "video": "VIDEO",
            "3d": "3D",
            "hardware": "HW",
            "openclaw": "OC",
        }
        prefix = prefixes.get(artifact.domain, domain)
        
        # Truncate and format
        short = sol[:150]
        if len(sol) > 150:
            short = short.rsplit(" ", 1)[0] + "..."
        
        return f"⚠️ {prefix}: {short}"
    
    def _template_fallback(self, failure: DetectedFailure) -> KnowledgeArtifact:
        """Template-based artifact generation when LLM is unavailable."""
        templates = {
            "oom": KnowledgeArtifact(
                type="rule", 
                root_cause="Insufficient memory for the requested operation",
                solution="Free GPU memory by stopping other processes, reduce batch size, or use a smaller model variant",
                context_injection="⚠️ MEMORY: Before this task, ensure at least 4GB VRAM is free. Reduce batch size to 1 if needed.",
                confidence=0.8
            ),
            "not_found": KnowledgeArtifact(
                type="checklist",
                root_cause="Resource not found at expected path",
                solution="Verify file paths, check if model is downloaded, ensure correct working directory",
                context_injection="⚠️ PATHS: Verify all file paths exist before execution. Run 'ls <path>' first.",
                confidence=0.9
            ),
            "import_error": KnowledgeArtifact(
                type="rule",
                root_cause="Missing Python module/dependency",
                solution="Install the required package via pip in the correct virtual environment",
                context_injection="⚠️ DEPS: Run 'pip install <missing_module>' in the active venv before proceeding.",
                confidence=0.9
            ),
            "timeout": KnowledgeArtifact(
                type="heuristic",
                root_cause="Operation exceeded time limit",
                solution="Increase timeout, split into smaller operations, or check for deadlocks",
                context_injection="⚠️ TIMEOUT: Consider increasing timeout or splitting task into smaller chunks.",
                confidence=0.7
            ),
            "comfyui_node_error": KnowledgeArtifact(
                type="heuristic",
                root_cause="ComfyUI node configuration or model compatibility issue",
                solution="Check node inputs, ensure model files exist, verify workflow JSON structure",
                context_injection="⚠️ COMFYUI: Validate workflow JSON, verify all model paths, check node connections.",
                confidence=0.7
            ),
        }
        
        template = templates.get(failure.subcategory) or templates.get(failure.category)
        if template:
            template.domain = failure.domain
            template.trigger = failure.message[:500]
            template.failure_signature = failure.signature_hash
            template.severity = failure.severity
            template.tags = [failure.category, failure.domain]
            template.source_failure = {
                "category": failure.category,
                "subcategory": failure.subcategory,
                "signature": failure.signature_hash,
                "timestamp": failure.timestamp,
            }
            template.source_session = failure.session_id
            return template
        
        # Generic fallback
        return KnowledgeArtifact(
            type="heuristic",
            domain=failure.domain,
            trigger=failure.message[:500],
            failure_signature=failure.signature_hash,
            root_cause=f"Failure in category '{failure.category}/{failure.subcategory}'",
            solution="Investigate the error message and apply domain-specific fix",
            context_injection=f"⚠️ {failure.domain.upper()}: Previous attempt failed with '{failure.category}'. Check error details before retrying.",
            confidence=0.4,
            severity=failure.severity,
            tags=[failure.category, failure.domain],
            source_failure={
                "category": failure.category,
                "subcategory": failure.subcategory,
                "signature": failure.signature_hash,
                "timestamp": failure.timestamp,
            },
            source_session=failure.session_id,
        )


# ── CLI test ────────────────────────────────────────────────────
if __name__ == "__main__":
    from .failure_detector import FailureDetector
    
    detector = FailureDetector()
    generator = ArtifactGenerator()
    
    test_err = "CUDA out of memory. Tried to allocate 2.00 GiB. GPU 0 has a total capacity of 15.88 GiB"
    failure = detector.detect(test_err, context="ComfyUI KSampler with 40 steps", source="exec")
    
    print(f"Failure: {failure.category}/{failure.subcategory} @ {failure.domain}")
    print(f"Severity: {failure.severity}")
    print(f"Signature: {failure.signature_hash}")
    print()
    
    artifact = generator.generate(failure, use_deep=False)
    print(f"Artifact [{artifact.id}]: {artifact.type} | confidence={artifact.confidence}")
    print(f"  Root cause: {artifact.root_cause}")
    print(f"  Solution: {artifact.solution}")
    print(f"  Injection: {artifact.context_injection}")
    print(f"  Tags: {artifact.tags}")
