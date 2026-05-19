#!/usr/bin/env python3
"""
ACE Musician v2 — generate.py
Génère de la musique via ACE-Step 1.5 XL Turbo dans ComfyUI.
Workflow vérifié live 19 mai 2026 — T4 16GB, --force-fp16 retiré.

Usage:
  python3 generate.py --caption "salsa festive, 180bpm" --lyrics paroles.txt
  python3 generate.py --caption "piano classique"  # durée aléatoire
  python3 generate.py --list-models
"""
import json, urllib.request, time, random, os, shutil, subprocess, argparse, sys

API = "http://127.0.0.1:8188"
OUTPUT = "/data/comfyui/comfyui/ComfyUI/output"
USB = "/mnt/usb/musique"

MODELS = {
    "xl-turbo": {
        "unet": "acestep_v1.5_xl_turbo_bf16.safetensors",
        "vae": "ace_1.5_vae.safetensors",
        "steps": 8, "cfg": 1.0,
        "sampler": "euler", "scheduler": "simple",
        "desc": "XL Turbo 4B — 8 steps, best quality"
    },
    "2b-turbo": {
        "unet": "acestep_v1.5_turbo.safetensors",
        "vae": "ace_1.5_vae.safetensors",
        "steps": 8, "cfg": 1.0,
        "sampler": "euler", "scheduler": "simple",
        "desc": "2B Turbo — 8 steps, fast"
    },
}

CLIP_MODELS = {
    "4b": ("qwen_0.6b_ace15.safetensors", "qwen_4b_ace15.safetensors"),
    "1.7b": ("qwen_0.6b_ace15.safetensors", "qwen_1.7b_ace15.safetensors"),
}

def build_workflow(caption, model="xl-turbo", duration=None, bpm=120,
                   key_sig="C major", lyrics="", prefix="ace_song",
                   language="fr", clip="4b", seed=None):
    m = MODELS.get(model, MODELS["xl-turbo"])
    if not duration:
        duration = random.randint(90, 240)
    if not seed:
        seed = random.randint(0, 2**31)
    if lyrics is None:
        lyrics = ""
    if isinstance(lyrics, str) and os.path.isfile(lyrics):
        with open(lyrics, 'r') as f:
            lyrics = f.read()

    c1, c2 = CLIP_MODELS.get(clip, CLIP_MODELS["4b"])

    tags = f"{caption}, {bpm}bpm, {key_sig}"
    if language == "fr":
        tags += ", voix francaise"

    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": m["unet"], "weight_dtype": "default"}},
        "2": {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": c1, "clip_name2": c2, "type": "ace"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": m["vae"]}},
        "4": {"class_type": "TextEncodeAceStepAudio1.5", "inputs": {
            "clip": ["2", 0], "tags": tags, "lyrics": lyrics,
            "seed": seed, "bpm": bpm, "duration": float(duration),
            "timesignature": "4", "language": language, "keyscale": key_sig,
            "generate_audio_codes": True, "cfg_scale": 2.0,
            "temperature": 0.9, "top_p": 0.95, "top_k": 0, "min_p": 0
        }},
        "5": {"class_type": "EmptyAceStep1.5LatentAudio", "inputs": {"seconds": float(duration), "batch_size": 1}},
        "6": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3.0}},
        "7": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
        "8": {"class_type": "KSampler", "inputs": {
            "model": ["6", 0], "positive": ["4", 0], "negative": ["7", 0],
            "latent_image": ["5", 0], "seed": seed, "steps": m["steps"], "cfg": float(m["cfg"]),
            "sampler_name": m["sampler"], "scheduler": m["scheduler"], "denoise": 1.0
        }},
        "9": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveAudioMP3", "inputs": {"audio": ["9", 0], "filename_prefix": prefix, "quality": "320k"}},
        "_meta": {"model": model, "duration": duration, "bpm": bpm, "key": key_sig, "seed": seed, "language": language}
    }

def check_volume(fp):
    """Return audio stats dict."""
    r = subprocess.run(["ffmpeg", "-i", fp, "-af", "volumedetect", "-f", "null", "/dev/null"],
                       capture_output=True, text=True)
    stats = {}
    for l in r.stderr.split('\n'):
        if 'Duration' in l:
            stats['duration'] = l.split('Duration:')[1].split(',')[0].strip()
        elif 'mean_volume' in l:
            stats['mean'] = l.split(':')[1].strip()
        elif 'max_volume' in l:
            stats['max'] = l.split(':')[1].strip()
    return stats

def main():
    p = argparse.ArgumentParser(description="ACE Musician v2 — Génération musicale")
    p.add_argument("--caption", "-c", help="Description musicale (genre, instruments, vibe)")
    p.add_argument("--prefix", "-p", default="ace_song", help="Préfixe du fichier de sortie")
    p.add_argument("--model", "-m", default="xl-turbo", choices=list(MODELS.keys()))
    p.add_argument("--duration", "-d", type=int, help="Durée en secondes (défaut: aléatoire 90-240)")
    p.add_argument("--bpm", type=int, default=120)
    p.add_argument("--key", dest="key_sig", default="C major")
    p.add_argument("--lyrics", "-l", help="Paroles (texte ou chemin de fichier)")
    p.add_argument("--seed", "-s", type=int)
    p.add_argument("--language", default="fr", help="Code langue (fr, en, es, zh, ja...)")
    p.add_argument("--clip", default="4b", choices=list(CLIP_MODELS.keys()))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--list-models", action="store_true")
    args = p.parse_args()

    if args.list_models:
        print("Modèles disponibles:")
        for k, m in MODELS.items():
            print(f"  {k:12s} → {m['desc']}")
            print(f"             UNET: {m['unet']}")
            print(f"             Steps: {m['steps']}, CFG: {m['cfg']}")
            print(f"             Sampler: {m['sampler']}/{m['scheduler']}")
        print(f"\nModèles CLIP:")
        for k, (c1, c2) in CLIP_MODELS.items():
            print(f"  {k}: {c1} + {c2}")
        return

    if not args.caption:
        p.error("--caption est requis pour la génération")

    workflow = build_workflow(
        caption=args.caption, model=args.model, duration=args.duration,
        bpm=args.bpm, key_sig=args.key_sig, lyrics=args.lyrics,
        prefix=args.prefix, language=args.language, clip=args.clip,
        seed=args.seed
    )
    meta = workflow.pop("_meta", {})

    if args.dry_run:
        print(json.dumps(workflow, indent=2))
        print(f"\nMeta: {json.dumps(meta, indent=2)}")
        return

    m = MODELS[args.model]
    print(f"🎵 ACE Musician — {m['desc']}")
    print(f"   {args.caption[:80]}...")
    print(f"   Durée: {meta['duration']}s | BPM: {meta['bpm']} | Key: {meta['key_sig']}")
    if args.lyrics:
        print(f"   Paroles: {meta.get('lyrics_chars', '?')} chars")
    print(f"   Seed: {meta['seed']}")

    try:
        data = json.dumps({"prompt": workflow}).encode()
        req = urllib.request.Request(f"{API}/prompt", data=data)
        resp = json.loads(urllib.request.urlopen(req).read())

        if resp.get("node_errors"):
            print(f"❌ Erreurs de validation:")
            for nid, err in resp["node_errors"].items():
                print(f"   Node {nid}: {err}")
            return

        pid = resp["prompt_id"]
        print(f"\n   ⏳ Génération en cours... (PID: {pid[:8]}...)")

        start = time.time()
        while time.time() - start < meta['duration'] + 600:
            time.sleep(5)
            h = json.loads(urllib.request.urlopen(urllib.request.Request(f"{API}/history/{pid}")).read())
            if pid not in h: continue
            s = h[pid].get("status", {})
            for msg in s.get("messages", []):
                if msg[0] == "execution_error":
                    print(f"\n❌ {msg[1].get('exception_message','?')}")
                    return
            if s.get("completed"):
                elapsed = time.time() - start
                for nid, out in h[pid].get("outputs", {}).items():
                    if "audio" in out:
                        for a in out["audio"]:
                            fn = a["filename"]
                            fp = os.path.join(OUTPUT, fn)
                            if os.path.exists(fp):
                                mb = os.path.getsize(fp) / (1024*1024)
                                stats = check_volume(fp)
                                print(f"\n✅ GÉNÉRÉ! {fn}")
                                print(f"   {mb:.1f} MB | {stats.get('duration','?')} | {elapsed:.0f}s")
                                print(f"   Volume: mean={stats.get('mean','?')}, max={stats.get('max','?')}")
                                # USB
                                os.makedirs(USB, exist_ok=True)
                                shutil.copy2(fp, os.path.join(USB, fn))
                                # OGG pour Telegram
                                ogg_fn = fn.replace('.mp3', '.ogg')
                                subprocess.run(["ffmpeg", "-y", "-i", fp, "-c:a", "libopus", "-b:a", "64k",
                                               os.path.join(USB, ogg_fn)], capture_output=True)
                                print(f"   \\\\192.168.2.21\\usb-archive\\musique\\{fn}")
                            else:
                                print(f"\n⚠️  Output listé mais fichier introuvable: {fn}")
                break
            if int(time.time() - start) % 30 == 0:
                print(f"   ... {int(time.time()-start)}s")
        else:
            print("\n❌ Timeout — la génération a pris trop de temps")

    except urllib.error.URLError:
        print(f"❌ Connexion impossible à ComfyUI ({API})")
    except Exception as e:
        print(f"❌ {e}")

if __name__ == "__main__":
    main()
