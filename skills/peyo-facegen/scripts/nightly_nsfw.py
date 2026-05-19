# PeyeOS FaceGen — Nightly NSFW Generator
# Génère 100 images NSFW hot chaque soir dans différentes catégories
# Run: python3 /home/peyo/.openclaw/workspace/skills/peyo-facegen/scripts/nightly_nsfw.py

import sys, json, urllib.request, time, uuid, os, random, itertools
sys.path.insert(0, '/home/peyo/.openclaw/workspace/skills/scripts')
from comfyui_gen import generate, notify_samba

NEGATIVE = (
    "(worst quality:1.4), (low quality:1.4), (bad anatomy:1.5), (extra limbs:1.4), "
    "(mutated hands:1.4), (poorly drawn hands:1.4), (deformed body:1.3), "
    "blurry, watermark, text, logo, cartoon, anime, "
    "beard, stubble, long hair, earring, necklace, jewelry, feminine"
)

# Base description dufour
BASE = (
    "35 year old man, athletic stocky build, 200 pounds, broad shoulders, "
    "short dark brown hair, clean shaven, light blue colored irises, "
    "masculine face, natural expression mouth closed"
)

CATEGORIES = [
    # 1 - Hard BDSM / Bondage
    {
        "name": "bdsm",
        "prompt": f"{BASE}, completely naked, full black leather bondage harness strapped tight across muscular chest and torso, arms tied above head with leather cuffs and chains, spreader bar on ankles, ball gag in mouth, kneeling on concrete floor in dark dungeon, red and blue mood lighting, whip marks on chest and thighs, submissive pose but defiant eyes looking up, sweat on skin, heavy metal chains, hardcore kink aesthetic, extreme BDSM, dramatic shadows, sharp focus, raw gritty atmosphere",
        "count": 14
    },
    # 2 - Gangbang / Group
    {
        "name": "gangbang",
        "prompt": f"{BASE}, completely naked on all fours on a bed, being used by multiple men, several hard cocks in frame, one in mouth one in ass one in each hand, thick cum on face and chest and back, sweaty muscular bodies all around, messy fucked expression, open mouth tongue out, extreme hardcore group sex, cum covered face and torso, dramatic bedroom lighting, raw explicit porn aesthetic, hyper-detailed, sharp focus",
        "count": 14
    },
    # 3 - Raw Anal / Fucked
    {
        "name": "anal",
        "prompt": f"{BASE}, completely naked bent over doggystyle, massive thick cock stretching asshole wide open, gape visible, ass red from spanking, hands gripping bedsheets, face pressed into pillow, mouth open moaning, sweaty back muscles flexed, huge balls slapping against perineum, extreme close-up penetration, anal gaping, intense raw fucking, dramatic lighting, skin texture detail, sweat droplets, hardcore porn",
        "count": 14
    },
    # 4 - Bukkake / Cum
    {
        "name": "bukkake",
        "prompt": f"{BASE}, kneeling naked on floor, completely covered in thick cum from head to toe, multiple layers of cum dripping down face and chest and stomach, cum in hair and eyelashes and beard stubble, cum dripping from chin down to chest, several men standing around still jerking off aiming at him, open mouth full of cum some dripping out, messy excessive cum, extreme bukkake, dramatic overhead lighting, wet skin glistening, sharp focus, explicit hardcore",
        "count": 12
    },
    # 5 - Double Penetration
    {
        "name": "dp",
        "prompt": f"{BASE}, completely naked on back legs spread wide, two huge cocks penetrating simultaneously one in ass one in mouth, face and ass full at the same time, eyes rolled back in extreme pleasure, drool and precum everywhere, muscular body fully exposed and vulnerable, double penetration extreme, hardcore intense fucking, two men dominating, sweat and fluids everywhere, dramatic porn lighting, sharp focus, extreme explicit",
        "count": 12
    },
    # 6 - Biker / Leather Cruising
    {
        "name": "biker_cruise",
        "prompt": f"{BASE}, wearing only open leather vest and leather cap, completely naked below, huge hard thick cock fully erect veiny and dripping precum, standing in dark alley leaning against brick wall, headlights of motorcycle illuminating steam rising from skin, heavy leather boots, hand wrapped around base of cock stroking, raw masculine sexuality, anonymous hookup vibe, street meat aesthetic, explicit male nudity, hard cock detail, moody lighting, sharp focus",
        "count": 12
    },
    # 7 - Gloryhole / Public
    {
        "name": "gloryhole",
        "prompt": f"{BASE}, completely naked in a public sex club, huge hard cock sticking through a gloryhole, anonymous hands reaching to grab it, other men watching in the background, red darkroom lighting, slutty submissive pose on knees, cock fully erect and leaking, raw anonymous public sex, gloryhole booth setting, extreme explicit nudity, harsh red lighting, gritty underground sex club atmosphere, sharp focus",
        "count": 12
    },
    # 8 - Fisting / Extreme
    {
        "name": "fisting",
        "prompt": f"{BASE}, completely naked on back with legs pulled back to chest, a fist buried deep in his ass to the wrist, asshole stretched wide around the wrist, other hand gripping his own hard cock, face in extreme ecstasy, mouth wide open, sweat dripping, muscular thighs shaking, extreme fisting, raw gaping hole, intense explicit content, dramatic lighting focused on penetration point, hyper-detailed skin texture, sharp focus",
        "count": 6
    },
    # 9 - Slave / Training
    {
        "name": "slave",
        "prompt": f"{BASE}, completely naked crawling on hands and knees, black leather collar with metal ring tight around neck, leash trailing on floor, nipple clamps with chain connecting them, metal cock ring on hard erect cock dripping, ass plugged with large metal butt plug, submissive posture, dog bowl on floor in front of him, dark basement dungeon setting, chains and hooks on walls, extreme slave submission aesthetic, dramatic lighting, sharp focus",
        "count": 4
    }
]

def build_reactor_workflow(prompt_text, seed, prefix):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "juggernautXL_ragnarokBy.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt_text, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEGATIVE, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 832, "height": 1216, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
            "latent_image": ["4", 0],
            "seed": seed, "steps": 35, "cfg": 6.5,
            "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0
        }},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "ReActorLoadFaceModel", "inputs": {"face_model": "dufour_face.safetensors"}},
        "8": {"class_type": "ReActorFaceSwap", "inputs": {
            "enabled": True, "input_image": ["6", 0], "face_model": ["7", 0],
            "swap_model": "inswapper_128.onnx", "facedetection": "YOLOv5l",
            "face_restore_model": "GPEN-BFR-512.onnx", "face_restore_visibility": 1.0,
            "codeformer_weight": 0.5, "detect_gender_input": "no", "detect_gender_source": "no",
            "input_faces_index": "0", "source_faces_index": "0", "console_log_level": 1
        }},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "nsfw_peyo"}}
    }

total = sum(c["count"] for c in CATEGORIES)
print(f"🔥 Nightly NSFW Generator — {total} images")
print(f"   Catégories: {len(CATEGORIES)}")
print(f"   Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

done = 0
failed = 0
date_stamp = time.strftime('%Y%m%d')

for cat in CATEGORIES:
    name = cat["name"]
    count = cat["count"]
    prompt = cat["prompt"]
    print(f"\n📁 [{name}] — {count} images")
    for i in range(count):
        seed = random.randint(1000000, 9999999)
        prefix = f"nsfw_{date_stamp}_{name}_{i+1:02d}"
        try:
            wf = build_reactor_workflow(prompt, seed, prefix)
            out = generate(wf, timeout=300)
            done += 1
            print(f"  ✅ [{done}/{total}] {prefix}")
        except Exception as e:
            failed += 1
            print(f"  ❌ [{done+failed}/{total}] {prefix}: {e}")
        
        # Petit delay entre chaque pour pas surcharger
        if i < count - 1:
            time.sleep(1)

print(f"\n{'=' * 60}")
print(f"🎉 Terminé! {done} succès, {failed} échecs sur {total}")
notify_samba()
