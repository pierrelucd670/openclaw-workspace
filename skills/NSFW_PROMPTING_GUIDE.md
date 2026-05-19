# NSFW Prompting Guide — Par catégorie

Guide de prompts NSFW pour SDXL (JuggernautXL, EpicRealism, Lustify, Homofidelis, PornWorks).
Basé sur recherche web et tests. Chaque catégorie inclut les settings optimaux.

---

## Settings généraux SDXL (sauf indication contraire)

- **VAE**: sdxl_vae.safetensors (chargé externe)
- **CLIP skip**: 2
- **Steps**: 25-30
- **Sampler**: DPM++ 2M Karras
- **CFG**: 6-7 (sauf EpicRealism CFG5, PornWorks CFG4)
- **Resolution**: 1024×1024 (ou 896×1152 full body)
- **Negative général**: `(worst quality, low quality:1.4), plastic skin, doll-like, overexposed skin, bad anatomy, bad hands, extra limbs, cartoon, 3d render`

---

## 1. Solo femme — poses simples

> Sujet seul = meilleure anatomie. Focus sur le visage et la pose.

**Prompt**: `RAW photo, (photorealistic:1.3), beautiful naked woman, [pose], [description corps], [éclairage], 85mm f/1.8, film grain, natural skin texture, 8k`

**Variantes par pose**:
- **Debout**: `standing, frontal nude, hands at sides, looking at camera`
- **Allongée**: `lying on bed, legs slightly parted, one knee bent, silk sheets`
- **À quatre pattes**: `on all fours, ass up, looking back over shoulder`
- **Assise**: `sitting on chair, legs open, one hand between thighs`

**Settings**: JuggernautXL, CFG 7, NSFW Master LoRA 0.7

---

## 2. Masturbation

> Mains sur le corps, focus sur l'expression faciale et les doigts.

**Prompt**: `RAW photo, (photorealistic:1.3), naked woman masturbating, fingers rubbing clit, wet pussy, aroused face, legs spread, lying on bed, soft lighting, detailed skin, 85mm f/1.8, film grain`

**Negative add**: `(bad hands, missing fingers, fused fingers:1.4)`

**Settings**: JuggernautXL, CFG 7, NSFW Master LoRA 0.7
**Resolution**: 1024×1024 (portrait)

---

## 3. Blowjob / Oral sex

> 2 personnages = plus dur. Le mieux est de faire 1 personne qui suce ou focus sur l'acte.

**Prompt SDXL**: `RAW photo, (photorealistic:1.3), naked woman giving blowjob, huge cock in mouth, deepthroat, drooling, tears, eye contact, on knees, masculine man standing, bedroom, dramatic lighting, 85mm f/1.8`

**Prompt alternative (focus femme)**: `RAW photo, (photorealistic:1.3), beautiful woman on knees, sucking cock, messy makeup, tears, drool, passion, intense eye contact, soft lighting`

**Settings**: JuggernautXL, CFG 7-8, NSFW Master LoRA 0.8
**Resolution**: 1216×832 (landscape pour deux persos)

---

## 4. Doggystyle / Penetration par derrière

> Une des positions les plus faciles pour SDXL.

**Prompt**: `RAW photo, (photorealistic:1.3), naked couple fucking doggystyle, huge cock penetrating pussy from behind, ass up, sweaty bodies, passionate, bedroom, dramatic lighting, detailed skin, 85mm f/1.8`

**Settings**: JuggernautXL, CFG 7, NSFW Master LoRA 0.7 + dildo LoRA 0.3
**Resolution**: 1216×832

---

## 5. Missionnaire / Face à face

> Plus dur à cause des visages. CFG plus haut (8) pour respecter le prompt.

**Prompt**: `RAW photo, (photorealistic:1.3), naked couple missionary position, man on top penetrating woman, legs wrapped around, passionate kissing, intimate, bedroom, warm lighting, detailed skin, 85mm f/1.8`

**Settings**: JuggernautXL, CFG 8, 30 steps

---

## 6. Gangbang / Multi-personnages

> Très dur pour SDXL. Utiliser toomanyv2 LoRA + résolution plus grande. Accepter des imperfections.

**Prompt**: `RAW photo, (photorealistic:1.3), naked woman surrounded by men, gangbang, multiple cocks, cum on face and body, bukkake, messy, explicit, orgy, bedroom, dramatic lighting`

**Settings**: JuggernautXL + toomanyv2 LoRA 0.5, CFG 7
**Resolution**: 1216×832 ou 1344×768
**Note**: Les résultats seront imparfaits avec 3+ personnages.

---

## 7. BDSM / Bondage

> Voir aussi le skill bondage-artist. Sur Juggernaut pour réaliste, Pony pour stylisé.

**Prompt Juggernaut (réaliste)**: `RAW photo, (photorealistic:1.3), naked woman bound, rope bondage, shibari, tight ropes on skin, kneeling, submissive pose, red marks on skin, dark room, dramatic lighting, 85mm f/1.8`

**Settings**: JuggernautXL, CFG 6, shibari LoRA 0.5-0.6

---

## 8. Gay / Hommes seuls

> Focus sur anatomie masculine. Voir le skill gay-nsfw-suite.

**Prompt Homofidelis**: `RAW photo, (photorealistic:1.3), naked muscular man, standing, frontal nude, huge erect penis, detailed penis, muscular body, handsome face, studio lighting, sharp focus, film grain`

**Settings**: HomofidelisXL + Gay NSFW LoRA 0.6, CFG 6
**Resolution**: 1024×1536

**Prompt PornWorks**: `RAW photo, hyper-realistic muscular naked man, [description détaillée], studio lighting with softbox, detailed skin pores, 85mm lens, film grain, score_9, score_8_up, score_7_up`

**Settings**: PornWorks BadBoysPhoto, CFG 4, sampler dpmpp_2m_sde_gpu, 30 steps, scheduler karras

---

## 9. Sissy / Femboy / Crossdresser

> Combinaison d'attributs masculins/féminins. Meilleurs résultats sur JuggernautXL ou Homofidelis.

**Prompt**: `RAW photo, (photorealistic:1.3), beautiful sissy, feminine boy, smooth skin, wearing lingerie, lace babydoll, stockings, wig, makeup, lipstick, eyeliner, erect penis visible through sheer fabric, feminine pose, seductive, boudoir, soft lighting, 85mm f/1.8`

**Tags supplémentaires**: `crossdresser, makeup, lipstick, thigh highs, lace, feminine, smooth body, hairless`

**Settings**: JuggernautXL (réaliste) ou HomofidelisXL (plus masculin), CFG 7
**AndroCore LoRA**: 0.6 pour mélanger androgyne

---

## 10. Trans / Pre-op

**Prompt**: `RAW photo, (photorealistic:1.3), beautiful trans woman, naked, erect penis, feminine body, breasts, smooth skin, long hair, intimate pose, soft lighting, boudoir, 85mm f/1.8, film grain`

**Settings**: JuggernautXL, CFG 7
**AndroCore LoRA**: 0.5

---

## 11. Cunnilingus / Femme recevant

> Focus sur la tête entre les jambes. Plan serré.

**Prompt**: `RAW photo, (photorealistic:1.3), close-up, naked woman legs spread, head between thighs eating pussy, tongue on clit, intense pleasure face, wet pussy, intimate, bedroom, warm lighting`

**Settings**: JuggernautXL, CFG 7, NSFW Master LoRA 0.6
**Resolution**: 1024×1024

---

## 12. Bukkake / Cum

> Focus sur le liquide et l'expression.

**Prompt**: `RAW photo, (photorealistic:1.3), naked woman covered in cum, cum on face, cum dripping from mouth, cum on breasts, messy, satisfied expression, after sex, bedroom, soft lighting, detailed skin`

**Settings**: JuggernautXL, CFG 7, dildo LoRA 0.4

---

## 13. Lesbien / Femme sur femme

> 2 femmes = attention aux membres. Utiliser le dildo LoRA.

**Prompt**: `RAW photo, (photorealistic:1.3), two naked women, scissoring, pussies rubbing together, passionate, intimate, erotic, legs intertwined, soft lighting, bedroom, 85mm f/1.8, film grain`

**Settings**: JuggernautXL, CFG 7, 30 steps
**Resolution**: 1216×832
**Note**: Attention aux membres qui se chevauchent.

---

## 14. Hentai / Anime / Pony

> Voir le skill pony-nsfw-studio. Utiliser PonyDiffusionV6XL + score tags.

**Prompt**: `score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, rating_explicit, source_anime, BREAK, 1girl, naked, ahegao, spread legs, pussy juice, blush, hentai, detailed`

**Settings**: PonyDiffusionV6XL, CLIP skip -2, Euler CFG 5, 28 steps
**VAE**: sdxl_vae.safetensors

---

## 15. Furry / Anthro

> PonyDiffusionV6XL avec source_furry.

**Prompt**: `score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, rating_explicit, source_furry, BREAK, 1girl, female anthro, [espèce], naked, [action], detailed fur, [éclairage]`

**Settings**: PonyDiffusionV6XL, CLIP skip -2, Euler CFG 5

---

## 16. POV (Point of View)

> Style première personne. Très efficace pour l'immersion.

**Prompt**: `RAW photo, (photorealistic:1.3), POV shot, looking down at naked woman, she's looking up at camera, lying beneath, legs wrapped, intimate, bedroom, soft lighting, 35mm lens, shallow depth of field`

**Settings**: JuggernautXL, CFG 7

---

## Quick Reference — Model Settings

| Modèle | CFG | Sampler | Steps | VAE | CLIP skip | Spécial |
|--------|-----|---------|-------|-----|-----------|---------|
| **JuggernautXL Ragnarok** | 6-8 | DPM++ 2M Karras | 25-30 | sdxl_vae | 2 | "RAW photo, photorealistic:1.3" |
| **EpicRealismXL PureFix** | 5 | DPM++ 2M Karras | 20-25 | sdxl_vae | 2 | Peu de negatives |
| **LustifySDXLNSFW ggwpV7** | 6-7 | DPM++ 2M Karras | 25 | sdxl_vae | 2 | Tags + langage naturel |
| **HomofidelisXL v30** | 5-7 | DPM++ 2M Karras | 25-28 | sdxl_vae | 2 | Langage naturel |
| **PornWorks BadBoysPhoto** | 4 | dpmpp_2m_sde_gpu | 30 | sdxl_vae | 2 | score_9 tags, karras |
| **PonyDiffusionV6XL** | 4-6 | Euler | 28-30 | sdxl_vae | -2 | Score tags OBLIGATOIRE |
| **CyberrealisticPony** | 4-6 | Euler | 28-30 | sdxl_vae | -2 | Même que Pony |
| **Starstruck GayYaoi v10** | 5-7 | DPM++ 2M Karras | 25 | sdxl_vae | 2 | Style anime |

---

*Document créé le 18 mai 2026. Sources: flirton.ai, picassoia.com, civitai, huggingface, openlaboratory.*
