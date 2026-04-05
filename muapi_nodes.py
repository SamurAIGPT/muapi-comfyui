"""
MuAPI ComfyUI Nodes — Full Suite
==================================
Universal nodes for every muapi.ai model category.

  MuAPITextToImage   — T2I  (Flux, HiDream, GPT-image, Imagen4, Seedream …)
  MuAPIImageToImage  — I2I  (Flux Kontext, GPT-4o edit, Seededit …)
  MuAPITextToVideo   — T2V  (Seedance, Kling, Veo3, Wan, Hunyuan …)
  MuAPIImageToVideo  — I2V  (all major I2V models)
  MuAPIExtendVideo   — extend a previous generation
  MuAPIImageEnhance  — upscale, bg-remove, face-swap, Ghibli, colorize …
  MuAPIVideoEdit     — effects, dance, dress-change, upscale, watermark …
  MuAPILipsync       — sync, veed, creatify
  MuAPIAudio         — Suno create / remix / extend, mmaudio
  MuAPIGenerate      — fully generic: any endpoint + raw JSON payload

Auth:     x-api-key header
API base: https://api.muapi.ai/api/v1
"""

import io
import json
import os
import time

import numpy as np
import requests
import torch
from PIL import Image

BASE_URL = "https://api.muapi.ai/api/v1"
POLL_INTERVAL = 10
MAX_WAIT = 900

# ── Endpoint lists ─────────────────────────────────────────────────────────────

T2I_ENDPOINTS = [
    "flux-dev-image", "flux-schnell-image", "flux-2-dev", "flux-2-pro",
    "flux-2-flex", "flux-2-klein-4b", "flux-2-klein-9b",
    "flux-kontext-dev-t2i", "flux-kontext-pro-t2i", "flux-kontext-max-t2i",
    "flux-krea-dev",
    "hidream_i1_fast_image", "hidream_i1_dev_image", "hidream_i1_full_image",
    "gpt4o-text-to-image", "gpt-image-1.5",
    "google-imagen4-fast", "google-imagen4", "google-imagen4-ultra",
    "bytedance-seedream-image", "bytedance-seedream-v4",
    "bytedance-seedream-v4.5", "seedream-5.0",
    "wan2.1-text-to-image", "wan2.5-text-to-image", "wan2.6-text-to-image",
    "hunyuan-image-2.1", "hunyuan-image-3.0",
    "kling-o1-text-to-image", "ideogram-v3-t2i",
    "grok-imagine-text-to-image", "chroma-image",
    "vidu-q2-text-to-image", "ai-anime-generator",
    "z-image-base", "z-image-turbo", "z-image-p",
    "straico-generate-image",
    "custom",
]

I2I_ENDPOINTS = [
    "flux-kontext-dev-i2i", "flux-kontext-pro-i2i", "flux-kontext-max-i2i",
    "flux-kontext-effects",
    "flux-2-dev-edit", "flux-2-pro-edit", "flux-2-flex-edit",
    "flux-2-klein-4b-edit", "flux-2-klein-9b-edit",
    "gpt4o-edit", "gpt4o-image-to-image", "gpt-image-1.5-edit",
    "bytedance-seededit-image", "bytedance-seedream-edit-v4",
    "bytedance-seedream-v4.5-edit", "seedream-5.0-edit", "seedance-v2.0-character",
    "grok-imagine-image-to-image", "higgsfield-soul-image-to-image",
    "kling-o1-edit-image", "ideogram-v3-reframe",
    "wan2.5-image-edit", "wan2.6-image-edit",
    "flux-redux", "flux-pulid", "tiktok-carousel",
    "custom",
]

T2V_ENDPOINTS = [
    "seedance-v2.0-t2v", "seedance-pro-t2v", "seedance-pro-t2v-fast",
    "seedance-lite-t2v", "seedance-v1.5-pro-t2v", "seedance-v1.5-pro-t2v-fast",
    "seedance-2.0-new-t2v", "seedance-2.0-t2v-480p",
    "kling-o1-text-to-video", "kling-v2.1-master-t2v",
    "kling-v2.5-turbo-pro-t2v", "kling-v2.6-pro-t2v",
    "veo3-text-to-video", "veo3-fast-text-to-video",
    "veo3.1-text-to-video", "veo3.1-fast-text-to-video", "veo3.1-4k-video",
    "grok-imagine-text-to-video",
    "wan2.1-text-to-video", "wan2.2-text-to-video",
    "wan2.2-5b-fast-t2v", "wan2.5-text-to-video", "wan2.5-text-to-video-fast",
    "wan2.6-text-to-video",
    "hunyuan-text-to-video", "hunyuan-fast-text-to-video",
    "minimax-hailuo-02-std-t2v", "minimax-hailuo-02-pro-t2v",
    "vidu-v2.0-t2v", "pixverse-t2v",
    "custom",
]

I2V_ENDPOINTS = [
    "seedance-v2.0-i2v", "seedance-pro-i2v", "seedance-pro-i2v-fast",
    "seedance-lite-i2v", "seedance-v1.5-pro-i2v", "seedance-v1.5-pro-i2v-fast",
    "seedance-2.0-new-omni", "seedance-2.0-new-first-last",
    "seedance-2.0-i2v-480p", "seedance-v2.0-omni-reference",
    "kling-o1-image-to-video", "kling-o1-standard-image-to-video",
    "kling-v2.1-master-i2v", "kling-v2.1-pro-i2v", "kling-v2.1-standard-i2v",
    "kling-v2.5-turbo-pro-i2v", "kling-v2.5-turbo-std-i2v",
    "kling-v2.6-pro-i2v", "kling-v3.0-pro-image-to-video",
    "veo3-image-to-video", "veo3-fast-image-to-video",
    "veo3.1-image-to-video", "veo3.1-fast-image-to-video",
    "grok-imagine-image-to-video",
    "wan2.1-image-to-video", "wan2.1-lora-i2v",
    "wan2.2-image-to-video", "wan2.2-spicy-image-to-video",
    "wan2.5-image-to-video", "wan2.5-image-to-video-fast",
    "wan2.6-image-to-video",
    "hunyuan-image-to-video",
    "vidu-v2.0-i2v", "vidu-q2-pro-start-end-video",
    "higgsfield-dop-image-to-video", "infinitetalk-image-to-video",
    "midjourney-i2v",
    "custom",
]

EXTEND_ENDPOINTS = [
    "seedance-v2.0-extend",
    "seedance-v1.5-pro-video-extend", "seedance-v1.5-pro-video-extend-fast",
    "veo3.1-extend-video", "wan2.2-spicy-video-extend",
    "custom",
]

ENHANCE_ENDPOINTS = [
    "ai-image-upscale", "topaz-image-upscale", "seedvr2-image-upscale",
    "ai-background-remover",
    "ai-image-face-swap",
    "ai-skin-enhancer",
    "ai-ghibli-style",
    "ai-color-photo",
    "ai-image-extension",
    "ai-object-eraser",
    "ai-product-shot", "ai-product-photography",
    "add-image-watermark",
    "custom",
]

VIDEO_EDIT_ENDPOINTS = [
    "video-effects", "image-effects",
    "ai-dance-effects", "ai-dress-change",
    "ai-video-face-swap",
    "ai-video-upscaler", "ai-video-upscaler-pro", "topaz-video-upscale",
    "video-watermark-remover", "seedance-v2.0-watermark-remover", "seedance-v2.0-video-watermark-remover-pro",
    "seedance-v2.0-video-edit",
    "add-video-watermark",
    "ai-clipping",
    "wan2.2-edit-video", "wan2.2-animate",
    "heygen-video-translate", "infinitetalk-video-to-video",
    "kling-o1-video-edit", "kling-o1-video-edit-fast",
    "custom",
]

LIPSYNC_ENDPOINTS = [
    "sync-lipsync", "veed-lipsync", "creatify-lipsync",
    "custom",
]

AUDIO_ENDPOINTS = [
    "suno-create-music", "suno-remix-music", "suno-extend-music",
    "mmaudio-text-to-audio", "mmaudio-video-to-audio",
    "custom",
]

# ── Shared helpers ─────────────────────────────────────────────────────────────

def _load_api_key(api_key_input):
    """Return api_key_input if set, otherwise fall back to ~/.muapi/config.json."""
    if api_key_input and api_key_input.strip():
        return api_key_input.strip()
    config_path = os.path.expanduser("~/.muapi/config.json")
    if os.path.isfile(config_path):
        try:
            with open(config_path) as f:
                key = json.load(f).get("api_key", "")
            if key:
                return key
        except Exception:
            pass
    raise ValueError(
        "No API key found. Either paste your key into the api_key field, "
        "or run `muapi auth configure --api-key YOUR_KEY` in a terminal."
    )

def _upload_image(api_key, image_tensor):
    if image_tensor.dim() == 4:
        image_tensor = image_tensor[0]
    arr = (image_tensor.cpu().numpy() * 255).astype("uint8")
    buf = io.BytesIO()
    Image.fromarray(arr, "RGB").save(buf, format="JPEG", quality=95)
    buf.seek(0)
    resp = requests.post(f"{BASE_URL}/upload_file",
                         headers={"x-api-key": api_key},
                         files={"file": ("image.jpg", buf, "image/jpeg")},
                         timeout=120)
    _check(resp)
    return _url(resp.json())

def _upload_file(api_key, path):
    mime = "video/mp4" if path.lower().endswith((".mp4", ".mov", ".webm")) else "image/jpeg"
    with open(path, "rb") as fh:
        resp = requests.post(f"{BASE_URL}/upload_file",
                             headers={"x-api-key": api_key},
                             files={"file": (os.path.basename(path), fh, mime)},
                             timeout=300)
    _check(resp)
    return _url(resp.json())

def _url(data):
    u = data.get("url") or data.get("file_url") or data.get("output")
    if not u:
        raise RuntimeError(f"Upload missing URL: {data}")
    return str(u)

def _submit(api_key, endpoint, payload):
    resp = requests.post(f"{BASE_URL}/{endpoint}",
                         headers={"x-api-key": api_key, "Content-Type": "application/json"},
                         json=payload, timeout=60)
    _check(resp)
    rid = resp.json().get("request_id")
    if not rid:
        raise RuntimeError(f"No request_id: {resp.json()}")
    return rid

def _poll(api_key, request_id):
    deadline = time.time() + MAX_WAIT
    while time.time() < deadline:
        resp = requests.get(f"{BASE_URL}/predictions/{request_id}/result",
                            headers={"x-api-key": api_key}, timeout=30)
        _check(resp)
        data = resp.json()
        status = data.get("status")
        print(f"[MuAPI] {status}  {request_id}")
        if status == "completed":
            return data
        if status == "failed":
            raise RuntimeError(f"Failed: {data.get('error', 'unknown')}")
        time.sleep(POLL_INTERVAL)
    raise RuntimeError(f"Timeout {request_id}")

def _output_url(result):
    out = result.get("outputs") or result.get("output") or []
    if isinstance(out, list) and out:
        return str(out[0])
    if isinstance(out, str):
        return out
    for k in ("video_url", "image_url", "audio_url", "url"):
        if result.get(k):
            return str(result[k])
    raise RuntimeError(f"No output URL: {result}")

def _check(resp):
    if resp.status_code == 401:
        raise RuntimeError("Auth failed — check API key.")
    if resp.status_code == 402:
        raise RuntimeError("Insufficient credits — top up at muapi.ai")
    if resp.status_code == 429:
        raise RuntimeError("Rate limited — retry later.")
    resp.raise_for_status()

def _img_from_url(url):
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        arr = np.array(Image.open(io.BytesIO(r.content)).convert("RGB")).astype(np.float32) / 255.0
        return torch.from_numpy(arr).unsqueeze(0)
    except Exception as e:
        print(f"[MuAPI] image download failed: {e}")
        return torch.zeros(1, 64, 64, 3)

def _first_frame(video_url):
    try:
        import tempfile, cv2
        r = requests.get(video_url, timeout=180, stream=True)
        r.raise_for_status()
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            for chunk in r.iter_content(8192):
                if chunk: tmp.write(chunk)
            path = tmp.name
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        cap.release(); os.remove(path)
        if not ret: raise RuntimeError("no frame")
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        return torch.from_numpy(rgb).unsqueeze(0)
    except Exception as e:
        print(f"[MuAPI] first frame failed: {e}")
        return torch.zeros(1, 64, 64, 3)

def _ep(model, custom):
    if model == "custom":
        ep = custom.strip()
        if not ep: raise ValueError("Set custom_endpoint when model='custom'.")
        return ep
    return model

def _extra(s):
    try: return json.loads(s or "{}")
    except json.JSONDecodeError as e: raise ValueError(f"Invalid JSON: {e}")

# ── Nodes ──────────────────────────────────────────────────────────────────────

class MuAPITextToImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": (T2I_ENDPOINTS, {"default": "flux-dev-image"}),
            "prompt": ("STRING", {"multiline": True, "default": "A photorealistic portrait of an astronaut on Mars"}),
            "aspect_ratio": (["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"], {"default": "1:1"}),
        }, "optional": {
            "api_key": ("STRING", {"multiline": False, "default": ""}),
            "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
            "custom_endpoint": ("STRING", {"multiline": False, "default": ""}),
            "extra_params_json": ("STRING", {"multiline": True, "default": "{}"}),
        }}
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "image_url", "request_id")
    FUNCTION = "run"
    CATEGORY = "🎨 MuAPI"

    def run(self, model, prompt, aspect_ratio,
            api_key="", negative_prompt="", custom_endpoint="", extra_params_json="{}"):
        api_key = _load_api_key(api_key)
        endpoint = _ep(model, custom_endpoint)
        payload = {"prompt": prompt, "aspect_ratio": aspect_ratio, **_extra(extra_params_json)}
        if negative_prompt.strip(): payload["negative_prompt"] = negative_prompt.strip()
        
        needs_wh = [
            "flux-dev", "flux-schnell", "flux-2-dev", "flux-2-pro", "flux-2-flex", 
            "flux-2-klein", "hidream_i1", "ai-anime", "wan2.", "hunyuan-image", 
            "chroma-image", "z-image-turbo", "z-image-p"
        ]
        if any(endpoint.startswith(p) for p in needs_wh) and "kontext" not in endpoint:
            mapping = {
                "1:1": (1024, 1024), "16:9": (1344, 768), "9:16": (768, 1344),
                "4:3": (1152, 864), "3:4": (864, 1152), "3:2": (1216, 832), "2:3": (832, 1216),
                "21:9": (1536, 640), "9:21": (640, 1536)
            }
            w, h = mapping.get(aspect_ratio, (1024, 1024))
            payload["width"] = w
            payload["height"] = h

        print(f"[MuAPI T2I] {endpoint}")
        rid = _submit(api_key, endpoint, payload)
        result = _poll(api_key, rid)
        url = _output_url(result)
        return (_img_from_url(url), url, rid)


class MuAPIImageToImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": (I2I_ENDPOINTS, {"default": "flux-kontext-pro-i2i"}),
            "image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True, "default": "Transform into a watercolour painting"}),
        }, "optional": {
            "api_key": ("STRING", {"multiline": False, "default": ""}),
            "custom_endpoint": ("STRING", {"multiline": False, "default": ""}),
            "extra_params_json": ("STRING", {"multiline": True, "default": "{}"}),
        }}
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "image_url", "request_id")
    FUNCTION = "run"
    CATEGORY = "🎨 MuAPI"

    def run(self, model, image, prompt, api_key="", custom_endpoint="", extra_params_json="{}"):
        api_key = _load_api_key(api_key)
        endpoint = _ep(model, custom_endpoint)
        print(f"[MuAPI I2I] Uploading image...")
        img_url = _upload_image(api_key, image)
        
        # Determine if endpoint needs images_list (array) or image_url (string)
        # Kontext, Wan2.x, Vidu, Seedream, Seedance usually use images_list
        needs_list = any(x in endpoint for x in ["kontext", "wan2.", "vidu", "seedream", "seedance"])
        if needs_list:
            payload = {"prompt": prompt, "images_list": [img_url], **_extra(extra_params_json)}
        else:
            payload = {"prompt": prompt, "image_url": img_url, **_extra(extra_params_json)}
            
        print(f"[MuAPI I2I] {endpoint}")
        rid = _submit(api_key, endpoint, payload)
        result = _poll(api_key, rid)
        url = _output_url(result)
        return (_img_from_url(url), url, rid)


class MuAPITextToVideo:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": (T2V_ENDPOINTS, {"default": "seedance-v2.0-t2v"}),
            "prompt": ("STRING", {"multiline": True, "default": "A cinematic aerial shot of a futuristic city at dusk"}),
            "aspect_ratio": (["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"], {"default": "16:9"}),
            "quality": (["basic", "high"], {"default": "basic"}),
            "duration": ("INT", {"default": 5, "min": 4, "max": 30, "step": 1}),
        }, "optional": {
            "api_key": ("STRING", {"multiline": False, "default": ""}),
            "custom_endpoint": ("STRING", {"multiline": False, "default": ""}),
            "extra_params_json": ("STRING", {"multiline": True, "default": "{}"}),
        }}
    RETURN_TYPES = ("STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("video_url", "first_frame", "request_id")
    FUNCTION = "run"
    CATEGORY = "🎬 MuAPI"

    def run(self, model, prompt, aspect_ratio, quality, duration,
            api_key="", custom_endpoint="", extra_params_json="{}"):
        api_key = _load_api_key(api_key)
        endpoint = _ep(model, custom_endpoint)
        payload = {"prompt": prompt, "aspect_ratio": aspect_ratio,
                   "quality": quality, "duration": duration, **_extra(extra_params_json)}
        print(f"[MuAPI T2V] {endpoint}")
        rid = _submit(api_key, endpoint, payload)
        result = _poll(api_key, rid)
        url = _output_url(result)
        return (url, _first_frame(url), rid)


class MuAPIImageToVideo:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": (I2V_ENDPOINTS, {"default": "seedance-v2.0-i2v"}),
            "prompt": ("STRING", {"multiline": True, "default": "The character in @image1 walks through a beautiful garden"}),
            "aspect_ratio": (["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"], {"default": "16:9"}),
            "quality": (["basic", "high"], {"default": "basic"}),
            "duration": ("INT", {"default": 5, "min": 4, "max": 30, "step": 1}),
        }, "optional": {
            "api_key": ("STRING", {"multiline": False, "default": ""}),
            "image_1": ("IMAGE",), "image_2": ("IMAGE",),
            "image_3": ("IMAGE",), "image_4": ("IMAGE",),
            "custom_endpoint": ("STRING", {"multiline": False, "default": ""}),
            "extra_params_json": ("STRING", {"multiline": True, "default": "{}"}),
        }}
    RETURN_TYPES = ("STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("video_url", "first_frame", "request_id")
    FUNCTION = "run"
    CATEGORY = "🎬 MuAPI"

    def run(self, model, prompt, aspect_ratio, quality, duration,
            api_key="", image_1=None, image_2=None, image_3=None, image_4=None,
            custom_endpoint="", extra_params_json="{}"):
        api_key = _load_api_key(api_key)
        endpoint = _ep(model, custom_endpoint)
        images_list = []
        for i, img in enumerate([image_1, image_2, image_3, image_4], 1):
            if img is not None:
                print(f"[MuAPI I2V] Uploading image {i}...")
                images_list.append(_upload_image(api_key, img))
        if not images_list: raise ValueError("At least one image required.")
        payload = {"prompt": prompt, "images_list": images_list,
                   "aspect_ratio": aspect_ratio, "quality": quality,
                   "duration": duration, **_extra(extra_params_json)}
        print(f"[MuAPI I2V] {endpoint}  {len(images_list)} image(s)")
        rid = _submit(api_key, endpoint, payload)
        result = _poll(api_key, rid)
        url = _output_url(result)
        return (url, _first_frame(url), rid)


class MuAPIExtendVideo:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": (EXTEND_ENDPOINTS, {"default": "seedance-v2.0-extend"}),
            "request_id": ("STRING", {"multiline": False, "default": ""}),
            "quality": (["basic", "high"], {"default": "basic"}),
            "duration": ("INT", {"default": 5, "min": 4, "max": 30, "step": 1}),
        }, "optional": {
            "api_key": ("STRING", {"multiline": False, "default": ""}),
            "prompt": ("STRING", {"multiline": True, "default": ""}),
            "custom_endpoint": ("STRING", {"multiline": False, "default": ""}),
            "extra_params_json": ("STRING", {"multiline": True, "default": "{}"}),
        }}
    RETURN_TYPES = ("STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("video_url", "first_frame", "new_request_id")
    FUNCTION = "run"
    CATEGORY = "🎬 MuAPI"

    def run(self, model, request_id, quality, duration,
            api_key="", prompt="", custom_endpoint="", extra_params_json="{}"):
        api_key = _load_api_key(api_key)
        if not request_id.strip(): raise ValueError("request_id required.")
        endpoint = _ep(model, custom_endpoint)
        payload = {"request_id": request_id.strip(), "quality": quality,
                   "duration": duration, **_extra(extra_params_json)}
        if prompt.strip(): payload["prompt"] = prompt.strip()
        print(f"[MuAPI Extend] {endpoint}")
        new_id = _submit(api_key, endpoint, payload)
        result = _poll(api_key, new_id)
        url = _output_url(result)
        return (url, _first_frame(url), new_id)


class MuAPIImageEnhance:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": (ENHANCE_ENDPOINTS, {"default": "ai-image-upscale"}),
            "image": ("IMAGE",),
        }, "optional": {
            "api_key": ("STRING", {"multiline": False, "default": ""}),
            "face_image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True, "default": ""}),
            "custom_endpoint": ("STRING", {"multiline": False, "default": ""}),
            "extra_params_json": ("STRING", {"multiline": True, "default": "{}"}),
        }}
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "image_url", "request_id")
    FUNCTION = "run"
    CATEGORY = "✨ MuAPI"

    def run(self, model, image, api_key="", face_image=None,
            prompt="", custom_endpoint="", extra_params_json="{}"):
        api_key = _load_api_key(api_key)
        endpoint = _ep(model, custom_endpoint)
        print(f"[MuAPI Enhance] Uploading image...")
        img_url = _upload_image(api_key, image)
        payload = {"image_url": img_url, **_extra(extra_params_json)}
        if face_image is not None:
            # Determine correct key for the secondary image based on endpoint
            key = "face_image_url"
            if endpoint == "ai-image-face-swap":
                key = "swap_url"
            elif endpoint == "ai-object-eraser":
                key = "mask_image_url"
            elif endpoint == "add-image-watermark":
                key = "watermark_image_url"
            
            payload[key] = _upload_image(api_key, face_image)
            
        if prompt.strip(): payload["prompt"] = prompt.strip()
        print(f"[MuAPI Enhance] {endpoint}")
        rid = _submit(api_key, endpoint, payload)
        result = _poll(api_key, rid)
        url = _output_url(result)
        return (_img_from_url(url), url, rid)


class MuAPIVideoEdit:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": (VIDEO_EDIT_ENDPOINTS, {"default": "video-effects"}),
            "video_url": ("STRING", {"multiline": False, "default": ""}),
        }, "optional": {
            "api_key": ("STRING", {"multiline": False, "default": ""}),
            "prompt": ("STRING", {"multiline": True, "default": ""}),
            "reference_image": ("IMAGE",),
            "custom_endpoint": ("STRING", {"multiline": False, "default": ""}),
            "extra_params_json": ("STRING", {"multiline": True, "default": "{}"}),
        }}
    RETURN_TYPES = ("STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("video_url", "first_frame", "request_id")
    FUNCTION = "run"
    CATEGORY = "🎬 MuAPI"

    def run(self, model, video_url, api_key="", prompt="",
            reference_image=None, custom_endpoint="", extra_params_json="{}"):
        api_key = _load_api_key(api_key)
        if not video_url.strip(): raise ValueError("video_url required.")
        endpoint = _ep(model, custom_endpoint)
        payload = {"video_url": video_url.strip(), **_extra(extra_params_json)}
        if prompt.strip(): payload["prompt"] = prompt.strip()
        if reference_image is not None:
            key = "image_url"
            if endpoint == "add-video-watermark":
                key = "watermark_image_url"
            payload[key] = _upload_image(api_key, reference_image)
            
        print(f"[MuAPI VideoEdit] {endpoint}")
        rid = _submit(api_key, endpoint, payload)
        result = _poll(api_key, rid)
        url = _output_url(result)
        return (url, _first_frame(url), rid)


class MuAPILipsync:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": (LIPSYNC_ENDPOINTS, {"default": "sync-lipsync"}),
            "video_url": ("STRING", {"multiline": False, "default": ""}),
            "audio_url": ("STRING", {"multiline": False, "default": ""}),
        }, "optional": {
            "api_key": ("STRING", {"multiline": False, "default": ""}),
            "audio_file_path": ("STRING", {"multiline": False, "default": ""}),
            "custom_endpoint": ("STRING", {"multiline": False, "default": ""}),
            "extra_params_json": ("STRING", {"multiline": True, "default": "{}"}),
        }}
    RETURN_TYPES = ("STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("video_url", "first_frame", "request_id")
    FUNCTION = "run"
    CATEGORY = "🎬 MuAPI"

    def run(self, model, video_url, audio_url, api_key="",
            audio_file_path="", custom_endpoint="", extra_params_json="{}"):
        api_key = _load_api_key(api_key)
        endpoint = _ep(model, custom_endpoint)
        if audio_file_path.strip() and os.path.isfile(audio_file_path):
            print("[MuAPI Lipsync] Uploading audio...")
            audio_url = _upload_file(api_key, audio_file_path)
        if not audio_url.strip(): raise ValueError("audio_url or audio_file_path required.")
        payload = {"video_url": video_url.strip(), "audio_url": audio_url.strip(),
                   **_extra(extra_params_json)}
        print(f"[MuAPI Lipsync] {endpoint}")
        rid = _submit(api_key, endpoint, payload)
        result = _poll(api_key, rid)
        url = _output_url(result)
        return (url, _first_frame(url), rid)


class MuAPIAudio:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": (AUDIO_ENDPOINTS, {"default": "suno-create-music"}),
            "prompt": ("STRING", {"multiline": True, "default": "An upbeat electronic track with driving bass"}),
        }, "optional": {
            "api_key": ("STRING", {"multiline": False, "default": ""}),
            "custom_endpoint": ("STRING", {"multiline": False, "default": ""}),
            "extra_params_json": ("STRING", {"multiline": True, "default": "{}"}),
        }}
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("audio_url", "request_id")
    FUNCTION = "run"
    CATEGORY = "🎵 MuAPI"

    def run(self, model, prompt, api_key="", custom_endpoint="", extra_params_json="{}"):
        api_key = _load_api_key(api_key)
        endpoint = _ep(model, custom_endpoint)
        payload = {"prompt": prompt, **_extra(extra_params_json)}
        print(f"[MuAPI Audio] {endpoint}")
        rid = _submit(api_key, endpoint, payload)
        result = _poll(api_key, rid)
        url = _output_url(result)
        return (url, rid)


class MuAPIGenerate:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "endpoint": ("STRING", {"multiline": False, "default": "seedance-v2.0-t2v"}),
            "payload_json": ("STRING", {"multiline": True,
                "default": json.dumps({
                    "image_url": "__file_1__",
                    "swap_url": "__file_2__",
                    "target_index": 0
                }, indent=2)}),
        }, "optional": {
            "api_key": ("STRING", {"multiline": False, "default": ""}),
            "file_1": ("IMAGE",), "file_2": ("IMAGE",),
            "file_3": ("IMAGE",), "file_4": ("IMAGE",),
            "file_path_1": ("STRING", {"default": ""}),
            "file_path_2": ("STRING", {"default": ""}),
        }}
    RETURN_TYPES = ("STRING", "IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("output_url", "preview", "request_id", "raw_result_json")
    FUNCTION = "run"
    CATEGORY = "🎬 MuAPI"

    def run(self, endpoint, payload_json, api_key="",
            file_1=None, file_2=None, file_3=None, file_4=None,
            file_path_1="", file_path_2=""):
        api_key = _load_api_key(api_key)
        if not endpoint.strip(): raise ValueError("endpoint required.")
        try: payload = json.loads(payload_json)
        except json.JSONDecodeError as e: raise ValueError(f"Invalid JSON: {e}")

        s = json.dumps(payload)
        for i, img in enumerate([file_1, file_2, file_3, file_4], 1):
            ph = f'"__file_{i}__"'
            if img is not None and ph in s:
                print(f"[MuAPI Generic] Uploading file_{i}...")
                s = s.replace(ph, f'"{_upload_image(api_key, img)}"')
        for i, p in enumerate([file_path_1, file_path_2], 1):
            ph = f'"__file_path_{i}__"'
            if p and p.strip() and os.path.isfile(p) and ph in s:
                print(f"[MuAPI Generic] Uploading file_path_{i}...")
                s = s.replace(ph, f'"{_upload_file(api_key, p)}"')
        payload = json.loads(s)

        print(f"[MuAPI Generic] {endpoint.strip()}")
        rid = _submit(api_key, endpoint.strip(), payload)
        result = _poll(api_key, rid)

        try: out_url = _output_url(result)
        except RuntimeError: out_url = ""

        if out_url and out_url.split("?")[0].lower().endswith((".mp4", ".mov", ".webm")):
            preview = _first_frame(out_url)
        elif out_url:
            preview = _img_from_url(out_url)
        else:
            preview = torch.zeros(1, 64, 64, 3)

        return (out_url, preview, rid, json.dumps(result, indent=2))


class MuAPIApiKey:
    """
    Store your MuAPI API key once and wire it to any node.
    Leave all node api_key fields empty — they auto-read from this node
    or from ~/.muapi/config.json (set via `muapi auth configure`).
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "api_key": ("STRING", {"multiline": False, "default": "",
                "tooltip": "Your muapi.ai API key. Get one at muapi.ai → Dashboard → API Keys"}),
        }}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("api_key",)
    FUNCTION = "run"
    CATEGORY = "🎬 MuAPI"

    def run(self, api_key):
        return (_load_api_key(api_key),)


NODE_CLASS_MAPPINGS = {
    "MuAPIApiKey":       MuAPIApiKey,
    "MuAPITextToImage":  MuAPITextToImage,
    "MuAPIImageToImage": MuAPIImageToImage,
    "MuAPITextToVideo":  MuAPITextToVideo,
    "MuAPIImageToVideo": MuAPIImageToVideo,
    "MuAPIExtendVideo":  MuAPIExtendVideo,
    "MuAPIImageEnhance": MuAPIImageEnhance,
    "MuAPIVideoEdit":    MuAPIVideoEdit,
    "MuAPILipsync":      MuAPILipsync,
    "MuAPIAudio":        MuAPIAudio,
    "MuAPIGenerate":     MuAPIGenerate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MuAPIApiKey":       "🔑 MuAPI API Key",
    "MuAPITextToImage":  "🎨 MuAPI Text-to-Image",
    "MuAPIImageToImage": "🎨 MuAPI Image-to-Image",
    "MuAPITextToVideo":  "🎬 MuAPI Text-to-Video",
    "MuAPIImageToVideo": "🎬 MuAPI Image-to-Video",
    "MuAPIExtendVideo":  "🎬 MuAPI Extend Video",
    "MuAPIImageEnhance": "✨ MuAPI Image Enhance",
    "MuAPIVideoEdit":    "🎬 MuAPI Video Edit",
    "MuAPILipsync":      "🎬 MuAPI Lipsync",
    "MuAPIAudio":        "🎵 MuAPI Audio",
    "MuAPIGenerate":     "🎬 MuAPI Generate (Generic)",
}
