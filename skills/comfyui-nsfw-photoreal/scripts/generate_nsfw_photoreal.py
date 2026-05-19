#!/usr/bin/env python3
"""
ComfyUI NSFW Photoreal Generator - API wrapper.
Usage:
  python generate_nsfw_photoreal.py --prompt "1girl, naked, ..." --checkpoint juggernaut --output result.png
"""
import json, sys, os, time, argparse, urllib.request, uuid

API_BASE = os.environ.get("COMFYUI_API", "http://127.0.0.1:8188")
CHECKPOINTS = [
    "juggernautXL_ragnarokBy.safetensors",
    "epicrealismXL_pureFix.safetensors",
    "lustifySDXLNSFW_ggwpV7.safetensors",
]

def build_workflow(prompt, negative, ckpt_name, lora_name=None, lora_weight=0.8, steps=25, cfg=6):
    """Build a valid ComfyUI workflow JSON for NSFW generation."""
    wf = {}

    # 1. Load checkpoint
    wf["3"] = {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": ckpt_name}
    }

    # 2. LoRA loader (optional)
    if lora_name:
        wf["10"] = {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": lora_name,
                "strength_model": lora_weight,
                "strength_clip": lora_weight,
                "model": ["3", 0],
                "clip": ["3", 1],
            }
        }
        model_out = ["10", 0]
        clip_out = ["10", 1]
    else:
        model_out = ["3", 0]
        clip_out = ["3", 1]

    # 3. Encode prompts
    wf["4"] = {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": prompt, "clip": clip_out}
    }
    wf["5"] = {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": negative, "clip": clip_out}
    }

    # 4. Empty latent
    wf["6"] = {
        "class_type": "EmptyLatentImage",
        "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
    }

    # 5. KSampler
    wf["7"] = {
        "class_type": "KSampler",
        "inputs": {
            "seed": int(time.time() * 1000) % (2**32),
            "steps": steps,
            "cfg": cfg,
            "sampler_name": "dpmpp_2m",
            "scheduler": "karras",
            "denoise": 1,
            "model": model_out,
            "positive": ["4", 0],
            "negative": ["5", 0],
            "latent_image": ["6", 0],
        }
    }

    # 6. VAE Decode
    wf["8"] = {
        "class_type": "VAEDecode",
        "inputs": {"samples": ["7", 0], "vae": ["3", 2]}
    }

    # 7. Save
    wf["9"] = {
        "class_type": "SaveImage",
        "inputs": {"filename_prefix": "nsfw_photoreal", "images": ["8", 0]}
    }

    return wf


def submit(workflow):
    data = json.dumps({"prompt": workflow, "client_id": str(uuid.uuid4())}).encode()
    req = urllib.request.Request(f"{API_BASE}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req).read())
    if "error" in resp:
        raise RuntimeError(f"ComfyUI error: {resp}")
    return resp["prompt_id"]


def poll(prompt_id, timeout=120):
    for _ in range(timeout):
        req = urllib.request.Request(f"{API_BASE}/history/{prompt_id}")
        resp = json.loads(urllib.request.urlopen(req).read())
        if prompt_id in resp and "outputs" in resp[prompt_id]:
            return resp[prompt_id]["outputs"]
        time.sleep(1)
    raise TimeoutError(f"Generation timeout for {prompt_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate NSFW photoreal with ComfyUI")
    parser.add_argument("--prompt", required=True, help="Positive prompt")
    parser.add_argument("--negative", default="", help="Negative prompt")
    parser.add_argument("--checkpoint", default="juggernautXL_ragnarokBy.safetensors",
                        choices=CHECKPOINTS, help="Checkpoint model")
    parser.add_argument("--lora", default=None, help="LoRA filename (e.g. NSFW_master_ZIT_000008766.safetensors)")
    parser.add_argument("--lora-weight", type=float, default=0.8, help="LoRA weight")
    parser.add_argument("--steps", type=int, default=25, help="Sampling steps")
    parser.add_argument("--cfg", type=float, default=6.0, help="CFG scale")
    parser.add_argument("--output", default="output.png", help="Output filename")
    args = parser.parse_args()

    wf = build_workflow(args.prompt, args.negative, args.checkpoint,
                        args.lora, args.lora_weight, args.steps, args.cfg)
    pid = submit(wf)
    print(f"✅ Submitted (prompt_id={pid})")
    outputs = poll(pid)
    print(f"✅ Done: {json.dumps(outputs, indent=2)}")
