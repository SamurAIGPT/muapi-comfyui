# MuAPI ComfyUI Nodes

> **The ultimate ComfyUI node pack for AI video, image, audio and enhancement** — powered by [muapi.ai](https://muapi.ai).
> Run 100+ state-of-the-art AI models inside ComfyUI with a single API key.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Nodes-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Models](https://img.shields.io/badge/Models-100%2B-orange)](https://muapi.ai)

## What is MuAPI?

[MuAPI](https://muapi.ai) is a generative media API aggregator giving you access to 100+ cutting-edge models: Seedance 2.0, Kling, Veo3, Flux, HiDream, GPT-image-1.5, Imagen4, and many more — all through one unified API key.

## Nodes (12 total)

| Node | Category | Description |
|------|----------|-------------|
| 🔑 MuAPI API Key | 🎬 MuAPI | Set your key once — wire to all nodes |
| 🎨 MuAPI Text-to-Image | 🎨 MuAPI | Flux, HiDream, GPT-image-1.5, Imagen4, Seedream … |
| 🎨 MuAPI Image-to-Image | 🎨 MuAPI | Flux Kontext, GPT-4o edit, Seededit, Wan edit … |
| 🎬 MuAPI Text-to-Video | 🎬 MuAPI | Seedance, Kling, Veo3, Wan, HunyuanVideo, Grok … |
| 🎬 MuAPI Image-to-Video | 🎬 MuAPI | 25+ I2V models, up to 4 reference images |
| 🎬 MuAPI Extend Video | 🎬 MuAPI | Extend any generation via request_id |
| ✨ MuAPI Image Enhance | ✨ MuAPI | Upscale, bg-remove, face-swap, Ghibli, colorize … |
| 🎬 MuAPI Video Edit | 🎬 MuAPI | Effects, dance, dress-change, upscale, lipsync … |
| 🎬 MuAPI Lipsync | 🎬 MuAPI | Sync.ai, Veed, Creatify |
| 🎵 MuAPI Audio | 🎵 MuAPI | Suno create/remix/extend, mmaudio |
| 🎬 MuAPI Generate (Generic) | 🎬 MuAPI | Any endpoint + raw JSON payload |
| 🎬 MuAPI Save Video | 🎬 MuAPI | Download video → disk + IMAGE frames |

## Installation

**Via ComfyUI Manager:**
1. Manager → Install via Git URL
2. Paste: `https://github.com/SamurAIGPT/muapi-comfyui`
3. Restart ComfyUI

**Manual:**
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/SamurAIGPT/muapi-comfyui
pip install -r muapi-comfyui/requirements.txt
```

## Quick Start

1. Get API key at [muapi.ai](https://muapi.ai) → Dashboard → API Keys
2. Right-click canvas → **Add Node** → **🔑 MuAPI API Key**, paste your key
3. Wire the `api_key` output to any generation node and queue the prompt

> **Tip:** If you use the [MuAPI CLI](https://github.com/SamurAIGPT/muapi-cli), run `muapi auth configure --api-key YOUR_KEY` once and all nodes pick it up automatically — no need to paste the key anywhere.

## Generic Node

Call **any** muapi endpoint with raw JSON. Use `__file_1__` … `__file_4__` placeholders for auto-uploaded images:

```json
{
  "prompt": "The character in @image1 runs through a forest",
  "images_list": ["__file_1__"],
  "aspect_ratio": "16:9",
  "quality": "basic",
  "duration": 5
}
```

## Supported Models (selected)

**T2V:** `seedance-v2.0-t2v` · `kling-v2.6-pro-t2v` · `veo3.1-text-to-video` · `wan2.5-text-to-video` · `hunyuan-text-to-video` · `minimax-hailuo-02-pro-t2v` · `grok-imagine-text-to-video`

**I2V:** `seedance-v2.0-i2v` · `seedance-2.0-new-omni` · `kling-v2.6-pro-i2v` · `veo3.1-image-to-video` · `wan2.5-image-to-video` · `hunyuan-image-to-video`

**T2I:** `flux-dev-image` · `flux-2-pro` · `flux-kontext-max-t2i` · `hidream_i1_full_image` · `gpt4o-text-to-image` · `google-imagen4-ultra` · `seedream-5.0` · `hunyuan-image-3.0`

**Enhance:** `ai-image-upscale` · `topaz-image-upscale` · `ai-background-remover` · `ai-ghibli-style` · `ai-color-photo` · `ai-object-eraser`

See the [full API docs](https://api.muapi.ai/docs) for 100+ endpoints.

## License

MIT © 2026
