#!/usr/bin/env python3
"""Wrapper de génération ComfyUI avec notification Samba automatique."""
import json, urllib.request, time, uuid, os, subprocess

API_BASE = os.environ.get("COMFYUI_API", "http://127.0.0.1:8188")

def submit(workflow):
    """Soumet un workflow et retourne le prompt_id."""
    d = json.dumps({"prompt": workflow, "client_id": str(uuid.uuid4())}).encode()
    r = urllib.request.Request(f"{API_BASE}/prompt", data=d, headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(r).read())
    if "error" in resp:
        raise RuntimeError(f"ComfyUI error: {resp}")
    return resp["prompt_id"]

def poll(pid, timeout=180):
    """Attend la fin de la génération."""
    for _ in range(timeout):
        try:
            r = urllib.request.Request(f"{API_BASE}/history/{pid}")
            resp = json.loads(urllib.request.urlopen(r).read())
            if pid in resp and "outputs" in resp.get(pid, {}):
                return resp[pid]["outputs"]
        except: pass
        time.sleep(1)
    raise TimeoutError(f"Timeout {pid}")

def notify_samba():
    """Force Samba à rafraîchir - les fichiers apparaissent immédiatement sur Windows."""
    marker = f"/mnt/usb/outputs/comfyui/.samba_refresh_{os.getpid()}"
    try:
        open(marker, 'w').close()
        time.sleep(0.3)
        os.remove(marker)
    except: pass

# Usage: generate(workflow_dict)
def generate(workflow, timeout=180):
    """Génère une image ET notifie Samba après. Retourne les outputs."""
    pid = submit(workflow)
    print(f"  prompt_id={pid}")
    outputs = poll(pid, timeout)
    notify_samba()  # ← Force l'apparition instantanée sur Windows
    return outputs
