# MuAPI ComfyUI Nodes

Run **any [muapi.ai](https://muapi.ai) model** directly inside ComfyUI.

## Nodes (11 total)

| Node | Category | Description |
|------|----------|-------------|
| 🎨 MuAPI Text-to-Image | 🎨 MuAPI | Flux, HiDream, GPT-image, Imagen4, Seedream, Wan … |
| 🎨 MuAPI Image-to-Image | 🎨 MuAPI | Flux Kontext, GPT-4o edit, Seededit, Wan edit … |
| 🎬 MuAPI Text-to-Video | 🎬 MuAPI | Seedance, Kling, Veo3, Wan, HunyuanVideo, Grok … |
| 🎬 MuAPI Image-to-Video | 🎬 MuAPI | All major I2V models |
| 🎬 MuAPI Extend Video | 🎬 MuAPI | Extend any previous generation |
| ✨ MuAPI Image Enhance | ✨ MuAPI | Upscale, bg-remove, face-swap, Ghibli, colorize … |
| 🎬 MuAPI Video Edit | 🎬 MuAPI | Effects, dance, dress-change, upscale, watermark … |
| 🎬 MuAPI Lipsync | 🎬 MuAPI | Sync.ai, Veed, Creatify |
| 🎵 MuAPI Audio | 🎵 MuAPI | Suno create/remix/extend, mmaudio |
| 🎬 MuAPI Generate (Generic) | 🎬 MuAPI | Any endpoint with raw JSON payload |
| 🎬 MuAPI Save Video | 🎬 MuAPI | Download URL → disk + frames tensor |

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

## Usage

1. Get your API key at [muapi.ai](https://muapi.ai) → Dashboard → API Keys
2. Right-click canvas → Add Node → find nodes under **🎨 MuAPI**, **🎬 MuAPI**, **✨ MuAPI**, or **🎵 MuAPI**
3. Paste your key into `api_key` and start generating

Every node has a **model dropdown** with 100+ endpoints and a `custom` option. The `extra_params_json` field accepts any model-specific parameters as a JSON object.

## Generic Node

The **🎬 MuAPI Generate (Generic)** node lets you call any endpoint with a raw JSON payload. Use `__file_1__` … `__file_4__` placeholders in the JSON — they are replaced with CDN URLs of the connected images automatically.

```json
{
  "prompt": "The character in @image1 runs through a forest",
  "images_list": ["__file_1__"],
  "aspect_ratio": "16:9",
  "quality": "basic",
  "duration": 5
}
```

## License

MIT
