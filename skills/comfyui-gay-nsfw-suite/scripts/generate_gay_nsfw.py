#!/usr/bin/env python3
"""
ComfyUI Gay NSFW Suite - API wrapper.
3 styles: photoreal (Homofidelis), badboys (Pornworks), yaoi (Starstruck).
These are standard SDXL models - natural language prompts, good negatives needed.
Usage:
  python generate_gay_nsfw.py --prompt "..." --style photoreal
"""
import json, sys, os, time, argparse, urllib.request, uuid

API_BASE = os.environ.get("COMFYUI_API", "http://127.0.0.1:8188")
# PornWorks BadBoysPhoto: CFG 4, sampler dpmpp_2m_sde_gpu, steps 30 (officiel)
# Homofidelis: CFG 5-7 standard SDXL
# Starstruck: anime/yaoi standard
STYLES = {
    "photoreal": "homofidelisXL_v30SDXL.safetensors",
    "badboys":   "pornworksBadBoysPhoto_v06.safetensors",
    "yaoi":      "starstruckGayYaoi_v10.safetensors",
}
LORAS = {
    "gay":     "Gay_NSFW_SDXL-000001.safetensors",   # SDXL, 228MB
    "andro":   "AndroCore-1.3.safetensors",           # SDXL, 1.23GB
}

# Universal negative prompt for SDXL NSFW
DEFAULT_NEGATIVE = ("worst quality, low quality, ugly, deformed, blurry, bad anatomy, "
                    "bad hands, extra limbs, missing limbs, disfigured, "
                    "(worst quality, low quality:1.4), monochrome, zombie")


def build_workflow(prompt, negative, ckpt_name, loras_list=None,
                   steps=25, cfg=6, width=1024, height=1024, sampler="dpmpp_2m", scheduler="karras"):
    """
    Standard SDXL workflow - no special tags, good negative prompts essential.
    """
    wf = {}
    last_model = ["3", 0]
    last_clip = ["3", 1]

    # 1. Checkpoint
    wf["3"] = {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt_name}}

    # 2. LoRA chain
    if loras_list:
        node_id = 10
        for lora_name, sw, cw in loras_list:
            wf[str(node_id)] = {
                "class_type": "LoraLoader",
                "inputs": {
                    "lora_name": lora_name,
                    "strength_model": sw,
                    "strength_clip": cw,
                    "model": last_model,
                    "clip": last_clip,
                }
            }
            last_model = [str(node_id), 0]
            last_clip = [str(node_id), 1]
            node_id += 1

    # 3. Prompts
    wf["4"] = {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": last_clip}}
    # Use default negative if user didn't provide one
    neg = negative if negative else DEFAULT_NEGATIVE
    wf["5"] = {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": last_clip}}

    # 4. Latent
    wf["6"] = {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}}

    # 5. KSampler
    wf["7"] = {
        "class_type": "KSampler",
        "inputs": {
            "seed": int(time.time() * 1000) % (2**32),
            "steps": steps,
            "cfg": cfg,
            "sampler_name": sampler,
            "scheduler": scheduler,
            "denoise": 1,
            "model": last_model,
            "positive": ["4", 0],
            "negative": ["5", 0],
            "latent_image": ["6", 0],
        }
    }

    # 6. VAE Decode
    # 6. VAE Decode - use external SDXL VAE for best quality
    wf["2"] = {"class_type": "VAELoader", "inputs": {"vae_name": "sdxl_vae.safetensors"}}
    wf["8"] = {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["2", 0]}}

    # 7. Save
    wf["9"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": "gay_nsfw", "images": ["8", 0]}}

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
    parser = argparse.ArgumentParser(description="Generate Gay NSFW with ComfyUI")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--negative", default="")
    parser.add_argument("--style", default="photoreal", choices=list(STYLES.keys()))
    parser.add_argument("--lora", default="gay", choices=list(LORAS.keys()) + ["none"])
    parser.add_argument("--steps", type=int, default=25)
    parser.add_argument("--cfg", type=float, default=6.0)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--sampler", default="dpmpp_2m")
    parser.add_argument("--scheduler", default="karras")
    args = parser.parse_args()

    loras_list = []
    if args.lora != "none":
        loras_list.append((LORAS[args.lora], 0.7, 0.7))

    ckpt = STYLES[args.style]
    wf = build_workflow(args.prompt, args.negative, ckpt, loras_list,
                        args.steps, args.cfg, args.width, args.height,
                        args.sampler, args.scheduler)
    pid = submit(wf)
    print(f"✅ Submitted ({args.style}): {pid}")
    r = poll(pid)
    print(f"✅ Done: {json.dumps(r, indent=2)[:300]}")
