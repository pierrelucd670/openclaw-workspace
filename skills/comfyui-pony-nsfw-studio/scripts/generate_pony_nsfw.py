#!/usr/bin/env python3
"""
ComfyUI Pony NSFW Studio - API wrapper.
PonyDiffusionV6XL requires: score tags, CLIP skip=2, source/rating tags.
Usage:
  python generate_pony_nsfw.py --prompt "1girl, naked, ..."
"""
import json, sys, os, time, argparse, urllib.request, uuid

API_BASE = os.environ.get("COMFYUI_API", "http://127.0.0.1:8188")
CHECKPOINTS = [
    "ponyDiffusionV6XL_v6StartWithThisOne.safetensors",
    "cyberrealisticPony_v170.safetensors",
]
PONY_VAE = "sdxl_vae.safetensors"

# Default quality prefix - THE FULL STRING is required (model trained on this exact sequence)
QUALITY_TAGS = "score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up"
RATING_EXPLICIT = "rating_explicit"
SOURCE_PONY = "source_pony"
BREAK = "BREAK"


def build_workflow(prompt, negative, ckpt_name, lora_name=None, lora_weight=0.6,
                   steps=30, cfg=5, width=1024, height=1024):
    """
    Pony workflow with CLIP skip=2 and proper score tag format.
    Negative prompt should be minimal or empty for Pony models.
    """
    wf = {}

    # 1. Load checkpoint
    wf["3"] = {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt_name}}

    # 2. CLIP Set Last Layer (CLIP skip = 2 → -2)
    wf["11"] = {
        "class_type": "CLIPSetLastLayer",
        "inputs": {"clip": ["3", 1], "stop_at_clip_layer": -2}
    }

    # 3. LoRA loader (optional)
    if lora_name:
        wf["10"] = {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": lora_name,
                "strength_model": lora_weight,
                "strength_clip": lora_weight,
                "model": ["3", 0],
                "clip": ["11", 0],  # Use CLIP with skip=2
            }
        }
        model_out = ["10", 0]
        clip_out = ["10", 1]
    else:
        model_out = ["3", 0]
        clip_out = ["11", 0]

    # 4. Build prompts with score tags
    # Quality tags MUST be at the start of the prompt
    full_prompt = f"{QUALITY_TAGS}, {RATING_EXPLICIT}, {SOURCE_PONY}, {BREAK}, {prompt}"

    # Negative: minimal - score tags don't work well in negative
    # Pony doesn't need heavy negative prompts
    full_negative = negative if negative else ""

    wf["4"] = {"class_type": "CLIPTextEncode", "inputs": {"text": full_prompt, "clip": clip_out}}
    wf["5"] = {"class_type": "CLIPTextEncode", "inputs": {"text": full_negative, "clip": clip_out}}

    # 5. Empty latent
    wf["6"] = {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}}

    # 6. KSampler - Pony works best with DPM++ 2M Karras, CFG 5-7
    wf["7"] = {
        "class_type": "KSampler",
        "inputs": {
            "seed": int(time.time() * 1000) % (2**32),
            "steps": steps,
            "cfg": cfg,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1,
            "model": model_out,
            "positive": ["4", 0],
            "negative": ["5", 0],
            "latent_image": ["6", 0],
        }
    }

    # 7. VAE Decode - use external SDXL VAE (Pony's built-in VAE can cause artifacts)
    wf["2"] = {"class_type": "VAELoader", "inputs": {"vae_name": "sdxl_vae.safetensors"}}
    wf["8"] = {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["2", 0]}}

    # 8. Save
    wf["9"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": "pony_nsfw", "images": ["8", 0]}}

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
    parser = argparse.ArgumentParser(description="Generate Pony NSFW with ComfyUI")
    parser.add_argument("--prompt", required=True,
                        help="Prompt AFTER score tags (they are auto-added)")
    parser.add_argument("--negative", default="",
                        help="Negative prompt (minimal for Pony)")
    parser.add_argument("--checkpoint", default="ponyDiffusionV6XL_v6StartWithThisOne.safetensors",
                        choices=CHECKPOINTS)
    parser.add_argument("--lora", default=None)
    parser.add_argument("--lora-weight", type=float, default=0.6)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--cfg", type=float, default=5.0)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    args = parser.parse_args()

    wf = build_workflow(args.prompt, args.negative, args.checkpoint,
                        args.lora, args.lora_weight, args.steps, args.cfg,
                        args.width, args.height)
    pid = submit(wf)
    print(f"✅ Submitted: {pid}")
    r = poll(pid)
    print(f"✅ Done: {json.dumps(r, indent=2)[:300]}")
