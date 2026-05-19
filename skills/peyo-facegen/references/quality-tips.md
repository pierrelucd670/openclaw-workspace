# Quality Tips — Améliorer la qualité des générations PeyeOS

Basé sur recherche web + tests réels.

## 🎯 Priorité #1 : Référence dufour

Le Reactor face swap est limité par la qualité de la référence.

**Ce qui existe :** 10 photos dans `models/reactor/faces/dufour_train/`
- Toutes sont des selfies PXL (~4-6 MP)
- Éclairage naturel variable
- Angles variés mais majoritairement frontaux
- Résolution correcte mais pas optimale

**Comment améliorer :**
1. Générer un **portrait studio 1024x1024** via le workflow actuel avec un seed qui donne un visage parfait
2. Recadrer juste la face de cette image
3. L'utiliser comme nouvelle `source_image` dans Reactor (input direct, pas besoin de retrain)
4. Résultat : swap plus précis, meilleure rétention des détails du visage

## 🎛️ Réglages Reactor avancés

| Setting | Recommandé | Effet |
|---------|-----------|-------|
| `face_restore_model` | `GPEN-BFR-512` | Meilleur pour photoréaliste |
| `face_restore_visibility` | 0.8-1.0 | 1.0 = restauration complète |
| `codeformer_weight` | 0.5 | Équilibre identité/qualité |
| `facedetection` | `YOLOv5l` | Meilleure détection (défaut) |

## 🧪 Sampling optimisé

| Sampler + Scheduler | Steps | CFG | Usage |
|--------------------|-------|-----|-------|
| `dpmpp_2m` + `karras` | 40 | 6.5 | Bon équilibre rapidité/qualité |
| `dpmpp_2m_sde` + `karras` | 35 | 6.0 | Plus de détails fins |
| `dpmpp_3m_sde` + `karras` | 40 | 7.0 | Maximum qualité (lent) |
| `euler` + `normal` | 30 | 6.0 | Rapide, qualité décente |
| `ddim` + `ddim_uniform` | 30 | 5.5 | Rapide, moins de détails |

## 📐 Résolution

- **896x1152** (bon pour portraits, vertical)
- **1024x1024** (carré, polyvalent)
- **832x1216** (portrait serré, économique en VRAM)
- Résolutions plus hautes = plus de VRAM, pas toujours mieux avec Reactor

## 🔧 Améliorations hardware (nouveaux nodes)

### 1. ADetailer (face detailer)
→ Installe `ComfyUI-ADetailer` via Manager
→ Ajoute un pass de détail sur la face AVANT Reactor
→ Améliore nettement les yeux, texture de peau

### 2. Ultimate SD Upscale
→ Utilise `4x-UltraSharp.pth` (déjà installé)
→ Upscale l'image entière APRÈS face swap
→ Résultat : 4x la résolution, détails préservés

### 3. IP-Adapter FaceID
→ Ajoute une guidance d'identité PENDANT la génération
→ Reactor vient ensuite verrouiller l'identité
→ Meilleur que Reactor seul pour les angles difficiles

### 4. InstantID
→ Alternative à Reactor pour la préservation d'identité
→ Meilleur pour les expressions extrêmes et profils
→ Remplace Reactor dans le pipeline

## 📊 Pipeline recommandé (ultime qualité)

```
Checkpoint → IP-Adapter FaceID (soft identity)
→ KSampler → VAEDecode
→ ADetailer (face detail pass)
→ ReActor Face Swap (hard identity lock)
→ Ultimate SD Upscale 4x
→ Save Image
```

## 📸 Améliorer la référence dufour

Pour mettre à jour le modèle de face :

```bash
# 1. Générer un portrait parfait en close-up
python3 skills/peyo-facegen/scripts/generate.py \
  --prompt "close-up portrait, 35 year old man, ..." \
  --prefix "face_ref" --seed 7777

# 2. Utiliser cette image comme source_image dans Reactor
#    au lieu du modèle .safetensors
#    (déconnecter le ReActorLoadFaceModel,
#     utiliser un LoadImage à la place)
```

## 🧹 Checklist pré-génération

- [ ] VRAM disponible (GPU 0 pour ComfyUI)
- [ ] ComfyUI running (port 8188)
- [ ] Checkpoint juggernautXL chargé
- [ ] dufour_face.safetensors présent
- [ ] 4x-UltraSharp.pth présent (pour upscale)
- [ ] Samba notify script (pour Windows)
