#!/usr/bin/env python3
"""
ComfyUI Ultimate Upscaler - API wrapper.
Upscale images using Ultimate SD Upscale + 4x-UltraSharp.
Usage:
  python upscale_image.py --input image.png --factor 2 --output result.png
"""
import json, sys, os, time, argparse, urllib.request, uuid

API_BASE = os.environ.get("COMFYUI_API", "http://127.0.0.1:8188")
UPSCALE_MODELS = ["4x-UltraSharp.pth"]


def build_workflow(input_path, upscale_by=2.0, tile_width=512, tile_height=512,
                   tile_padding=64, denoise=0.3, steps=20, cfg=4.0,
                   ckpt_name="juggernautXL_ragnarokBy.safetensors",
                   upscale_model_name="4x-UltraSharp.pth"):
    """
    Build a proper UltimateSDUpscale workflow.
    Requires: image, model, positive, negative, vae, and sampling params.
    """
    wf = {}

    # 1. Load input image
    wf["1"] = {"class_type": "LoadImage", "inputs": {"image": input_path}}

    # 2. Load checkpoint (needed for model/vae/CLIP)
    wf["3"] = {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt_name}}

    # 3. Load upscale model
    wf["2"] = {
        "class_type": "UpscaleModelLoader",
        "inputs": {"model_name": upscale_model_name}
    }

    # 4. Empty prompts for positive/negative (upscale uses blank/textless)
    wf["4"] = {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["3", 1]}}
    wf["5"] = {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["3", 1]}}

    # 5. Ultimate SD Upscale
    wf["6"] = {
        "class_type": "UltimateSDUpscale",
        "inputs": {
            "image": ["1", 0],
            "model": ["3", 0],
            "positive": ["4", 0],
            "negative": ["5", 0],
            "vae": ["3", 2],
            "upscale_by": upscale_by,
            "seed": int(time.time() * 1000) % (2**32),
            "steps": steps,
            "cfg": cfg,
            "sampler_name": "dpmpp_2m",
            "scheduler": "karras",
            "denoise": denoise,
            "upscale_model": ["2", 0],
            "mode_type": "Linear",
            "tile_width": tile_width,
            "tile_height": tile_height,
            "mask_blur": 8,
            "tile_padding": tile_padding,
            "seam_fix_mode": "None",
            "seam_fix_denoise": 0.5,
            "seam_fix_width": 64,
            "seam_fix_mask_blur": 8,
            "seam_fix_padding": 16,
            "force_uniform_tiles": True,
            "tiled_decode": False,
            "batch_size": 1,
        }
    }

    # 6. Save
    wf["7"] = {
        "class_type": "SaveImage",
        "inputs": {"filename_prefix": "upscaled", "images": ["6", 0]}
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


def poll(prompt_id, timeout=300):
    for _ in range(timeout):
        req = urllib.request.Request(f"{API_BASE}/history/{prompt_id}")
        resp = json.loads(urllib.request.urlopen(req).read())
        if prompt_id in resp and "outputs" in resp[prompt_id]:
            return resp[prompt_id]["outputs"]
        time.sleep(1)
    raise TimeoutError(f"Timeout for {prompt_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upscale images with ComfyUI Ultimate SD Upscale")
    parser.add_argument("--input", required=True, help="Input image filename (must be in ComfyUI input/)")
    parser.add_argument("--output", default="upscaled.png")
    parser.add_argument("--factor", type=float, default=2.0, help="Upscale factor (1-4)")
    parser.add_argument("--tile", type=int, default=512, help="Tile size")
    parser.add_argument("--padding", type=int, default=64, help="Tile padding/overlap")
    parser.add_argument("--denoise", type=float, default=0.3, help="Denoise strength")
    parser.add_argument("--steps", type=int, default=20, help="Sampling steps")
    parser.add_argument("--cfg", type=float, default=4.0, help="CFG scale")
    parser.add_argument("--checkpoint", default="juggernautXL_ragnarokBy.safetensors")
    parser.add_argument("--upscale-model", default="4x-UltraSharp.pth", choices=UPSCALE_MODELS)
    args = parser.parse_args()

    wf = build_workflow(
        input_path=args.input,
        upscale_by=args.factor,
        tile_width=args.tile,
        tile_height=args.tile,
        tile_padding=args.padding,
        denoise=args.denoise,
        steps=args.steps,
        cfg=args.cfg,
        ckpt_name=args.checkpoint,
        upscale_model_name=args.upscale_model,
    )
    pid = submit(wf)
    print(f"✅ Upscale submitted: {pid}")
    outputs = poll(pid)
    print(f"✅ Done: {json.dumps(outputs, indent=2)}")
