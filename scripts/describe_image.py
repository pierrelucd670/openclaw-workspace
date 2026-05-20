#!/usr/bin/env python3
"""Décrit une image avec Ollama LLaVA (urllib, no deps)."""
import sys, base64, json, urllib.request

def describe(image_path, model="llava:7b", prompt="Describe this image in detail."):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "images": [b64],
        "stream": False,
        "options": {"num_predict": 512, "temperature": 0.1}
    }).encode()
    
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=payload,
                                  headers={"Content-Type": "application/json"})
    data = json.loads(urllib.request.urlopen(req, timeout=120).read())
    return data.get("response", data.get("error", str(data)))

if __name__ == "__main__":
    path = sys.argv[1]
    model = "qwen3-vl:8b"
    prompt = None
    for a in sys.argv[2:]:
        if a.startswith("--model="):
            model = a.split("=",1)[1]
        else:
            prompt = a
    if not prompt:
        prompt = "Describe this image in explicit detail."
    print(f"=== {path} === (model={model})")
    print(describe(path, model=model, prompt=prompt))
