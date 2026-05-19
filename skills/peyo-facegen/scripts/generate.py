#!/usr/bin/env python3
"""
PeyeOS FaceGen - generate.py
Génère un portrait de PeyeOS avec face swap dufour_face.
Usage: python3 generate.py --prompt "description" --prefix "nom" [--seed 12345] [--cfg 6.5] [--steps 40]
"""
import json, urllib.request, time, uuid, os, sys, argparse, random

API_BASE = os.environ.get("COMFYUI_API", "http://127.0.0.1:8188")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from comfyui_gen import generate

def build_workflow(pos_prompt, neg_prompt, seed, prefix, cfg=6.5, steps=40, width=896, height=1152, sampler="dpmpp_2m", scheduler="karras"):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "juggernautXL_ragnarokBy.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": pos_prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": neg_prompt, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
            "latent_image": ["4", 0],
            "seed": seed, "steps": steps, "cfg": cfg,
            "sampler_name": sampler, "scheduler": scheduler, "denoise": 1.0
        }},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "ReActorLoadFaceModel", "inputs": {"face_model": "dufour_face.safetensors"}},
        "8": {"class_type": "ReActorFaceSwap", "inputs": {
            "enabled": True,
            "input_image": ["6", 0],
            "face_model": ["7", 0],
            "swap_model": "inswapper_128.onnx",
            "facedetection": "YOLOv5l",
            "face_restore_model": "GPEN-BFR-512.onnx",
            "face_restore_visibility": 1.0,
            "codeformer_weight": 0.5,
            "detect_gender_input": "no", "detect_gender_source": "no",
            "input_faces_index": "0", "source_faces_index": "0",
            "console_log_level": 1
        }},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}}
    }

NEGATIVE_DEFAULT = (
    "(worst quality:1.4), (low quality:1.4), (bad anatomy:1.5), (extra limbs:1.4), "
    "(mutated hands:1.4), (poorly drawn hands:1.4), (deformed body:1.3), "
    "blurry, watermark, text, logo, cartoon, anime, "
    "beard, stubble, long hair, open mouth, teeth, "
    "feminine, cropped, earring, necklace, jewelry"
)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Génère un portrait PeyeOS")
    p.add_argument("--prompt", required=True, help="Description positive")
    p.add_argument("--neg", default=NEGATIVE_DEFAULT, help="Description négative")
    p.add_argument("--prefix", default="peyo_gen", help="Préfixe fichier sortie")
    p.add_argument("--seed", type=int, default=None, help="Seed (random si omis)")
    p.add_argument("--cfg", type=float, default=6.5, help="CFG scale")
    p.add_argument("--steps", type=int, default=40, help="Steps")
    p.add_argument("--width", type=int, default=896, help="Largeur")
    p.add_argument("--height", type=int, default=1152, help="Hauteur")
    p.add_argument("--sampler", default="dpmpp_2m", help="Sampler")
    p.add_argument("--scheduler", default="karras", help="Scheduler")
    p.add_argument("--count", type=int, default=1, help="Nombre de générations")
    args = p.parse_args()
    seed = args.seed or random.randint(1000000, 9999999)
    for i in range(args.count):
        s = seed + i
        prefix = f"{args.prefix}_{s}" if args.count > 1 else args.prefix
        print(f"[{i+1}/{args.count}] seed={s} prefix={prefix}")
        wf = build_workflow(args.prompt, args.neg, s, prefix,
                          args.cfg, args.steps, args.width, args.height,
                          args.sampler, args.scheduler)
        out = generate(wf, timeout=300)
        for node_id, node_out in out.items():
            for img in node_out.get('images', []):
                print(f"  → {img['filename']}")
