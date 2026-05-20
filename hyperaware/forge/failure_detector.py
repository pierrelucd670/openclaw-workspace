#!/usr/bin/env python3
"""
FailureDetector — Détecte et classifie les échecs d'exécution.
Supporte: exec logs, sub-agent outputs, ComfyUI errors, API failures.

Signature-based: pattern matching rapide sans LLM.
LLM-based: classification fine via Ollama pour cas ambigus.
"""

import re
import json
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional

# ── Failure Categories ──────────────────────────────────────────
FAILURE_CATEGORIES = {
    "exec_error": "Command failed with non-zero exit",
    "timeout": "Operation timed out",
    "oom": "Out of memory (GPU or RAM)",
    "syntax_error": "Code syntax/parse error",
    "import_error": "Missing module/dependency",
    "permission_denied": "Access/permission denied",
    "not_found": "File/model/resource not found",
    "comfyui_node_error": "ComfyUI node execution failed",
    "comfyui_quality": "ComfyUI output quality unacceptable",
    "ollama_error": "Ollama model loading/inference failed",
    "openclaw_error": "OpenClaw internal/config error",
    "network_error": "Connection/network failure",
    "disk_full": "No space left on device",
    "gpu_out_of_memory": "CUDA OOM",
    "unknown": "Unclassified failure",
}

# ── Failure Signatures (regex patterns) ─────────────────────────
FAILURE_SIGNATURES = [
    (re.compile(r"CUDA out of memory|out of memory.*GPU|RuntimeError.*OOM", re.I), "oom", "gpu_out_of_memory"),
    (re.compile(r"Killed|OOM killer|MemoryError|Cannot allocate memory", re.I), "oom", "oom"),
    (re.compile(r"No space left on device|ENOSPC", re.I), "disk_full", "disk_full"),
    (re.compile(r"Timed out|timed out after \d+|TimeoutError", re.I), "timeout", "timeout"),
    (re.compile(r"SyntaxError|Invalid syntax|unexpected EOF|EOL while scanning", re.I), "syntax_error", "syntax_error"),
    (re.compile(r"ModuleNotFoundError|ImportError|No module named", re.I), "import_error", "import_error"),
    (re.compile(r"Permission denied|EACCES|not permitted", re.I), "permission_denied", "permission_denied"),
    (re.compile(r"No such file|file not found|ENOENT|does not exist", re.I), "not_found", "not_found"),
    (re.compile(r"ComfyUI.*error|node.*failed|execution.*error|KeyError.*node", re.I), "comfyui_node_error", "comfyui_node_error"),
    (re.compile(r"ollama.*error|exit status \d+|model.*not found.*ollama", re.I), "ollama_error", "ollama_error"),
    (re.compile(r"Connection refused|Connection reset|ENETUNREACH|ECONNREFUSED", re.I), "network_error", "network_error"),
    (re.compile(r"Command failed|returned non-zero|exit code [1-9]", re.I), "exec_error", "exec_error"),
]

# ── Domain Classification ───────────────────────────────────────
DOMAIN_PATTERNS = [
    (re.compile(r"comfyui|comfy|workflow|ksampler|vae|lora|reactor|upscale", re.I), "comfyui"),
    (re.compile(r"ollama|llama|qwen|dolphin|mistral|llava", re.I), "llm"),
    (re.compile(r"openclaw|gateway|session|channel|telegram|cron|config\.patch", re.I), "openclaw"),
    (re.compile(r"docker|container|compose|qdrant|nginx|caddy", re.I), "infra"),
    (re.compile(r"python|import|syntax|module|pip|venv|package", re.I), "coding"),
    (re.compile(r"gpu|cuda|nvidia|t4|vram|torch", re.I), "hardware"),
    (re.compile(r"tts|audio|voice|speech|sound|wav|mp3", re.I), "audio"),
    (re.compile(r"video|ffmpeg|ltx|animate|frame", re.I), "video"),
    (re.compile(r"3d|mesh|obj|glb|pixal|hunyuan", re.I), "3d"),
]


@dataclass
class DetectedFailure:
    """Structured failure detected by FailureDetector."""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    category: str = "unknown"
    subcategory: str = ""
    domain: str = "unknown"
    severity: str = "medium"  # low, medium, high, critical
    message: str = ""
    context: str = ""  # surrounding context (command, prompt, etc.)
    stack_trace: str = ""
    source: str = "unknown"  # exec, subagent, api, manual
    session_id: str = ""
    signature_hash: str = ""
    
    def compute_signature(self) -> str:
        """Generate a stable hash for this failure to detect duplicates."""
        raw = f"{self.category}|{self.subcategory}|{self.domain}|{self.message[:200]}"
        self.signature_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return self.signature_hash


class FailureDetector:
    """
    Detects and classifies failures from raw error output.
    
    Two modes:
    - fast: regex signature matching (no LLM call)
    - deep: LLM classification for ambiguous cases
    """
    
    def __init__(self, llm_model: str = "dolphin-llama3:latest", ollama_url: str = "http://127.0.0.1:11434"):
        self.llm_model = llm_model
        self.ollama_url = ollama_url
    
    def detect(self, error_text: str, context: str = "", source: str = "unknown",
               session_id: str = "") -> DetectedFailure:
        """
        Analyze error output and return a structured DetectedFailure.
        Falls back to LLM for unclassified errors.
        """
        failure = DetectedFailure(
            message=error_text[:2000],
            context=context[:2000],
            source=source,
            session_id=session_id,
        )
        
        # Phase 1: Signature matching
        matched = False
        for pattern, cat, subcat in FAILURE_SIGNATURES:
            if pattern.search(error_text):
                failure.category = cat
                failure.subcategory = subcat
                matched = True
                break
        
        if not matched:
            failure.category = "unknown"
            failure.subcategory = "unknown"
        
        # Phase 2: Domain detection
        for pattern, domain in DOMAIN_PATTERNS:
            if pattern.search(error_text + " " + context):
                failure.domain = domain
                break
        
        # Phase 3: Severity heuristics
        if failure.subcategory in ("gpu_out_of_memory", "oom", "disk_full"):
            failure.severity = "critical"
        elif failure.category in ("timeout", "network_error"):
            failure.severity = "high"
        elif failure.category == "unknown":
            failure.severity = "medium"
        
        failure.compute_signature()
        return failure
    
    def detect_deep(self, failure: DetectedFailure) -> DetectedFailure:
        """
        Use LLM to refine classification for ambiguous or unclassified failures.
        Returns updated failure with LLM insights.
        """
        if failure.category != "unknown":
            return failure  # Skip LLM for classified failures
        
        prompt = f"""Analyze this failure and classify it. Return ONLY a JSON object:
{{
  "category": "one of: exec_error, timeout, oom, syntax_error, import_error, permission_denied, not_found, comfyui_error, ollama_error, openclaw_error, network_error, unknown",
  "domain": "comfyui|llm|openclaw|infra|coding|hardware|audio|video|3d|unknown",
  "severity": "low|medium|high|critical",
  "root_cause_short": "one sentence max 100 chars"
}}

Error text:
{failure.message[:1500]}

Context:
{failure.context[:500]}"""

        try:
            import requests
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.llm_model, "prompt": prompt, "stream": False, "temperature": 0.1},
                timeout=30
            )
            result = json.loads(resp.json().get("response", "{}"))
            failure.category = result.get("category", failure.category)
            failure.domain = result.get("domain", failure.domain)
            failure.severity = result.get("severity", failure.severity)
        except Exception:
            pass  # Keep original classification on LLM failure
        
        failure.compute_signature()
        return failure
    
    def is_duplicate(self, failure: DetectedFailure, recent_failures: list, 
                     window_minutes: int = 10) -> bool:
        """Check if this failure is a duplicate of a recent one."""
        cutoff = datetime.now(timezone.utc).timestamp() - (window_minutes * 60)
        for f in recent_failures:
            try:
                f_time = datetime.fromisoformat(f.timestamp).timestamp()
            except (ValueError, TypeError, AttributeError):
                continue
            if f_time < cutoff:
                continue
            if f.signature_hash == failure.signature_hash:
                return True
        return False
    
    def to_dict(self, failure: DetectedFailure) -> dict:
        """Convert failure to dictionary."""
        return asdict(failure)


# ── CLI test ────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    detector = FailureDetector()
    
    test_errors = [
        "CUDA out of memory. Tried to allocate 2.00 GiB. GPU 0 has a total capacity of 15.88 GiB",
        "RuntimeError: ComfyUI node 'KSampler' failed: KeyError 'seed'",
        "ModuleNotFoundError: No module named 'torch'",
        "Connection refused on port 8188",
        "ollama: error: exit status 2 loading model qwen3-vl",
        "Some random error I've never seen before with weird behavior in the pipeline",
    ]
    
    for err in test_errors:
        f = detector.detect(err, context="ComfyUI image generation pipeline", source="exec")
        print(f"  [{f.severity.upper()}] {f.category}/{f.subcategory} @ {f.domain}")
        print(f"    sig={f.signature_hash} msg={err[:80]}")
        print()
