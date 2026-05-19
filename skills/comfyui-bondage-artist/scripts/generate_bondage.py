#!/usr/bin/env python3
"""
ComfyUI Bondage Artist - API wrapper.
PonyDiffusionV6XL + shibari + suspension LoRAs with proper Pony settings.
Critical: CLIP skip=2, score tags, minimal negative prompt.
Usage:
  python generate_bondage.py --prompt "1girl, shibari, rope bondage" --shibari 0.8
"""
import json, sys, os, time, argparse, urllib.request, uuid

API_BASE = os.environ.get("COMFYUI_API", "http://127.0.0.1:8188")
CHECKPOINTS = [
    "ponyDiffusionV6XL_v6StartWithThisOne.safetensors",
    "cyberrealisticPony_v170.safetensors",
    "juggernautXL_ragnarokBy.safetensors",
]

QUALITY_TAGS = "score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up"
RATING_EXPLICIT = "rating_explicit"
SOURCE_PONY = "source_pony"
BREAK = "BREAK"


def build_workflow(prompt, negative, ckpt_name, loras_list=None,
                   steps=30, cfg=5, width=1024, height=1024):
    """
    Bondage workflow: CLIP skip=2, score tags, with LoRA chain.
    """
    wf = {}
    last_model = None
    last_clip = None

    # 1. Checkpoint
    wf["3"] = {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt_name}}

    # 2. CLIP skip = 2 (required for Pony-based models)
    if "pony" in ckpt_name.lower() or "cyberrealistic" in ckpt_name.lower():
        wf["11"] = {
            "class_type": "CLIPSetLastLayer",
            "inputs": {"clip": ["3", 1], "stop_at_clip_layer": -2}
        }
        last_clip = ["11", 0]
    else:
        last_clip = ["3", 1]  # Juggenaut doesn't need CLIP skip
    last_model = ["3", 0]

    # 3. LoRA chain (supports multiple)
    if loras_list:
        node_id = 10
        for lora_name, weight in loras_list:
            wf[str(node_id)] = {
                "class_type": "LoraLoader",
                "inputs": {
                    "lora_name": lora_name,
                    "strength_model": weight,
                    "strength_clip": weight,
                    "model": last_model,
                    "clip": last_clip,
                }
            }
            last_model = [str(node_id), 0]
            last_clip = [str(node_id), 1]
            node_id += 1

    # 4. Build prompt with Pony tags if applicable
    if "pony" in ckpt_name.lower() or "cyberrealistic" in ckpt_name.lower():
        full_prompt = f"{QUALITY_TAGS}, {RATING_EXPLICIT}, {SOURCE_PONY}, {BREAK}, {prompt}"
        # Pony: minimal or empty negative
        full_negative = negative if negative else ""
    else:
        full_prompt = prompt
        full_negative = negative

    wf["4"] = {"class_type": "CLIPTextEncode", "inputs": {"text": full_prompt, "clip": last_clip}}
    wf["5"] = {"class_type": "CLIPTextEncode", "inputs": {"text": full_negative, "clip": last_clip}}

    # 5. Latent
    wf["6"] = {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}}

    # 6. KSampler
    wf["7"] = {
        "class_type": "KSampler",
        "inputs": {
            "seed": int(time.time() * 1000) % (2**32),
            "steps": steps,
            "cfg": cfg,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1,
            "model": last_model,
            "positive": ["4", 0],
            "negative": ["5", 0],
            "latent_image": ["6", 0],
        }
    }

    # 7. VAE Decode - use external SDXL VAE
    wf["2"] = {"class_type": "VAELoader", "inputs": {"vae_name": "sdxl_vae.safetensors"}}
    wf["8"] = {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["2", 0]}}

    # 8. Save
    wf["9"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": "bondage", "images": ["8", 0]}}

    return wf


def submit(workflow):
    data = json.dumps({"prompt": workflow, "client_id": str(uuid.uuid4())}).encode()
    req = urllib.request.Request(f"{API_BASE}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req).read())
    if "error" in resp:
        raise RuntimeError(f"ComfyUI error: {resp}")
    return resp["prompt_id"]


def poll(prompt_id, timeout=180):
    for _ in range(timeout):
        req = urllib.request.Request(f"{API_BASE}/history/{prompt_id}")
        resp = json.loads(urllib.request.urlopen(req).read())
        if prompt_id in resp and "outputs" in resp[prompt_id]:
            return resp[prompt_id]["outputs"]
        time.sleep(1)
    raise TimeoutError(f"Timeout for {prompt_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Bondage with ComfyUI")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--negative", default="")
    parser.add_argument("--checkpoint", default="ponyDiffusionV6XL_v6StartWithThisOne.safetensors",
                        choices=CHECKPOINTS)
    parser.add_argument("--shibari", type=float, default=0.8)
    parser.add_argument("--suspension", type=float, default=0.0)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--cfg", type=float, default=5.0)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    args = parser.parse_args()

    loras_list = []
    if args.shibari > 0:
        loras_list.append(("shibari_1990s_ZiB.safetensors", args.shibari))
    if args.suspension > 0:
        loras_list.append(("suspension_bondage_hng.safetensors", args.suspension))

    wf = build_workflow(args.prompt, args.negative, args.checkpoint,
                        loras_list, args.steps, args.cfg,
                        args.width, args.height)
    pid = submit(wf)
    print(f"✅ Submitted: {pid}")
    r = poll(pid)
    print(f"✅ Done: {json.dumps(r, indent=2)[:300]}")
