"""
Generates example ComfyUI workflow JSON files for the MuAPI node pack.

Run:  python workflows/_generate_workflows.py
Outputs *.json files into the same directory.

Each spec describes nodes by display-friendly handles; the generator
expands them into the full ComfyUI graph format with proper links.
"""

import json
import os
from pathlib import Path

OUT_DIR = Path(__file__).parent

# ── Node widget signatures ────────────────────────────────────────────────────
# Order MUST match INPUT_TYPES iteration in muapi_nodes.py:
#   required first, then optional.
WIDGETS = {
    "MuAPIApiKey":       ["api_key"],
    "MuAPITextToImage":  ["model", "prompt", "aspect_ratio",
                          "api_key", "negative_prompt", "custom_endpoint", "extra_params_json"],
    "MuAPIImageToImage": ["model", "prompt",
                          "api_key", "custom_endpoint", "extra_params_json"],
    "MuAPITextToVideo":  ["model", "prompt", "aspect_ratio", "quality", "duration",
                          "api_key", "custom_endpoint", "extra_params_json"],
    "MuAPIImageToVideo": ["model", "prompt", "aspect_ratio", "quality", "duration",
                          "api_key", "custom_endpoint", "extra_params_json"],
    "MuAPIExtendVideo":  ["model", "request_id", "quality", "duration",
                          "api_key", "custom_endpoint", "extra_params_json"],
    "MuAPIImageEnhance": ["model",
                          "api_key", "custom_endpoint", "extra_params_json"],
    "MuAPIVideoEdit":    ["model", "video_url",
                          "api_key", "prompt", "custom_endpoint", "extra_params_json"],
    "MuAPILipsync":      ["model", "video_url", "audio_url",
                          "api_key", "audio_file_path", "custom_endpoint", "extra_params_json"],
    "MuAPIAudio":        ["model", "prompt",
                          "api_key", "custom_endpoint", "extra_params_json"],
    "MuAPIImageTo3D":    ["model", "prompt",
                          "api_key", "custom_endpoint", "extra_params_json"],
    "MuAPIGenerate":     ["endpoint", "payload_json",
                          "api_key", "file_path_1", "file_path_2"],
    "MuAPIVideoSaver":   ["video_url", "save_subfolder", "filename_prefix",
                          "frame_load_cap", "skip_first_frames", "select_every_nth"],
    # built-in nodes
    "LoadImage":         ["image", "upload"],
    "PreviewImage":      [],
    "SaveImage":         ["filename_prefix"],
}

# Connection-only inputs (IMAGE type, etc.) that are NOT widgets.
IMG_INPUTS = {
    "MuAPIImageToImage": ["image"],
    "MuAPIImageToVideo": ["image_1", "image_2", "image_3", "image_4"],
    "MuAPIImageEnhance": ["image", "swap_image"],
    "MuAPIVideoEdit":    ["secondary_image"],
    "MuAPIImageTo3D":    ["image_1", "image_2", "image_3"],
    "MuAPIGenerate":     ["file_1", "file_2", "file_3", "file_4"],
    "PreviewImage":      ["images"],
    "SaveImage":         ["images"],
    "MuAPIVideoSaver":   [],
}

# Output slots in order.
OUTPUTS = {
    "MuAPIApiKey":       [("api_key", "STRING")],
    "MuAPITextToImage":  [("image", "IMAGE"), ("image_url", "STRING"), ("request_id", "STRING")],
    "MuAPIImageToImage": [("image", "IMAGE"), ("image_url", "STRING"), ("request_id", "STRING")],
    "MuAPITextToVideo":  [("video_url", "STRING"), ("first_frame", "IMAGE"), ("request_id", "STRING")],
    "MuAPIImageToVideo": [("video_url", "STRING"), ("first_frame", "IMAGE"), ("request_id", "STRING")],
    "MuAPIExtendVideo":  [("video_url", "STRING"), ("first_frame", "IMAGE"), ("new_request_id", "STRING")],
    "MuAPIImageEnhance": [("image", "IMAGE"), ("image_url", "STRING"), ("request_id", "STRING")],
    "MuAPIVideoEdit":    [("video_url", "STRING"), ("first_frame", "IMAGE"), ("request_id", "STRING")],
    "MuAPILipsync":      [("video_url", "STRING"), ("first_frame", "IMAGE"), ("request_id", "STRING")],
    "MuAPIAudio":        [("audio_url", "STRING"), ("request_id", "STRING")],
    "MuAPIImageTo3D":    [("model_url", "STRING"), ("request_id", "STRING")],
    "MuAPIGenerate":     [("output_url", "STRING"), ("preview", "IMAGE"),
                          ("request_id", "STRING"), ("raw_result_json", "STRING")],
    "MuAPIVideoSaver":   [("frames", "IMAGE"), ("filepath", "STRING"), ("frame_count", "INT")],
    "LoadImage":         [("IMAGE", "IMAGE"), ("MASK", "MASK")],
    "PreviewImage":      [],
    "SaveImage":         [],
}


def build(spec):
    """spec = {nodes: [...], links: [(src_handle, src_slot, dst_handle, dst_slot), ...]}"""
    nodes_out, links_out = [], []
    handles = {}
    nid = 0
    lid = 0
    x = 40

    for n in spec["nodes"]:
        nid += 1
        handle = n["handle"]
        ntype = n["type"]
        widgets = n.get("widgets", {})
        widget_order = WIDGETS.get(ntype, [])
        widget_vals = [widgets.get(w, _default(ntype, w)) for w in widget_order]

        inputs = []
        for inp_name in IMG_INPUTS.get(ntype, []):
            inputs.append({"name": inp_name, "type": _input_type(ntype, inp_name), "link": None})

        outputs = []
        for out_name, out_type in OUTPUTS.get(ntype, []):
            outputs.append({"name": out_name, "type": out_type, "links": [], "slot_index": len(outputs)})

        node = {
            "id": nid,
            "type": ntype,
            "pos": [x, 60 + (nid % 3) * 320],
            "size": [340, 240],
            "flags": {},
            "order": nid - 1,
            "mode": 0,
            "inputs": inputs,
            "outputs": outputs,
            "properties": {"Node name for S&R": ntype},
            "widgets_values": widget_vals,
        }
        nodes_out.append(node)
        handles[handle] = node
        x += 380

    for src_h, src_slot, dst_h, dst_slot in spec.get("links", []):
        lid += 1
        src = handles[src_h]
        dst = handles[dst_h]
        out = src["outputs"][src_slot]
        inp = dst["inputs"][dst_slot]
        out["links"].append(lid)
        inp["link"] = lid
        links_out.append([lid, src["id"], src_slot, dst["id"], dst_slot, out["type"]])

    return {
        "last_node_id": nid,
        "last_link_id": lid,
        "nodes": nodes_out,
        "links": links_out,
        "groups": [],
        "config": {},
        "extra": {"ds": {"scale": 1.0, "offset": [0, 0]}},
        "version": 0.4,
    }


def _input_type(ntype, name):
    if name in ("file_1", "file_2", "file_3", "file_4",
                "image", "image_1", "image_2", "image_3", "image_4",
                "swap_image", "secondary_image", "images"):
        return "IMAGE"
    return "STRING"


# Reusable nano-banana-2 (Gemini-3 style) brief used in many skill examples.
NANO_REASONING_BRIEF = (
    "Subject: a single product hero shot. Action: floating with subtle rotation. "
    "Context: minimalist studio with seamless cyclorama. Composition: 85mm lens, f/2.8, "
    "centered. Lighting: soft volumetric key from upper-left, gentle rim light. "
    "Style: cinematic, photorealistic, 4K commercial."
)


def _default(ntype, w):
    defaults = {
        "api_key": "", "custom_endpoint": "", "extra_params_json": "{}",
        "negative_prompt": "", "filename_prefix": "muapi", "save_subfolder": "muapi_videos",
        "frame_load_cap": 0, "skip_first_frames": 0, "select_every_nth": 1,
        "audio_file_path": "", "audio_url": "", "video_url": "",
        "request_id": "", "file_path_1": "", "file_path_2": "",
        "image": "example.png", "upload": "image",
    }
    return defaults.get(w, "")


# ── Workflow specs ─────────────────────────────────────────────────────────────

WORKFLOWS = {
    "MuAPI_Basic_TextToImage_Flux.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "flux-dev-image",
                "prompt": "A photorealistic portrait of an astronaut on Mars, cinematic lighting, 35mm film",
                "aspect_ratio": "1:1",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("t2i", 0, "preview", 0)],
    },

    "MuAPI_TextToImage_Imagen4.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "google-imagen4-ultra",
                "prompt": "Macro photo of a dewdrop on a red maple leaf, sunrise",
                "aspect_ratio": "16:9",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "imagen4"}},
        ],
        "links": [("t2i", 0, "save", 0)],
    },

    "MuAPI_TextToImage_Seedream5.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "seedream-5.0",
                "prompt": "Studio Ghibli inspired countryside village at golden hour",
                "aspect_ratio": "3:2",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("t2i", 0, "preview", 0)],
    },

    "MuAPI_TextToImage_GPT_Image.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "gpt-image-1.5",
                "prompt": "Vintage travel poster of Tokyo, bold typography, retro print textures",
                "aspect_ratio": "9:16",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("t2i", 0, "preview", 0)],
    },

    "MuAPI_TextToImage_HiDream.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "hidream_i1_full_image",
                "prompt": "Hyperrealistic cyberpunk samurai under neon rain, ultra detail",
                "aspect_ratio": "9:16",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("t2i", 0, "preview", 0)],
    },

    "MuAPI_ImageToImage_FluxKontext.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "i2i", "type": "MuAPIImageToImage", "widgets": {
                "model": "flux-kontext-pro-i2i",
                "prompt": "Make this a moody black-and-white film still",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("load", 0, "i2i", 0), ("i2i", 0, "preview", 0)],
    },

    "MuAPI_ImageToImage_Seededit.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "i2i", "type": "MuAPIImageToImage", "widgets": {
                "model": "bytedance-seededit-image",
                "prompt": "Replace the background with snowy mountains at sunrise",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("load", 0, "i2i", 0), ("i2i", 0, "preview", 0)],
    },

    "MuAPI_ImageToImage_GPT4o_Edit.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "i2i", "type": "MuAPIImageToImage", "widgets": {
                "model": "gpt4o-edit",
                "prompt": "Add a cat sitting on the chair in the foreground",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("load", 0, "i2i", 0), ("i2i", 0, "preview", 0)],
    },

    "MuAPI_TextToVideo_Seedance.json": {
        "nodes": [
            {"handle": "t2v", "type": "MuAPITextToVideo", "widgets": {
                "model": "seedance-v2.0-t2v",
                "prompt": "Aerial shot flying over a misty rainforest at dawn",
                "aspect_ratio": "16:9", "quality": "basic", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "seedance",
            }},
        ],
        # Wire video_url (out 0) into the saver's video_url widget — convert widget to input.
        # For simplicity here, the saver also has video_url as its first widget; user can paste manually
        # or right-click → convert to input. Most workflows wire it via the link below.
        "links": [],  # handled with a note below
    },

    "MuAPI_TextToVideo_Veo3.json": {
        "nodes": [
            {"handle": "t2v", "type": "MuAPITextToVideo", "widgets": {
                "model": "veo3.1-text-to-video",
                "prompt": "A cinematic tracking shot of a wolf walking through a snowy forest",
                "aspect_ratio": "16:9", "quality": "high", "duration": 8,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "veo3",
            }},
        ],
        "links": [],
    },

    "MuAPI_TextToVideo_Kling.json": {
        "nodes": [
            {"handle": "t2v", "type": "MuAPITextToVideo", "widgets": {
                "model": "kling-v2.6-pro-t2v",
                "prompt": "A dragon soaring above a medieval castle, epic cinematic shot",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "kling",
            }},
        ],
        "links": [],
    },

    "MuAPI_ImageToVideo_Seedance.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "i2v", "type": "MuAPIImageToVideo", "widgets": {
                "model": "seedance-v2.0-i2v",
                "prompt": "The character in @image1 starts dancing under spotlight",
                "aspect_ratio": "9:16", "quality": "basic", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "seedance_i2v",
            }},
        ],
        "links": [("load", 0, "i2v", 0)],
    },

    "MuAPI_ImageToVideo_Veo3.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "i2v", "type": "MuAPIImageToVideo", "widgets": {
                "model": "veo3.1-image-to-video",
                "prompt": "Slow cinematic push-in. Subject smiles and turns toward the camera.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 8,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "veo3_i2v",
            }},
        ],
        "links": [("load", 0, "i2v", 0)],
    },

    "MuAPI_ImageToVideo_4References.json": {
        "nodes": [
            {"handle": "img1", "type": "LoadImage"},
            {"handle": "img2", "type": "LoadImage"},
            {"handle": "img3", "type": "LoadImage"},
            {"handle": "img4", "type": "LoadImage"},
            {"handle": "i2v", "type": "MuAPIImageToVideo", "widgets": {
                "model": "seedance-2.0-new-omni",
                "prompt": "Combine the characters from @image1 and @image2 in the setting from @image3, styled like @image4. Cinematic shot.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "omni_4ref",
            }},
        ],
        "links": [
            ("img1", 0, "i2v", 0),
            ("img2", 0, "i2v", 1),
            ("img3", 0, "i2v", 2),
            ("img4", 0, "i2v", 3),
        ],
    },

    "MuAPI_ExtendVideo.json": {
        "nodes": [
            {"handle": "t2v", "type": "MuAPITextToVideo", "widgets": {
                "model": "seedance-v2.0-t2v",
                "prompt": "Time-lapse of clouds rolling over mountain peaks",
                "aspect_ratio": "16:9", "quality": "basic", "duration": 5,
            }},
            {"handle": "extend", "type": "MuAPIExtendVideo", "widgets": {
                "model": "seedance-v2.0-extend",
                "quality": "basic", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "extended",
            }},
        ],
        # request_id (out 2) → extend.request_id widget — left as widget; user pastes.
        "links": [],
    },

    "MuAPI_FaceSwap.json": {
        "nodes": [
            {"handle": "base", "type": "LoadImage"},
            {"handle": "face", "type": "LoadImage"},
            {"handle": "swap", "type": "MuAPIImageEnhance", "widgets": {
                "model": "ai-image-face-swap",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [
            ("base", 0, "swap", 0),
            ("face", 0, "swap", 1),
            ("swap", 0, "preview", 0),
        ],
    },

    "MuAPI_Upscale_Topaz.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "up", "type": "MuAPIImageEnhance", "widgets": {
                "model": "topaz-image-upscale",
                "extra_params_json": '{"scale": 4}',
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "topaz_4x"}},
        ],
        "links": [("load", 0, "up", 0), ("up", 0, "save", 0)],
    },

    "MuAPI_BackgroundRemover.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "rm", "type": "MuAPIImageEnhance", "widgets": {
                "model": "ai-background-remover",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "no_bg"}},
        ],
        "links": [("load", 0, "rm", 0), ("rm", 0, "save", 0)],
    },

    "MuAPI_Ghibli_Style.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "ghibli", "type": "MuAPIImageEnhance", "widgets": {
                "model": "ai-ghibli-style",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("load", 0, "ghibli", 0), ("ghibli", 0, "preview", 0)],
    },

    "MuAPI_ProductShot.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "ps", "type": "MuAPIImageEnhance", "widgets": {
                "model": "ai-product-shot",
                "extra_params_json": '{"prompt": "on a marble countertop with soft window light"}',
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("load", 0, "ps", 0), ("ps", 0, "preview", 0)],
    },

    "MuAPI_VideoUpscale_Topaz.json": {
        "nodes": [
            {"handle": "edit", "type": "MuAPIVideoEdit", "widgets": {
                "model": "topaz-video-upscale",
                "extra_params_json": '{"scale": 2}',
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "topaz_video",
            }},
        ],
        "links": [],
    },

    "MuAPI_VideoEdit_Effects.json": {
        "nodes": [
            {"handle": "edit", "type": "MuAPIVideoEdit", "widgets": {
                "model": "video-effects",
                "prompt": "Apply a vintage film grain and warm color grade",
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "vfx",
            }},
        ],
        "links": [],
    },

    "MuAPI_Lipsync_Sync.json": {
        "nodes": [
            {"handle": "lip", "type": "MuAPILipsync", "widgets": {
                "model": "sync-lipsync",
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "lipsync",
            }},
        ],
        "links": [],
    },

    "MuAPI_Audio_Suno.json": {
        "nodes": [
            {"handle": "audio", "type": "MuAPIAudio", "widgets": {
                "model": "suno-create-music",
                "prompt": "Upbeat indie pop with bright synths and a catchy chorus",
            }},
        ],
        "links": [],
    },

    "MuAPI_Generic_RawJSON.json": {
        "nodes": [
            {"handle": "img", "type": "LoadImage"},
            {"handle": "gen", "type": "MuAPIGenerate", "widgets": {
                "endpoint": "ai-image-face-swap",
                "payload_json": json.dumps({
                    "image_url": "__file_1__",
                    "swap_url": "__file_2__",
                    "target_index": 0
                }, indent=2),
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [
            ("img", 0, "gen", 0),
            ("gen", 1, "preview", 0),
        ],
    },

    "MuAPI_Chain_T2I_to_I2V.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "flux-2-pro",
                "prompt": "Hero portrait of a knight in glowing armor, cinematic key light",
                "aspect_ratio": "9:16",
            }},
            {"handle": "i2v", "type": "MuAPIImageToVideo", "widgets": {
                "model": "veo3.1-image-to-video",
                "prompt": "The knight slowly raises their sword. Cinematic camera dolly-in.",
                "aspect_ratio": "9:16", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "t2i_to_i2v",
            }},
        ],
        "links": [("t2i", 0, "i2v", 0)],
    },

    "MuAPI_Chain_I2I_then_Upscale.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "i2i", "type": "MuAPIImageToImage", "widgets": {
                "model": "flux-kontext-max-i2i",
                "prompt": "Convert to a watercolour painting on textured paper",
            }},
            {"handle": "up", "type": "MuAPIImageEnhance", "widgets": {
                "model": "topaz-image-upscale",
                "extra_params_json": '{"scale": 2}',
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "watercolour_4k"}},
        ],
        "links": [
            ("load", 0, "i2i", 0),
            ("i2i", 0, "up", 0),
            ("up", 0, "save", 0),
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # Skill-based workflows — mirror the agent skills under
    # muapiapp/skills/library/ (visual, motion, social, edit).
    # Each example wires the exact endpoint(s) the skill uses, so dragging
    # the JSON onto ComfyUI gives you a working starting point.
    # ──────────────────────────────────────────────────────────────────────────

    # ── Visual / image-only skills ────────────────────────────────────────────

    "MuAPI_Skill_NanoBanana.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-pro",
                "prompt": NANO_REASONING_BRIEF,
                "aspect_ratio": "1:1",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("t2i", 0, "preview", 0)],
    },

    "MuAPI_Skill_NanoBanana2.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-2",
                "prompt": "Reasoning brief: a stoic robot barista with exposed copper wiring, "
                          "pouring a latte art leaf with mechanical precision, inside a neon-lit "
                          "cyberpunk cafe at midnight, 85mm lens, f/1.8, volumetric blue rim light.",
                "aspect_ratio": "3:2",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("t2i", 0, "preview", 0)],
    },

    "MuAPI_Skill_LogoGenerator.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "flux-2-pro",
                "prompt": "Minimalist geometric logo for a tech startup named 'NORTH'. "
                          "Single solid color, flat design, isolated on white, perfectly centered, "
                          "negative space hides an upward arrow. Vector style.",
                "aspect_ratio": "1:1",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("t2i", 0, "preview", 0)],
    },

    "MuAPI_Skill_LogoBranding_Ideogram.json": {
        "nodes": [
            {"handle": "logo", "type": "MuAPITextToImage", "widgets": {
                "model": "ideogram-v3-t2i",
                "prompt": "Wordmark logo reading 'AURORA' in clean geometric sans-serif. "
                          "Monochromatic deep navy, flat vector, isolated on pure white, centered.",
                "aspect_ratio": "1:1",
            }},
            {"handle": "monogram", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-pro",
                "prompt": "Monogram of the letter 'A' as a geometric lockup, single color, "
                          "flat vector, isolated white background, centered, scalable.",
                "aspect_ratio": "1:1",
            }},
            {"handle": "save1", "type": "SaveImage", "widgets": {"filename_prefix": "logo_primary"}},
            {"handle": "save2", "type": "SaveImage", "widgets": {"filename_prefix": "logo_monogram"}},
        ],
        "links": [("logo", 0, "save1", 0), ("monogram", 0, "save2", 0)],
    },

    "MuAPI_Skill_YouTubeThumbnail.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "gpt-image-2-text-to-image",
                "prompt": "YouTube thumbnail, 16:9, bold expressive face on the left looking "
                          "shocked, large readable text on the right reading \"INSANE RESULT!\" in "
                          "thick yellow outlined sans, dark vignetted background, high contrast.",
                "aspect_ratio": "16:9",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("t2i", 0, "preview", 0)],
    },

    "MuAPI_Skill_BlogHeader.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "gpt-image-2-text-to-image",
                "prompt": "Professional blog header image, 1200x628, abstract illustration of "
                          "data flowing through circuits, deep blue and electric purple palette, "
                          "modern flat design with subtle gradients, plenty of negative space.",
                "aspect_ratio": "16:9",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "blog_header"}},
        ],
        "links": [("t2i", 0, "save", 0)],
    },

    "MuAPI_Skill_InstagramPost.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-2",
                "prompt": "Aesthetic Instagram post, square 1:1, flat lay of ceramic coffee cup, "
                          "fresh croissant, and an open notebook on a beige linen background, "
                          "warm morning light from the upper-left, leave breathing room for caption.",
                "aspect_ratio": "1:1",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "ig_post"}},
        ],
        "links": [("t2i", 0, "save", 0)],
    },

    "MuAPI_Skill_RedNoteCover.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "bytedance-seedream-v4.5",
                "prompt": "Xiaohongshu/RedNote cover, 3:4 portrait, vibrant lifestyle aesthetic, "
                          "girl holding a matcha drink, soft pastel palette, bold Chinese-style "
                          "title block at the top with crisp hand-drawn typography.",
                "aspect_ratio": "3:4",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "rednote"}},
        ],
        "links": [("t2i", 0, "save", 0)],
    },

    "MuAPI_Skill_KeyboardArt.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "ideogram-v3-t2i",
                "prompt": "Top-down photograph of pristine mechanical-keyboard keycaps arranged "
                          "to spell \"HELLO WORLD\" centered on a clean wooden desk, soft natural "
                          "light, precisely aligned, real keycap legends.",
                "aspect_ratio": "16:9",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("t2i", 0, "preview", 0)],
    },

    "MuAPI_Skill_AdCreative.json": {
        "nodes": [
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-pro",
                "prompt": "High-converting ad creative, 4:5 portrait, product hero of a "
                          "premium skincare bottle on glossy marble, dewdrops, soft natural "
                          "highlight, headline space reserved at the top reading \"GLOW DAILY\".",
                "aspect_ratio": "4:5",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "ad_creative"}},
        ],
        "links": [("t2i", 0, "save", 0)],
    },

    "MuAPI_Skill_BrandKit.json": {
        "nodes": [
            {"handle": "logo", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-pro",
                "prompt": "Logo concept for 'LUMEN' — minimalist sun + arc mark, single color, "
                          "vector flat, isolated on white, centered.",
                "aspect_ratio": "1:1",
            }},
            {"handle": "palette", "type": "MuAPITextToImage", "widgets": {
                "model": "gpt-image-2-text-to-image",
                "prompt": "Brand color palette moodboard, 5 swatch chips horizontally, hex codes "
                          "under each, premium magazine style, soft paper texture.",
                "aspect_ratio": "16:9",
            }},
            {"handle": "type", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-pro",
                "prompt": "Typography pairing sheet — large display sans-serif heading 'LUMEN', "
                          "elegant serif subheading beneath, on cream paper, editorial layout.",
                "aspect_ratio": "4:3",
            }},
            {"handle": "save1", "type": "SaveImage", "widgets": {"filename_prefix": "brand_logo"}},
            {"handle": "save2", "type": "SaveImage", "widgets": {"filename_prefix": "brand_palette"}},
            {"handle": "save3", "type": "SaveImage", "widgets": {"filename_prefix": "brand_type"}},
        ],
        "links": [
            ("logo", 0, "save1", 0),
            ("palette", 0, "save2", 0),
            ("type", 0, "save3", 0),
        ],
    },

    "MuAPI_Skill_Storyboard.json": {
        "nodes": [
            {"handle": "k1", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-2",
                "prompt": "Storyboard frame 1: wide establishing shot of a futuristic city at "
                          "sunrise, golden glow, cinematic 2.39:1 letterbox feel.",
                "aspect_ratio": "16:9",
            }},
            {"handle": "k2", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-2",
                "prompt": "Storyboard frame 2: medium shot, lone hero in long coat walking "
                          "down empty street, neon reflections, same city, same time of day.",
                "aspect_ratio": "16:9",
            }},
            {"handle": "k3", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-2",
                "prompt": "Storyboard frame 3: close-up of the same hero, determined expression, "
                          "warm key light from the left, neon bokeh background.",
                "aspect_ratio": "16:9",
            }},
            {"handle": "s1", "type": "SaveImage", "widgets": {"filename_prefix": "sb_01"}},
            {"handle": "s2", "type": "SaveImage", "widgets": {"filename_prefix": "sb_02"}},
            {"handle": "s3", "type": "SaveImage", "widgets": {"filename_prefix": "sb_03"}},
        ],
        "links": [("k1", 0, "s1", 0), ("k2", 0, "s2", 0), ("k3", 0, "s3", 0)],
    },

    "MuAPI_Skill_AmazonListing.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "hero", "type": "MuAPIImageEnhance", "widgets": {
                "model": "ai-product-shot",
                "extra_params_json": '{"prompt": "Pure white seamless background, soft studio key, '
                                     'gentle floor shadow, centered, e-commerce hero shot"}',
            }},
            {"handle": "lifestyle", "type": "MuAPIImageEnhance", "widgets": {
                "model": "ai-product-photography",
                "extra_params_json": '{"prompt": "Lifestyle context — product on a marble kitchen '
                                     'counter, morning light from window, soft natural shadow"}',
            }},
            {"handle": "save1", "type": "SaveImage", "widgets": {"filename_prefix": "amazon_hero"}},
            {"handle": "save2", "type": "SaveImage", "widgets": {"filename_prefix": "amazon_lifestyle"}},
        ],
        "links": [
            ("load", 0, "hero", 0),
            ("load", 0, "lifestyle", 0),
            ("hero", 0, "save1", 0),
            ("lifestyle", 0, "save2", 0),
        ],
    },

    "MuAPI_Skill_MultiAngleShots.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "front", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Re-render the exact same product from a straight-on front view, "
                          "white seamless background, soft studio light.",
            }},
            {"handle": "side", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Re-render the exact same product from a 90° side profile view, "
                          "white seamless background, same lighting.",
            }},
            {"handle": "top", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Re-render the exact same product from a top-down bird's-eye view, "
                          "white seamless background, same lighting.",
            }},
            {"handle": "s1", "type": "SaveImage", "widgets": {"filename_prefix": "angle_front"}},
            {"handle": "s2", "type": "SaveImage", "widgets": {"filename_prefix": "angle_side"}},
            {"handle": "s3", "type": "SaveImage", "widgets": {"filename_prefix": "angle_top"}},
        ],
        "links": [
            ("load", 0, "front", 0), ("load", 0, "side", 0), ("load", 0, "top", 0),
            ("front", 0, "s1", 0), ("side", 0, "s2", 0), ("top", 0, "s3", 0),
        ],
    },

    "MuAPI_Skill_MultiAngleReshoot.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "fish", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-pro-edit",
                "prompt": "Re-render the same scene with a fish-eye lens, dramatic curvature, "
                          "preserve subject identity exactly.",
            }},
            {"handle": "low", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-pro-edit",
                "prompt": "Re-render the same scene from a low-angle hero shot, looking up, "
                          "subject identity preserved.",
            }},
            {"handle": "preview1", "type": "PreviewImage"},
            {"handle": "preview2", "type": "PreviewImage"},
        ],
        "links": [
            ("load", 0, "fish", 0), ("load", 0, "low", 0),
            ("fish", 0, "preview1", 0), ("low", 0, "preview2", 0),
        ],
    },

    "MuAPI_Skill_PhotoPackGenerator.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "pack", "type": "MuAPIImageToImage", "widgets": {
                "model": "photo-pack",
                "extra_params_json": '{"category": "linkedin"}',
                "prompt": "Generate a professional LinkedIn-style headshot pack. "
                          "Preserve the exact facial identity from the reference image. "
                          "Do not modify eye shape, nose, jawline, cheekbones, or face proportions.",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "photo_pack"}},
        ],
        "links": [("load", 0, "pack", 0), ("pack", 0, "save", 0)],
    },

    "MuAPI_Skill_ActionFigure.json": {
        "nodes": [
            {"handle": "load", "type": "LoadImage"},
            {"handle": "i2i", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Convert the person in the reference image into a 6-inch collectible "
                          "action figure on a blister-pack card with logo and tagline. Preserve "
                          "the face exactly. Studio product-shot lighting.",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "action_figure"}},
        ],
        "links": [("load", 0, "i2i", 0), ("i2i", 0, "save", 0)],
    },

    "MuAPI_Skill_FashionTryOn.json": {
        "nodes": [
            {"handle": "person", "type": "LoadImage"},
            {"handle": "outfit", "type": "LoadImage"},
            {"handle": "tryon", "type": "MuAPIImageToImage", "widgets": {
                "model": "qwen-image-edit-plus",
                "prompt": "Dress the person in @image1 with the outfit shown in @image2. "
                          "Preserve identity and pose. Natural fit and folds, realistic shadows.",
            }},
            {"handle": "animate", "type": "MuAPIImageToVideo", "widgets": {
                "model": "seedance-v1.5-pro-i2v",
                "prompt": "The model takes one elegant turn revealing the outfit. Studio runway feel.",
                "aspect_ratio": "9:16", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "fashion_tryon",
            }},
        ],
        "links": [
            ("person", 0, "tryon", 0),
            ("tryon", 0, "animate", 0),
        ],
    },

    "MuAPI_Skill_UGCLifestyleTryOn.json": {
        "nodes": [
            {"handle": "person", "type": "LoadImage"},
            {"handle": "edit", "type": "MuAPIImageToImage", "widgets": {
                "model": "ai-dress-change",
                "prompt": "Dress the subject in a casual streetwear outfit (cream knit sweater, "
                          "dark wide-leg jeans). Preserve identity exactly.",
            }},
            {"handle": "i2v", "type": "MuAPIImageToVideo", "widgets": {
                "model": "kling-v3.0-pro-image-to-video",
                "prompt": "Natural UGC lifestyle clip. Subject smiles at the camera and "
                          "casually adjusts the sleeve. Soft handheld feel.",
                "aspect_ratio": "9:16", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "ugc_tryon",
            }},
        ],
        "links": [
            ("person", 0, "edit", 0),
            ("edit", 0, "i2v", 0),
        ],
    },

    "MuAPI_Skill_SelfieWithCelebrity.json": {
        "nodes": [
            {"handle": "user", "type": "LoadImage"},
            {"handle": "celeb", "type": "LoadImage"},
            {"handle": "selfie", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Generate a realistic BTS selfie of the person in @image1 with the "
                          "person in @image2, arms-length camera angle, warm event lighting. "
                          "Preserve both facial identities exactly.",
            }},
            {"handle": "i2v", "type": "MuAPIImageToVideo", "widgets": {
                "model": "veo3.1-image-to-video",
                "prompt": "Both subjects laugh and turn slightly toward each other. "
                          "Subtle handheld motion.",
                "aspect_ratio": "9:16", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "celeb_selfie",
            }},
        ],
        "links": [
            ("user", 0, "selfie", 0),
            ("selfie", 0, "i2v", 0),
        ],
    },

    "MuAPI_Skill_FloorPlanRendering.json": {
        "nodes": [
            {"handle": "plan", "type": "LoadImage"},
            {"handle": "render", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Convert the 2D floor plan in @image1 into a realistic 3D isometric "
                          "architectural rendering with furniture, plants, and warm interior light.",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "floor_3d"}},
        ],
        "links": [("plan", 0, "render", 0), ("render", 0, "save", 0)],
    },

    "MuAPI_Skill_InteriorDesign.json": {
        "nodes": [
            {"handle": "room", "type": "LoadImage"},
            {"handle": "redesign", "type": "MuAPIImageToImage", "widgets": {
                "model": "flux-kontext-pro-i2i",
                "prompt": "Redesign this room in Japandi style — light oak floor, off-white walls, "
                          "low linen sofa, large floor lamp, indoor plant. Keep the geometry.",
            }},
            {"handle": "i2v", "type": "MuAPIImageToVideo", "widgets": {
                "model": "kling-v3.0-pro-image-to-video",
                "prompt": "Slow architectural dolly through the redesigned space. Soft daylight.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "interior",
            }},
        ],
        "links": [("room", 0, "redesign", 0), ("redesign", 0, "i2v", 0)],
    },

    "MuAPI_Skill_InteriorVisualizer.json": {
        "nodes": [
            {"handle": "empty", "type": "MuAPITextToImage", "widgets": {
                "model": "gpt-image-2-text-to-image",
                "prompt": "Empty modern living room, large window with soft morning light, "
                          "matte beige walls, light oak parquet floor, photo-realistic.",
                "aspect_ratio": "16:9",
            }},
            {"handle": "furnish", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Furnish this room: low linen sofa, oak coffee table, soft rug, "
                          "indoor plant, floor lamp, framed art on the wall. Preserve geometry.",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "interior_viz"}},
        ],
        "links": [
            ("empty", 0, "furnish", 0),
            ("furnish", 0, "save", 0),
        ],
    },

    "MuAPI_Skill_CoupleGrid.json": {
        "nodes": [
            {"handle": "ref", "type": "LoadImage"},
            {"handle": "grid", "type": "MuAPIImageToImage", "widgets": {
                "model": "qwen-image-edit-plus",
                "prompt": "Create a 6-cell grid (2 rows × 3 cols) of the couple in @image1 in "
                          "six romantic poses and outfits. Preserve both identities exactly. "
                          "Consistent style across cells.",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "couple_grid"}},
        ],
        "links": [("ref", 0, "grid", 0), ("grid", 0, "save", 0)],
    },

    "MuAPI_Skill_Brochure.json": {
        "nodes": [
            {"handle": "cover", "type": "MuAPITextToImage", "widgets": {
                "model": "bytedance-seedream-v4.5",
                "prompt": "Brochure cover for a coastal real-estate brand — large hero photo of "
                          "an ocean villa at sunset, brand name 'AZURE STAYS' set in elegant serif "
                          "at the bottom, premium magazine layout.",
                "aspect_ratio": "3:4",
            }},
            {"handle": "spread", "type": "MuAPITextToImage", "widgets": {
                "model": "bytedance-seedream-v4.5",
                "prompt": "Brochure inner spread (landscape), two pages, left page: full-bleed "
                          "lifestyle photo. Right page: paragraph copy block, headline, three "
                          "small spot photos. Same brand palette.",
                "aspect_ratio": "16:9",
            }},
            {"handle": "save1", "type": "SaveImage", "widgets": {"filename_prefix": "brochure_cover"}},
            {"handle": "save2", "type": "SaveImage", "widgets": {"filename_prefix": "brochure_spread"}},
        ],
        "links": [("cover", 0, "save1", 0), ("spread", 0, "save2", 0)],
    },

    "MuAPI_Skill_UrlToDesign.json": {
        "nodes": [
            {"handle": "screenshot", "type": "LoadImage"},
            {"handle": "redesign", "type": "MuAPIImageToImage", "widgets": {
                "model": "gpt4o-edit",
                "prompt": "Redesign this website screenshot with modern UI: cleaner hierarchy, "
                          "8pt spacing, generous whitespace, modern type, vibrant accent color.",
            }},
            {"handle": "save", "type": "SaveImage", "widgets": {"filename_prefix": "url_redesign"}},
        ],
        "links": [("screenshot", 0, "redesign", 0), ("redesign", 0, "save", 0)],
    },

    "MuAPI_Skill_DesignGuide.json": {
        "nodes": [
            {"handle": "g1", "type": "MuAPITextToImage", "widgets": {
                "model": "gpt-image-2-text-to-image",
                "prompt": "Page 1: color palette page — 5 large swatches with hex codes and names, "
                          "premium design-system layout.",
                "aspect_ratio": "3:2",
            }},
            {"handle": "g2", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-pro",
                "prompt": "Page 2: typography pairings — H1/H2/H3 + body samples, two type "
                          "families displayed side-by-side, editorial layout.",
                "aspect_ratio": "3:2",
            }},
            {"handle": "g3", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-pro",
                "prompt": "Page 3: UI component preview — buttons, input fields, cards, navbar, "
                          "all on a soft neutral background.",
                "aspect_ratio": "3:2",
            }},
            {"handle": "s1", "type": "SaveImage", "widgets": {"filename_prefix": "guide_palette"}},
            {"handle": "s2", "type": "SaveImage", "widgets": {"filename_prefix": "guide_type"}},
            {"handle": "s3", "type": "SaveImage", "widgets": {"filename_prefix": "guide_components"}},
        ],
        "links": [("g1", 0, "s1", 0), ("g2", 0, "s2", 0), ("g3", 0, "s3", 0)],
    },

    "MuAPI_Skill_SocialPack.json": {
        "nodes": [
            {"handle": "hero", "type": "LoadImage"},
            {"handle": "ig", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Reframe to 1:1 Instagram square, preserve subject and brand layout, "
                          "extend the background naturally.",
            }},
            {"handle": "tt", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Reframe to 9:16 TikTok vertical, preserve subject, extend background.",
            }},
            {"handle": "tw", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Reframe to 16:9 Twitter/X landscape, preserve subject, extend background.",
            }},
            {"handle": "s1", "type": "SaveImage", "widgets": {"filename_prefix": "social_ig"}},
            {"handle": "s2", "type": "SaveImage", "widgets": {"filename_prefix": "social_tt"}},
            {"handle": "s3", "type": "SaveImage", "widgets": {"filename_prefix": "social_tw"}},
        ],
        "links": [
            ("hero", 0, "ig", 0), ("hero", 0, "tt", 0), ("hero", 0, "tw", 0),
            ("ig", 0, "s1", 0), ("tt", 0, "s2", 0), ("tw", 0, "s3", 0),
        ],
    },

    # ── Motion / video skills ─────────────────────────────────────────────────

    "MuAPI_Skill_Seedance2_T2V.json": {
        "nodes": [
            {"handle": "t2v", "type": "MuAPITextToVideo", "widgets": {
                "model": "seedance-2-text-to-video",
                "prompt": "Aerial drone push-in over a moonlit desert canyon. Subject: lone "
                          "figure on the cliff edge. Lens: 24mm. Move: low-altitude orbital. "
                          "Lighting: silver moon key, warm fill from torch.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "seedance2_t2v",
            }},
        ],
        "links": [],
    },

    "MuAPI_Skill_Seedance2_OmniReference.json": {
        "nodes": [
            {"handle": "img1", "type": "LoadImage"},
            {"handle": "img2", "type": "LoadImage"},
            {"handle": "img3", "type": "LoadImage"},
            {"handle": "omni", "type": "MuAPIImageToVideo", "widgets": {
                "model": "seedance-2.0-omni-reference",
                "prompt": "Combine character from @image1, prop from @image2, setting from "
                          "@image3 into a cinematic medium shot. Smooth dolly.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "seedance2_omni",
            }},
        ],
        "links": [
            ("img1", 0, "omni", 0),
            ("img2", 0, "omni", 1),
            ("img3", 0, "omni", 2),
        ],
    },

    "MuAPI_Skill_Seedance2_FirstLastFrame.json": {
        "nodes": [
            {"handle": "first", "type": "LoadImage"},
            {"handle": "last", "type": "LoadImage"},
            {"handle": "interp", "type": "MuAPIImageToVideo", "widgets": {
                "model": "seedance-2-first-last-frame",
                "prompt": "Smoothly interpolate between the two frames with naturalistic motion "
                          "and consistent lighting.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "first_last",
            }},
        ],
        "links": [
            ("first", 0, "interp", 0),
            ("last", 0, "interp", 1),
        ],
    },

    "MuAPI_Skill_CinemaDirector.json": {
        "nodes": [
            {"handle": "ref", "type": "LoadImage"},
            {"handle": "shot", "type": "MuAPIImageToVideo", "widgets": {
                "model": "kling-v3.0-pro-image-to-video",
                "prompt": "Director brief: Lens 35mm. Move: slow dolly-in. Subject holds gaze. "
                          "Lighting: warm key, cool rim. Atmosphere: rain mist particles.",
                "aspect_ratio": "21:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "cinema",
            }},
        ],
        "links": [("ref", 0, "shot", 0)],
    },

    "MuAPI_Skill_DroneStyleVideo.json": {
        "nodes": [
            {"handle": "t2v", "type": "MuAPITextToVideo", "widgets": {
                "model": "veo3.1-text-to-video",
                "prompt": "Aerial drone footage. Subject: turquoise coastline with cliffs. "
                          "Move: sweeping orbit at 80m altitude. Time: golden hour. "
                          "Lens: 24mm wide. Stabilized cinematic feel.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 8,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "drone",
            }},
        ],
        "links": [],
    },

    "MuAPI_Skill_OneShotVideo.json": {
        "nodes": [
            {"handle": "start", "type": "LoadImage"},
            {"handle": "shot", "type": "MuAPIImageToVideo", "widgets": {
                "model": "veo3.1-image-to-video",
                "prompt": "Continuous one-shot: camera glides through the doorway, follows "
                          "the subject down the corridor, ends on their face in close-up. "
                          "No cuts, no edits, single take.",
                "aspect_ratio": "21:9", "quality": "high", "duration": 8,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "oneshot",
            }},
        ],
        "links": [("start", 0, "shot", 0)],
    },

    "MuAPI_Skill_3DLogoAnimation.json": {
        "nodes": [
            {"handle": "logo2d", "type": "LoadImage"},
            {"handle": "logo3d", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Convert this flat 2D logo into a premium 3D version — beveled edges, "
                          "soft metallic shading, on a deep gradient background.",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "veo3.1-fast-image-to-video",
                "prompt": "The 3D logo rotates slowly, sweeping specular highlight passes "
                          "across the bevel. Premium product reveal feel.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "logo_3d",
            }},
        ],
        "links": [("logo2d", 0, "logo3d", 0), ("logo3d", 0, "anim", 0)],
    },

    "MuAPI_Skill_AnimalVideoGenerator.json": {
        "nodes": [
            {"handle": "vlogger", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-pro",
                "prompt": "Photorealistic anthropomorphic golden retriever in a hoodie, sitting "
                          "at a desk like a YouTube vlogger, ring light, microphone in front.",
                "aspect_ratio": "9:16",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "veo3.1-fast-image-to-video",
                "prompt": "The dog speaks expressively into the microphone, paws gesturing. "
                          "Subtle camera bob.",
                "aspect_ratio": "9:16", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "animal_vlog",
            }},
        ],
        "links": [("vlogger", 0, "anim", 0)],
    },

    "MuAPI_Skill_CartoonDance.json": {
        "nodes": [
            {"handle": "person", "type": "LoadImage"},
            {"handle": "toon", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Convert the person in @image1 into a Pixar-style 3D cartoon "
                          "character. Preserve identity cues (hair color, outfit). "
                          "Stylized but recognizable.",
            }},
            {"handle": "dance", "type": "MuAPIVideoEdit", "widgets": {
                "model": "kling-v2.6-std-motion-control",
                "prompt": "Apply lively dance motion to the character. Energetic and fluid.",
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "cartoon_dance",
            }},
        ],
        "links": [("person", 0, "toon", 0)],  # toon → motion-control wired via video_url widget
    },

    "MuAPI_Skill_CharacterStoryVideo.json": {
        "nodes": [
            {"handle": "char", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-pro",
                "prompt": "Establish the hero character: young explorer in worn leather jacket, "
                          "amber eyes, soft natural light. Reference sheet, neutral background.",
                "aspect_ratio": "1:1",
            }},
            {"handle": "scene1", "type": "MuAPIImageToImage", "widgets": {
                "model": "flux-kontext-pro-i2i",
                "prompt": "Place the same character in scene 1: standing at the edge of a "
                          "misty forest at dawn. Preserve identity exactly.",
            }},
            {"handle": "shot1", "type": "MuAPIImageToVideo", "widgets": {
                "model": "kling-v3.0-pro-image-to-video",
                "prompt": "Camera dollies forward as the character steps into the forest. "
                          "Cinematic, naturalistic motion.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "char_story",
            }},
        ],
        "links": [
            ("char", 0, "scene1", 0),
            ("scene1", 0, "shot1", 0),
        ],
    },

    "MuAPI_Skill_GiantProductShowcase.json": {
        "nodes": [
            {"handle": "product", "type": "LoadImage"},
            {"handle": "giant", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Re-render the product from @image1 at a colossal building-size scale, "
                          "placed in the middle of a busy city plaza, cinematic low-angle shot, "
                          "people for scale, dramatic light.",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "veo3.1-fast-image-to-video",
                "prompt": "Camera slowly rises tilting up to reveal the full giant product. "
                          "City sounds, crowd reactions.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "giant_product",
            }},
        ],
        "links": [("product", 0, "giant", 0), ("giant", 0, "anim", 0)],
    },

    "MuAPI_Skill_JewelryProductVideo.json": {
        "nodes": [
            {"handle": "ring", "type": "LoadImage"},
            {"handle": "studio", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2-edit",
                "prompt": "Place the jewelry on black velvet, dramatic spotlight, macro studio "
                          "shot, hyper-detailed.",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "grok-imagine-image-to-video",
                "prompt": "Slow macro orbit around the jewel, light catches each facet, "
                          "luxury commercial feel.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "jewelry",
            }},
        ],
        "links": [("ring", 0, "studio", 0), ("studio", 0, "anim", 0)],
    },

    "MuAPI_Skill_MusicVideo.json": {
        "nodes": [
            {"handle": "kf1", "type": "MuAPITextToImage", "widgets": {
                "model": "nano-banana-pro",
                "prompt": "Music video keyframe 1: synthwave city skyline at night, neon "
                          "horizon, lone figure on rooftop.",
                "aspect_ratio": "16:9",
            }},
            {"handle": "shot1", "type": "MuAPIImageToVideo", "widgets": {
                "model": "veo3.1-image-to-video",
                "prompt": "Slow camera dolly toward the figure as neon lights pulse with the beat.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "audio", "type": "MuAPIAudio", "widgets": {
                "model": "suno-create-music",
                "prompt": "Retro synthwave instrumental, 80 BPM, lush analog pads, driving "
                          "arpeggio, cinematic build.",
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "music_video",
            }},
        ],
        "links": [("kf1", 0, "shot1", 0)],
    },

    "MuAPI_Skill_ProductAdCinematic.json": {
        "nodes": [
            {"handle": "shot", "type": "LoadImage"},
            {"handle": "hero", "type": "MuAPIImageToImage", "widgets": {
                "model": "nano-banana-2",
                "prompt": "Cinematic product hero shot — marble surface, sweeping volumetric "
                          "light, depth-of-field background, premium commercial look.",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "kling-v3.0-standard-image-to-video",
                "prompt": "Cinematic 8s product ad: slow rotate revealing the silhouette, "
                          "dramatic backlight bloom, dust particles drifting.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 8,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "product_ad",
            }},
        ],
        "links": [("shot", 0, "hero", 0), ("hero", 0, "anim", 0)],
    },

    "MuAPI_Skill_ProductShowcaseVideo.json": {
        "nodes": [
            {"handle": "product", "type": "LoadImage"},
            {"handle": "edit", "type": "MuAPIImageToImage", "widgets": {
                "model": "bytedance-seedream-v4.5-edit",
                "prompt": "Surround the product with an explosive splash of its key ingredients "
                          "frozen mid-air. High-end commercial macro.",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "seedance-v1.5-pro-i2v-fast",
                "prompt": "Macro motion: ingredients orbit the product, ending on a centered "
                          "hero shot.",
                "aspect_ratio": "9:16", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "product_showcase",
            }},
        ],
        "links": [("product", 0, "edit", 0), ("edit", 0, "anim", 0)],
    },

    "MuAPI_Skill_ProductVideoAdMaker.json": {
        "nodes": [
            {"handle": "product", "type": "LoadImage"},
            {"handle": "edit", "type": "MuAPIImageToImage", "widgets": {
                "model": "flux-2-pro-edit",
                "prompt": "Re-render the product on a polished black surface with theatrical "
                          "rim light. Studio commercial feel.",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "wan2.5-image-to-video",
                "prompt": "High-end ad shot: slow camera arc around the product, soft particle "
                          "drift, premium commercial tone.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "product_video_ad",
            }},
        ],
        "links": [("product", 0, "edit", 0), ("edit", 0, "anim", 0)],
    },

    "MuAPI_Skill_TalkingBabyVideo.json": {
        "nodes": [
            {"handle": "baby", "type": "MuAPITextToImage", "widgets": {
                "model": "wan2.5-text-to-image",
                "prompt": "Photorealistic 1-year-old baby wearing a tiny astronaut costume, "
                          "studio backdrop, dramatic key light. Family-friendly.",
                "aspect_ratio": "9:16",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "grok-imagine-image-to-video",
                "prompt": "The baby grins and speaks expressively to the camera, hands moving "
                          "in cute gestures. Soft handheld feel.",
                "aspect_ratio": "9:16", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "talking_baby",
            }},
        ],
        "links": [("baby", 0, "anim", 0)],
    },

    "MuAPI_Skill_AiFightScene.json": {
        "nodes": [
            {"handle": "board", "type": "MuAPITextToImage", "widgets": {
                "model": "gpt-image-2-text-to-image",
                "prompt": "16-cell storyboard grid (4×4) of an action scene: two warriors duel "
                          "across a rainy rooftop, each cell a unique cut — dodge, slash, parry, "
                          "kick, fall, recover. High-density frame design.",
                "aspect_ratio": "1:1",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "seedance-v2.0-i2v",
                "prompt": "Animate the storyboard into a high-cut-density fight sequence, "
                          "rapid action, motion blur, impact frames.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "fight_scene",
            }},
        ],
        "links": [("board", 0, "anim", 0)],
    },

    "MuAPI_Skill_FreezeEffectVideo.json": {
        "nodes": [
            {"handle": "photo", "type": "LoadImage"},
            {"handle": "freeze", "type": "MuAPIImageToVideo", "widgets": {
                "model": "seedance-v2.0-i2v",
                "prompt": "Ultra-realistic, shot on Arri Alexa Mini, 35mm lens, moody sports "
                          "bar interior with neon accents, volumetric haze, shallow DOF. "
                          "The person from @image1 walks confidently through a packed crowd "
                          "and snaps their fingers — a spherical shockwave ripples outward and "
                          "everything freezes mid-motion: golden arcs of beer suspended in air, "
                          "popcorn floating, people locked mid-cheer. Only the subject moves, "
                          "tracking backward through the frozen scene, plucks a kernel from "
                          "midair, whispers 'perfect', then snaps again — a reverse shockwave "
                          "resumes motion and the celebration explodes back to life. "
                          "Sound: cheer → snap → bass drop → silence → footsteps → snap → cheer.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 15,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "freeze_effect",
            }},
        ],
        "links": [("photo", 0, "freeze", 0)],
    },

    "MuAPI_Skill_UGCAdsWorkflow.json": {
        "nodes": [
            {"handle": "scene", "type": "MuAPITextToImage", "widgets": {
                "model": "gpt-image-2-text-to-image",
                "prompt": "Authentic UGC selfie scene — young woman in cozy kitchen holding a "
                          "branded snack bar, natural window light, slightly imperfect framing.",
                "aspect_ratio": "9:16",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "veo3.1-image-to-video",
                "prompt": "Subject takes a bite, reacts with genuine delight, talks to camera "
                          "for a beat. Handheld feel.",
                "aspect_ratio": "9:16", "quality": "high", "duration": 8,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "ugc_ad",
            }},
        ],
        "links": [("scene", 0, "anim", 0)],
    },

    "MuAPI_Skill_SocialMediaVideo.json": {
        "nodes": [
            {"handle": "hero", "type": "MuAPITextToImage", "widgets": {
                "model": "google-imagen4-ultra",
                "prompt": "Brand-aware social hero frame, vertical 9:16, energetic and "
                          "on-brand for a wellness app — sunrise yoga silhouette over ocean.",
                "aspect_ratio": "9:16",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "veo3.1-image-to-video",
                "prompt": "Subtle parallax push-in, waves move, sun rises slightly. "
                          "Calm pacing for social.",
                "aspect_ratio": "9:16", "quality": "high", "duration": 5,
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "social_video",
            }},
        ],
        "links": [("hero", 0, "anim", 0)],
    },

    "MuAPI_Skill_AiClipping.json": {
        "nodes": [
            {"handle": "clip", "type": "MuAPIVideoEdit", "widgets": {
                "model": "ai-clipping",
                "prompt": "Detect the most viral 9:16 moments from this long video — "
                          "hooks, punchlines, peak emotion. Auto-crop vertical.",
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "shorts",
            }},
        ],
        "links": [],
    },

    "MuAPI_Skill_YoutubeShorts.json": {
        "nodes": [
            {"handle": "clip", "type": "MuAPIVideoEdit", "widgets": {
                "model": "ai-clipping",
                "extra_params_json": '{"num_clips": 5, "min_duration": 15, "max_duration": 60}',
                "prompt": "Generate 5 viral 9:16 YouTube Shorts from this long-form video. "
                          "Each clip: tight hook, single payoff, vertical auto-crop.",
            }},
            {"handle": "save", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "yt_shorts",
            }},
        ],
        "links": [],
    },

    "MuAPI_Skill_ProductCampaign.json": {
        "nodes": [
            {"handle": "product", "type": "LoadImage"},
            {"handle": "hero", "type": "MuAPIImageEnhance", "widgets": {
                "model": "ai-product-shot",
                "extra_params_json": '{"prompt": "Premium hero shot, white seamless, soft '
                                     'studio light, gentle floor shadow"}',
            }},
            {"handle": "lifestyle", "type": "MuAPIImageToImage", "widgets": {
                "model": "bytedance-seedream-v4.5-edit",
                "prompt": "Place the product in an aspirational lifestyle scene — modern "
                          "kitchen counter, morning sunlight, plants in soft focus background.",
            }},
            {"handle": "anim", "type": "MuAPIImageToVideo", "widgets": {
                "model": "kling-v3.0-pro-image-to-video",
                "prompt": "Slow cinematic dolly across the lifestyle scene, ending on the "
                          "product hero close-up.",
                "aspect_ratio": "16:9", "quality": "high", "duration": 5,
            }},
            {"handle": "save_hero", "type": "SaveImage", "widgets": {"filename_prefix": "campaign_hero"}},
            {"handle": "save_life", "type": "SaveImage", "widgets": {"filename_prefix": "campaign_lifestyle"}},
            {"handle": "save_vid", "type": "MuAPIVideoSaver", "widgets": {
                "save_subfolder": "muapi_videos", "filename_prefix": "campaign_video",
            }},
        ],
        "links": [
            ("product", 0, "hero", 0),
            ("product", 0, "lifestyle", 0),
            ("lifestyle", 0, "anim", 0),
            ("hero", 0, "save_hero", 0),
            ("lifestyle", 0, "save_life", 0),
        ],
    },

    # ── 3D skills ─────────────────────────────────────────────────────────────

    "MuAPI_Skill_ImageTo3D_Tripo.json": {
        "nodes": [
            {"handle": "ref", "type": "LoadImage"},
            {"handle": "to3d", "type": "MuAPIImageTo3D", "widgets": {
                "model": "tripo3d-p1-image-to-3d",
                "prompt": "",
                "extra_params_json": '{"texture": true, "face_limit": 30000}',
            }},
        ],
        "links": [("ref", 0, "to3d", 0)],
    },

    "MuAPI_Skill_TextTo3D_Meshy.json": {
        "nodes": [
            {"handle": "to3d", "type": "MuAPIImageTo3D", "widgets": {
                "model": "meshy-6-text-to-3d",
                "prompt": "A stylized treasure chest, low-poly, fantasy game-ready asset, "
                          "wood and brass, PBR textures.",
                "extra_params_json": '{"topology": "quad", "target_polycount": 30000, "enable_pbr": true}',
            }},
        ],
        "links": [],
    },

    "MuAPI_ApiKey_Hub.json": {
        # Standalone reference workflow showing the API Key node wired to a T2I.
        # In ComfyUI you'll need to right-click the T2I 'api_key' widget → 'Convert to input'
        # for the link to take effect; this file ships with that conversion already applied
        # via the inputs list.
        "nodes": [
            {"handle": "key", "type": "MuAPIApiKey", "widgets": {"api_key": ""}},
            {"handle": "t2i", "type": "MuAPITextToImage", "widgets": {
                "model": "flux-dev-image",
                "prompt": "Sunset over a desert canyon, ultra-wide cinematic shot",
                "aspect_ratio": "16:9",
            }},
            {"handle": "preview", "type": "PreviewImage"},
        ],
        "links": [("t2i", 0, "preview", 0)],
        # api_key wiring handled in post-process
        "post": "wire_api_key",
    },
}


def post_wire_api_key(graph):
    """Convert the api_key widget on the T2I node into an input wired from the API Key node."""
    key_node = next(n for n in graph["nodes"] if n["type"] == "MuAPIApiKey")
    t2i_node = next(n for n in graph["nodes"] if n["type"] == "MuAPITextToImage")

    # Find api_key widget index for T2I.
    widget_names = WIDGETS["MuAPITextToImage"]
    ak_idx = widget_names.index("api_key")

    # Add as input with widget reference.
    graph["last_link_id"] += 1
    lid = graph["last_link_id"]
    new_input = {"name": "api_key", "type": "STRING", "link": lid,
                 "widget": {"name": "api_key"}}
    t2i_node["inputs"].append(new_input)
    key_node["outputs"][0]["links"].append(lid)
    graph["links"].append([lid, key_node["id"], 0, t2i_node["id"],
                           len(t2i_node["inputs"]) - 1, "STRING"])
    # Blank the widget value (still keep the slot in widgets_values).
    t2i_node["widgets_values"][ak_idx] = ""


POST = {"wire_api_key": post_wire_api_key}


def main():
    written = []
    for name, spec in WORKFLOWS.items():
        graph = build(spec)
        if "post" in spec:
            POST[spec["post"]](graph)
        path = OUT_DIR / name
        path.write_text(json.dumps(graph, indent=2))
        written.append(name)
    print(f"Wrote {len(written)} workflows to {OUT_DIR}")
    for n in written:
        print(f"  - {n}")


if __name__ == "__main__":
    main()
