"""MuAPI Video Saver — downloads a video URL, saves to disk, returns frames."""

import os
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import requests
import torch

try:
    import folder_paths
except ImportError:
    class folder_paths:
        @staticmethod
        def get_output_directory():
            return os.path.join(os.path.expanduser("~"), "comfyui_output")


ALLOWED_VIDEO_HOSTS = frozenset({"cdn.muapi.ai"})


def _validate_video_url(video_url):
    """Return a safe MuAPI CDN URL or raise for untrusted input."""
    if not isinstance(video_url, str):
        raise ValueError("Invalid video URL")

    url = video_url.strip()
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid video URL") from exc

    if (
        parsed.scheme != "https"
        or hostname is None
        or hostname.lower() not in ALLOWED_VIDEO_HOSTS
        or port not in (None, 443)
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError("Video URL must be an HTTPS MuAPI CDN URL")
    return url


def _confined_output_dir(save_subfolder):
    """Resolve a user-selected subfolder without leaving ComfyUI's output directory."""
    if not isinstance(save_subfolder, str):
        raise ValueError("Save subfolder must be a relative path")

    output_root = Path(folder_paths.get_output_directory()).resolve(strict=False)
    requested_dir = (output_root / save_subfolder).resolve(strict=False)
    try:
        requested_dir.relative_to(output_root)
    except ValueError as exc:
        raise ValueError("Save subfolder must remain inside the output directory") from exc
    return output_root, requested_dir


def _validate_filename_prefix(filename_prefix):
    """Validate the filename component used for saved videos."""
    if not isinstance(filename_prefix, str):
        raise ValueError("Filename prefix must be a single filename component")

    prefix = filename_prefix.strip()
    if (
        not prefix
        or prefix in {".", ".."}
        or any(separator in prefix for separator in ("/", "\\", ":"))
        or any(ord(character) < 32 for character in prefix)
    ):
        raise ValueError("Filename prefix must be a single filename component")
    return prefix


class MuAPIVideoSaver:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "video_url": ("STRING", {"multiline": False, "default": ""}),
            "save_subfolder": ("STRING", {"default": "muapi_videos"}),
            "filename_prefix": ("STRING", {"default": "muapi"}),
        }, "optional": {
            "frame_load_cap": ("INT", {"default": 0, "min": 0, "max": 9999}),
            "skip_first_frames": ("INT", {"default": 0, "min": 0, "max": 500}),
            "select_every_nth": ("INT", {"default": 1, "min": 1, "max": 30}),
        }}
    RETURN_TYPES = ("IMAGE", "STRING", "INT")
    RETURN_NAMES = ("frames", "filepath", "frame_count")
    FUNCTION = "run"
    CATEGORY = "🎬 MuAPI"
    OUTPUT_NODE = True

    def run(self, video_url, save_subfolder, filename_prefix,
            frame_load_cap=0, skip_first_frames=0, select_every_nth=1):
        try:
            safe_url = _validate_video_url(video_url)
            output_root, out_dir = _confined_output_dir(save_subfolder)
            safe_prefix = _validate_filename_prefix(filename_prefix)
            os.makedirs(out_dir, exist_ok=True)
            n = 1
            fp = os.path.join(out_dir, f"{safe_prefix}_{n:05d}.mp4")
            while os.path.exists(fp):
                n += 1
                fp = os.path.join(out_dir, f"{safe_prefix}_{n:05d}.mp4")

            print(f"[MuAPI VideoSaver] Downloading {video_url[:80]}...")
            r = requests.get(
                safe_url,
                stream=True,
                timeout=300,
                allow_redirects=False,
            )
            if 300 <= r.status_code < 400:
                raise ValueError("MuAPI CDN redirects are not allowed")
            r.raise_for_status()
            with open(fp, "wb") as fh:
                for chunk in r.iter_content(8192):
                    if chunk:
                        fh.write(chunk)
            frames, count = self._load(fp, frame_load_cap, skip_first_frames, select_every_nth)
            fname = os.path.basename(fp)
            relative_subfolder = os.path.relpath(out_dir, output_root)
            preview = {
                "filename": fname,
                "subfolder": "" if relative_subfolder == "." else relative_subfolder,
                "type": "output",
                "format": "video/mp4",
            }
            print(f"[MuAPI VideoSaver] Saved {fname} — {count} frames")
            return {"ui": {"gifs": [preview]}, "result": (frames, fp, count)}
        except Exception as e:
            return self._err(str(e))

    def _load(self, path, cap, skip, nth):
        try:
            import cv2
            frames, raw, loaded = [], 0, 0
            vc = cv2.VideoCapture(path)
            while True:
                ret, frame = vc.read()
                if not ret:
                    break
                if raw < skip:
                    raw += 1
                    continue
                if (raw - skip) % nth == 0:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                    frames.append(rgb)
                    loaded += 1
                    if cap > 0 and loaded >= cap:
                        break
                raw += 1
            vc.release()
            if not frames:
                raise RuntimeError("No frames")
            return torch.from_numpy(np.stack(frames)), len(frames)
        except Exception as e:
            print(f"[MuAPI VideoSaver] frame load error: {e}")
            return torch.zeros(1, 64, 64, 3), 1

    def _err(self, msg):
        print(f"[MuAPI VideoSaver] ERROR: {msg}")
        return {"ui": {"text": [msg]}, "result": (torch.zeros(1, 64, 64, 3), "ERROR", 0)}


NODE_CLASS_MAPPINGS = {"MuAPIVideoSaver": MuAPIVideoSaver}
NODE_DISPLAY_NAME_MAPPINGS = {"MuAPIVideoSaver": "🎬 MuAPI Save Video"}
