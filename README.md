# ComfyUI-OnePromptStoryboard

[English](README.md) | [日本語](README_ja.md)

The standard examples share the MOSS Qwen3.5 encoder for script generation, with all optional character/style LoRA slots disabled by default. See [model selection and settings](docs/GEMMA4_DEVELOPMENT.md) (Japanese) for optional Gemma4, system-prompt editing, and additional LoRAs.

A ComfyUI custom node that turns one request into a shared four-shot script, then generates storyboard instructions for MOSS and video instructions for MiniMax H3 Ref2VA.

**This repository installs only its own custom nodes. It does not automatically install models, MOSS, H3, external custom nodes, or Python packages.** This is an unofficial helper node.

## Installation

Run the following command in the ComfyUI `custom_nodes` folder, then restart ComfyUI:

```sh
git clone https://github.com/sepiablue-ai/ComfyUI-OnePromptStoryboard.git
```

Alternatively, extract the ZIP into `custom_nodes/ComfyUI-OnePromptStoryboard`. Registering the nodes requires no additional pip dependencies.

## Nodes

| Registered name | Purpose |
| --- | --- |
| `StoryboardPromptPlanner` | Uses a request and a compatible local text-generation CLIP to create a shared script; outputs the MOSS instructions, H3 instructions, script JSON, column count, and row count. The standard examples use Qwen3.5; an optional example supports Gemma4. |
| `StoryboardPromptText` | Lets you manually edit and output an H3 prompt. No model is required. |
| `StoryboardPlanCompile` | Restores instructions for both models from saved script JSON, without rerunning the LLM. |
| `StoryboardOptionalLora` | Adds an optional MOSS LoRA and trigger words. Disabled by default; duplicate and chain slots to add more. |

The planner uses ComfyUI's built-in `comfy_extras.nodes_textgen.TextGenerate`. You need a version of ComfyUI that provides this API and native MOSS/H3 support; older versions may need an update. The presence of a node alone does not mean that any CLIP can generate text. The included examples use the Qwen3.5 9B encoder with the `moss_image` type.

## Additional requirements

For the all-in-one examples, install the following yourself and follow each project's instructions and license:

- [ComfyUI](https://github.com/Comfy-Org/ComfyUI) with MOSS, MiniMax H3, Ref2VA, BlockSparseAttention, and TextGenerate support.
- [ComfyUI-MOSS-Storyboard](https://github.com/ZenHG/ComfyUI-MOSS-Storyboard) for `MossStoryboardSampler` and `MossStoryboardLayout`.
- [ComfyUI-FastH3-OmniRef-Accel](https://github.com/sepiablue-ai/ComfyUI-FastH3-OmniRef-Accel) for H3 acceleration, LBH, and video saving in the included examples. Check that repository for requirements such as the LBH latent upscaler.
- An NVIDIA NVENC-capable environment for video saving, plus FFmpeg and any other dependencies required by FastH3.

**The H3-only example does not require MOSS or its models.** The prompt-editing node itself does not require Qwen; the H3 workflow still requires its own text encoder. The FastH3 requirements still apply.

### Models specified in the included examples

| File | Location in ComfyUI |
| --- | --- |
| `moss_image_sft_int8_convrot.safetensors` | `models/diffusion_models` |
| `lora.safetensors` (8-step DMD for SFT) | `models/loras` |
| `qwen3.5_9b_int8_convrot.safetensors` | `models/text_encoders` |
| `flux2-vae.safetensors` | `models/vae` |
| `fasth3_omniref_8step_pruned_int8_convrot.safetensors` | `models/diffusion_models` |
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `models/text_encoders` |
| `minimax_h3_video_vae_int8_convrot.safetensors` | `models/vae` |
| `minimax_h3_audio_vae_fp32.safetensors` | `models/vae` |
| `minimax_h3_latent_upscaler_3d_conv_v1_fp16.safetensors` | `models/latent_upscale_models` |
| `realesr-animevideov3.pth` | `models/upscale_models` |

The H3 models are available from [FastVideo/FastH3-Omni-Comfy](https://huggingface.co/FastVideo/FastH3-Omni-Comfy). See the FastH3 repository for H3, LBH, and Real-ESRGAN setup requirements. Use the original distribution filenames. If you place files in subfolders, update the model selections in the workflow. No custom style LoRA is included or required by the examples.

The MOSS SFT INT8 model, Qwen, and VAE are available from [Comfy-Org/MOSS-Image](https://huggingface.co/Comfy-Org/MOSS-Image/tree/main). Use the distillation LoRA [`lora.safetensors`](https://huggingface.co/lodestones/MOSS-Image-SFT-8-steps-dmd/blob/main/lora.safetensors) from [lodestones/MOSS-Image-SFT-8-steps-dmd](https://huggingface.co/lodestones/MOSS-Image-SFT-8-steps-dmd) without renaming it. `lora_latest.safetensors` contains different weights. Also distinguish this LoRA from the DMD LoRA for the Base model.

For LBH, use `minimax_h3_latent_upscaler_3d_conv_v1_fp16.safetensors` from [Minimax_h3_latent_Upscaler](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/tree/main/minimax_h3_latent_upscaler_3d_conv_v1) without renaming it. The workflows use the same distribution filename.

### File verification and precision

On 2026-10-26, the weights used in the test environment were checked against the distribution sources' LFS SHA-256 hashes.

| Distribution file | SHA-256 |
| --- | --- |
| SFT DMD `lora.safetensors` | `4abb14e39c1a59018907581e609f43616ec6810126144ec2b1d2e6f8969628fe` |
| LBH `minimax_h3_latent_upscaler_3d_conv_v1_fp16.safetensors` | `043e5a48e161610ef6c3ea974645220354d06fa618abca15f76d084812eb55c2` |

The current lodestones model card shows how to use `lora.safetensors` at strength 1 with the standard ComfyUI LoRA loader. The older `transformer/` method, explicitly marked deprecated, requires FP32 loading and execution because the distilled differences are smaller than BF16 rounding. We do not interpret that requirement for the old method as requiring the base model to run in FP32 when using the current LoRA. The examples in this repository use an INT8 base model with a separately applied LoRA; their quality has not been compared with the distributor's FP32 configuration. Precision and the application method may affect quality.

## Generate everything from one request

Start with `workflows/all_in_one_magic_battle.json`, the standard example that shares the Qwen encoder with MOSS. The standard romance and meeting examples also use Qwen. Files ending in `.api.json` are for API submission.

`all_in_one_magic_battle_gemma4.json` is an optional example with Gemma4 selected initially. It requires a separate model download. The standard examples do not require Gemma4 or Ollama.

The included workflow labels are in Japanese. The labels below show their exact text followed by an English explanation.

1. Edit the request in `① 作りたい動画をここに1つ入力` (enter the video you want to make here).
2. Choose `横一列4コマ` (four panels in one horizontal row) or `縦一列4コマ` (four panels in one vertical column), and check the selected models.
3. Run the workflow. It processes the request → shared script → MOSS image → that single image as the H3 reference → saved video.
4. If you like the result, keep the saved storyboard and copy the previews from `保存用・生成されたH3プロンプト` (generated H3 prompt for saving) and `自動生成した共通台本・確認用` (automatically generated shared script for review) into text files. Automatic saving of scripts and prompts is not implemented.

The examples cover a magical-girl battle, a boy-meets-girl story, and a romance film. You write one story request; the instructions for each model are generated automatically. The workflows are designed for four shots and approximately 14 seconds; arbitrary shot counts are not supported.

## System prompt and optional LoRAs

Edit `system_prompt` in the request node to change the script's directing policy. For ordinary use, enter one story in `request`. The node appends the required four-shot JSON format instructions.

The optional-LoRA area contains three slots, all disabled initially. To use a slot, select a MOSS-compatible LoRA, set `strength_model` and `trigger_words`, then turn `enabled` on. Trigger words are added directly to the MOSS prompt, not the H3 prompt. A disabled slot loads no additional LoRA and adds no trigger words. To add more slots, duplicate a node and chain both its MODEL and STRING connections.

Character and style LoRAs are not bundled or downloaded automatically and are not required by default. The SFT DMD `lora.safetensors` required for 8-step generation remains enabled before the optional area and must be installed separately.

After updating, restart ComfyUI, force-reload the browser, and load the original updated workflow JSON. The workflows include stage groups and named-widget restoration.

## Keep a storyboard and regenerate only the H3 video

Load `workflows/h3_from_saved_storyboard.json`.

1. Load the image you want to use in `保存済みストーリーボードを1枚選択` (select one saved storyboard). `storyboard.png` is a placeholder filename.
2. In `H3プロンプトを編集・元の指示をここへコピー` (edit the H3 prompt and copy the original instructions here), paste the H3 prompt saved with that image. The default is the horizontal four-panel magical-girl example, so replace it when using another image.
3. Keep the panel order and character and costume correspondence, and adjust the action, camera, sound, and so on. For four vertical panels, also update the instructions to match the top-to-bottom order.
4. Run the workflow. This graph is not connected to MOSS or script generation; it runs only H3.

If you saved only the script JSON, paste it into `StoryboardPlanCompile` and choose the original layout to restore the H3 instructions. Preview the output and copy it into the editing field; you can then make changes without generating the script again.

## How the reference works and limitations

Qwen does not see the generated image. The shared script sends still-image compositions to MOSS and instructions including motion and camera work to H3. A fixed template tells H3 that reference image 1 contains four panels, that they correspond to shots 1–4, and that they should be expanded into full-frame video without the borders. Panels are not split for FL2VA; output 0 of the complete MOSS image is connected to Ref2VA as a single reference image.

There is no automatic detection or correction if MOSS produces the wrong number of panels or changes their content. The nodes do not analyze arbitrary image layouts or automatically read text descriptions. Invalid script JSON or fewer than four shots causes an error and stops execution. The BGM output field is currently fixed to `N/A`; requested music is not passed to H3.

MOSS uses `reborder=false`, disabling post-generation border redrawing. The included H3 examples use FastH3's LBH latent upscaling, Real-ESRGAN, resizing and center cropping, and NVENC saving. This repository itself does not repair or composite images or videos.

## Validation

On 2026-10-27, the standard all-in-one example ran with the shared Qwen encoder, all optional LoRAs disabled, and the default system prompt and seeds. It saved the storyboard and video in 203.80 seconds. The saved-image H3 example also succeeded in 173.04 seconds after changing only its image selection and the matching generated H3 prompt.

Both videos are 1024×1792 at 24 fps, lasting 14.375 seconds. All 345 video frames and 450 audio frames decoded successfully. In this test, the video files also had identical SHA-256 hashes. See [default-workflow validation](docs/DEFAULT_VALIDATION.md) (Japanese) for the scope and conditions.

Sixteen unit tests and the frontend named-widget restoration test passed on a fresh clone. Generation in this check used the API; GUI connections and named values were compared statically. Tests need no additional models:

```sh
python -m unittest discover -p "test_*.py" -v
```

Earlier isolated-installation tests are recorded in [the previous validation report](docs/VALIDATION.md); Gemma4 and GUI value-restoration checks are covered in [model selection and settings](docs/GEMMA4_DEVELOPMENT.md). Successful execution does not guarantee visual quality or support for every environment.

## License

GPL-3.0. The H3 examples are based on workflows from [ComfyUI-FastH3-OmniRef-Accel](https://github.com/sepiablue-ai/ComfyUI-FastH3-OmniRef-Accel), which is also GPL-3.0. Models and external nodes are subject to their respective licenses. Models and external implementations are not bundled.
