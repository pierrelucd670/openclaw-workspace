# LTX-2.3 Model Card

LTX-2.3 is a DiT-based audio-video foundation model designed to generate synchronized video and audio within a single model. It brings together the core building blocks of modern video generation, with open weights and a focus on practical, local execution.

## Model Checkpoints

- **ltx-2.3-22b-dev**: The full model, flexible and trainable in bf16 (42.98 GB)
- **ltx-2.3-22b-distilled**: The distilled version, 8 steps, CFG=1
- **ltx-2.3-22b-distilled-1.1**: Distilled v1.1, improved audio compared to v1.0
- **ltx-2.3-22b-distilled-lora-384**: LoRA version of the distilled model applicable to the full model (7.08 GB)
- **ltx-2.3-22b-distilled-lora-384-1.1**: LoRA version of the v1.1 distilled model (7.08 GB)
- **ltx-2.3-spatial-upscaler-x2-1.1**: x2 spatial upscaler for LTX-2.3 latents (~1 GB)
- **ltx-2.3-spatial-upscaler-x1.5-1.0**: x1.5 spatial upscaler
- **ltx-2.3-temporal-upscaler-x2-1.0**: x2 temporal upscaler for higher FPS

## Model Details

- Developed by: Lightricks
- Model type: Diffusion-based audio-video foundation model
- Language(s): English

## General Tips

- Width & height settings must be divisible by 32. Frame count must be divisible by 8 + 1.
- In case the resolution or number of frames are not divisible by 32 or 8 + 1, the input should be padded with -1 and then cropped to the desired resolution and number of frames.

## Limitations

- This model is not intended or able to provide factual information.
- The model may fail to generate videos that matches the prompts perfectly.
- Prompt following is heavily influenced by the prompting-style.
- The model may generate content that is inappropriate or offensive.
- When generating audio without speech, the audio may be of lower quality.

## Training

The base (dev) model is fully trainable. Training for motion, style or likeness (sound+appearance) can take less than an hour in many settings.

## Citation

@article{hacohen2025ltx2,
 title={LTX-2: Efficient Joint Audio-Visual Foundation Model},
 author={HaCohen, Yoav and Brazowski, Benny and Chiprut, Nisan and Bitterman, Yaki and Kvochko, Andrew and Berkowitz, Avishai and Shalem, Daniel and Lifschitz, Daphna and Moshe, Dudu and Porat, Eitan and Richardson, Eitan and Guy Shiran and Itay Chachy and Jonathan Chetboun and Michael Finkelson and Michael Kupchick and Nir Zabari and Nitzan Guetta and Noa Kotler and Ofir Bibi and Ori Gordon and Poriya Panet and Roi Benita and Shahar Armon and Victor Kulikov and Yaron Inger and Yonatan Shiftan and Zeev Melumian and Zeev Farbman},
 journal={arXiv preprint arXiv:2601.03233},
 year={2025}
}
