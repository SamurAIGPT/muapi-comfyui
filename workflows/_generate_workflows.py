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
