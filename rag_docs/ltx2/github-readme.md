# LTX-2

LTX-2 is the first DiT-based audio-video foundation model that contains all core capabilities of modern video generation in one model: synchronized audio and video, high fidelity, multiple performance modes, production-ready outputs, API access, and open access.

## Quick Start

```bash
git clone https://github.com/Lightricks/LTX-2.git
cd LTX-2
uv sync --frozen
source .venv/bin/activate
```

## Required Models

Download from https://huggingface.co/Lightricks/LTX-2.3:

- **Base Checkpoint**: ltx-2.3-22b-dev.safetensors OR ltx-2.3-22b-distilled-1.1.safetensors
- **Spatial Upscaler**: ltx-2.3-spatial-upscaler-x2-1.1.safetensors (for two-stage pipeline)
- **Temporal Upscaler**: ltx-2.3-temporal-upscaler-x2-1.0.safetensors
- **Distilled LoRA**: ltx-2.3-22b-distilled-lora-384-1.1.safetensors (for two-stage pipeline)
- **Gemma Text Encoder**: google/gemma-3-12b-it-qat-q4_0-unquantized
- **IC-LoRAs**: Various control LoRAs (union control, motion track, HDR, LipDub, pose, camera controls)

## Available Pipelines

- **TI2VidTwoStagesPipeline** - Production-quality text/image-to-video with 2x upsampling (recommended)
- **TI2VidTwoStagesHQPipeline** - Same two-stage flow with res_2s second-order sampler (fewer steps, better quality)
- **TI2VidOneStagePipeline** - Single-stage generation for quick prototyping
- **DistilledPipeline** - Fastest inference with 8 predefined sigmas
- **ICLoraPipeline** - Video-to-video and image-to-video transformations
- **KeyframeInterpolationPipeline** - Interpolate between keyframe images
- **A2VidPipelineTwoStage** - Audio-to-video generation conditioned on input audio
- **RetakePipeline** - Regenerate a specific time region of an existing video
- **HDRICLoraPipeline** - Video-to-video with HDR output
- **LipDubPipeline** - Lip dubbing, rephrasing, matching speaker identity

## CLI Usage

Each pipeline module is executable:
```bash
python -m ltx_pipelines.ti2vid_two_stages \
    --checkpoint-path path/to/checkpoint.safetensors \
    --distilled-lora path/to/distilled_lora.safetensors 0.8 \
    --spatial-upsampler-path path/to/upsampler.safetensors \
    --gemma-root path/to/gemma \
    --prompt "A beautiful sunset over the ocean" \
    --output-path output.mp4
```

## Optimization Tips

- **Use DistilledPipeline** - Fastest with only 8 predefined sigmas (8 steps stage 1, 4 steps stage 2)
- **Enable FP8 quantization**: --quantization fp8-cast or quantization=QuantizationPolicy.fp8_cast()
- **Install attention optimizations**: xFormers or Flash Attention 3
- **Use gradient estimation**: Reduce inference steps from 40 to 20-30
- **Skip memory cleanup** if you have sufficient VRAM

## Prompting for LTX-2

Focus on detailed, chronological descriptions of actions and scenes. Include specific movements, appearances, camera angles, and environmental details in a single flowing paragraph. Start directly with the action, keep descriptions literal and precise. Keep within 200 words.

Structure:
- Start with main action in a single sentence
- Add specific details about movements and gestures
- Describe character/object appearances precisely
- Include background and environment details
- Specify camera angles and movements
- Describe lighting and colors
- Note any changes or sudden events

Support for automatic prompt enhancement via enhance_prompt parameter.

## ComfyUI Integration

https://github.com/Lightricks/ComfyUI-LTXVideo/

## VRAM Requirements (from community testing)

On RTX 3060 12GB:
- Distilled model at 512x512, 16 frames: ~7-8.5 GB peak
- Distilled model at 768x768, 24 frames: ~15-18 GB peak (too much for 12GB)
- Distilled model at 1280x720, 32 frames: ~20-22 GB peak
- Full model at 512x512, 16 frames: ~10-12 GB peak
- Full model at 768x768, 24 frames: ~20-22 GB peak

Distilled variant saves ~30-40% VRAM versus full model at same resolution/frame count.

For 12GB cards: keep to 512-640px, 16-20 frames, distilled model.
