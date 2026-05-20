# Using ComfyUI with LTX-2

Use LTX-2 in ComfyUI with visual node-based workflows. This is the recommended way to work with LTX-2 for most users.

## Installation

### Prerequisites
- ComfyUI installed
- CUDA-compatible GPU with 32GB+ VRAM
- 100GB+ free disk space for models and cache
- Python 3.10+

### Recommended: ComfyUI Manager
1. Open ComfyUI
2. Click the Templates button
3. Search for "LTX-2.3"
4. Select a template (Text to Video or Image to Video)
5. Press "Download all" to download the required models
6. Wait for installation to complete
7. Restart ComfyUI
The nodes appear under the "LTXVideo" category.

### Manual Installation
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Lightricks/ComfyUI-LTXVideo.git
cd ComfyUI-LTXVideo
pip install -r requirements.txt
```

For portable/embedded ComfyUI:
```bash
.\python_embeded\python.exe -m pip install -r .\ComfyUI\custom_nodes\ComfyUI-LTXVideo\requirements.txt
```

After installation, right-click canvas → Add Node → LTXVideo. Categories: loaders, samplers, conditioning, utils.

## Models

### Automatic Download
LTX-2 nodes auto-download models on first use. Load a workflow and click Queue Prompt.

### Manual Download
```bash
# 22B Distilled (recommended for beginners)
huggingface-cli download Lightricks/LTX-2.3 \
  --include "ltx-2.3-22b-distilled-1.1.safetensors" \
  --local-dir ComfyUI/models/checkpoints/LTX-Video

# 22B Full (maximum quality)
huggingface-cli download Lightricks/LTX-2.3 \
  --include "ltx-2.3-22b-dev.safetensors" \
  --local-dir ComfyUI/models/checkpoints/LTX-Video
```

### Text Encoder
Install Gemma 3 encoder via ComfyUI Manager (search "gemma-3-12b-it") or download from HuggingFace.

## Workflows

### Loading
1. Click Workflows
2. Navigate to custom_nodes/ComfyUI-LTXVideo/example_workflows/
3. Select a .json workflow file
4. Click Open

### Tips
- Start with low resolution (480x720)
- Use fewer frames (41-81) for speed
- Use distilled model for iteration, full model for final render
- Use FP8 models for VRAM savings

### Common Node Patterns

Basic generation: Model Loader → Text Encode → Sampler → VAE Decode → Save
Image-to-video: Load Image → Image Conditioning → Sampler → VAE Decode → Save
With upscaling: Sampler → Upscaler → Sampler → VAE Decode → Save

## Troubleshooting

### Nodes Not Appearing
Verify installation in ComfyUI/custom_nodes/ComfyUI-LTXVideo/
Check ComfyUI console for errors
Reinstall requirements: pip install -r requirements.txt
Restart ComfyUI completely

### Workflow Errors
- Missing nodes: Click "Install Missing Custom Nodes"
- Update ComfyUI and LTXVideo nodes
- Check model paths

### Model Loading Errors
- Verify model files aren't corrupted
- Ensure models are in correct directories:
  - Checkpoints: ComfyUI/models/checkpoints/
  - VAE: ComfyUI/models/vae/
  - LoRAs: ComfyUI/models/loras/
