# LTX-2 VRAM Requirements

Based on community testing with RTX 3060 12GB, RTX 4070 12GB, RTX 4090 24GB.

## Minimum vs Comfortable VRAM

- **8GB Minimum**: Can run LTX-2 in a pinch. Cap to lower resolutions (512x512), fewer frames (12-16), careful settings.
- **12GB Comfortable**: Practical baseline. Decent 512-640px square clips at modest frame counts (16-20).
- **24GB Creator sweet spot**: Push 720p+ and longer clips (24-32 frames) with fewer compromises.

## Full vs Distilled Model Comparison

### 512x512, 16 frames, 8-10 steps:
- Full model: ~10-12 GB peak
- Distilled: ~7-8.5 GB peak
- Distilled looks 85-90% as good in motion on casual viewing

### 768x768, 24 frames, 12-14 steps:
- Full model: ~20-22 GB peak
- Distilled: ~15-18 GB peak
- This is where 12GB cards choke unless dropping frames or precision

### 1280x720, 32 frames, 16 steps:
- Full model: often >24GB
- Distilled: ~20-22 GB peak
- Distilled at 720p/32f is the sweet spot on 24GB cards

## What Increases VRAM

1. **Resolution**: Pixel count is the loudest VRAM eater. Jump 512→768 = ~2.25x pixels
2. **Frames**: Going 16→24 frames often crosses from stable to OOM
3. **Batch size**: Keep at 1 for 12GB+ cards
4. **Precision**: fp16/bf16 vs fp32 makes significant difference

## Optimization Tips for 12GB Cards

- Use distilled model variant (~30-40% VRAM savings)
- Keep to 512-640px resolution
- Limit to 16-20 frames
- Use FP8 quantization
- Use gradient estimation to reduce steps from 40 to 20-30
- Use memory cleanup between stages
- Consider single-stage pipeline (no upscaling pass)
