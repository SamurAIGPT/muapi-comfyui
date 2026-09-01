import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

# Keep the security tests runnable in a lightweight checkout without ComfyUI's
# tensor runtime. The production node still imports the real torch package.
if "torch" not in sys.modules:
    try:
        import torch  # noqa: F401
    except ModuleNotFoundError:
        torch_stub = ModuleType("torch")
        torch_stub.zeros = lambda *args, **kwargs: None
        sys.modules["torch"] = torch_stub

import muapi_video_saver_node as saver


class FakeResponse:
    def __init__(self, status_code=200, headers=None, chunks=None):
        self.status_code = status_code
        self.headers = headers or {}
        self._chunks = chunks or [b"video"]

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size):
        return iter(self._chunks)


class MuAPIVideoSaverSecurityTests(unittest.TestCase):
    def test_output_subfolder_cannot_escape_output_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(saver.folder_paths, "get_output_directory", return_value=temp_dir):
                _, safe_dir = saver._confined_output_dir("nested/muapi")
                self.assertEqual(safe_dir, Path(temp_dir).resolve() / "nested/muapi")

                with self.assertRaisesRegex(ValueError, "inside the output directory"):
                    saver._confined_output_dir("../../outside")

    def test_filename_prefix_is_one_path_component(self):
        self.assertEqual(saver._validate_filename_prefix("  muapi  "), "muapi")
        for unsafe_prefix in ("../escape", "nested/name", r"nested\\name", "C:escape", ".."):
            with self.subTest(unsafe_prefix=unsafe_prefix):
                with self.assertRaises(ValueError):
                    saver._validate_filename_prefix(unsafe_prefix)

    def test_video_url_requires_the_muapi_cdn(self):
        self.assertEqual(
            saver._validate_video_url(" https://cdn.muapi.ai/outputs/video.mp4 "),
            "https://cdn.muapi.ai/outputs/video.mp4",
        )
        for unsafe_url in (
            "http://cdn.muapi.ai/outputs/video.mp4",
            "https://example.com/video.mp4",
            "https://cdn.muapi.ai.evil.example/video.mp4",
            "https://cdn.muapi.ai@evil.example/video.mp4",
        ):
            with self.subTest(unsafe_url=unsafe_url):
                with self.assertRaises(ValueError):
                    saver._validate_video_url(unsafe_url)

    def test_run_rejects_untrusted_url_before_network_request(self):
        with patch.object(saver.requests, "get") as get:
            result = saver.MuAPIVideoSaver().run(
                "https://example.com/video.mp4",
                "muapi_videos",
                "muapi",
            )

        get.assert_not_called()
        self.assertIn("HTTPS MuAPI CDN", result["ui"]["text"][0])

    def test_run_rejects_escape_subfolder_before_network_request(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(saver.folder_paths, "get_output_directory", return_value=temp_dir):
                with patch.object(saver.requests, "get") as get:
                    result = saver.MuAPIVideoSaver().run(
                        "https://cdn.muapi.ai/outputs/video.mp4",
                        "../../outside",
                        "muapi",
                    )

        get.assert_not_called()
        self.assertIn("inside the output directory", result["ui"]["text"][0])

    def test_run_disables_redirects_for_allowlisted_url(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            response = FakeResponse(status_code=302, headers={"Location": "https://evil.example/video.mp4"})
            with patch.object(saver.folder_paths, "get_output_directory", return_value=temp_dir):
                with patch.object(saver.requests, "get", return_value=response) as get:
                    result = saver.MuAPIVideoSaver().run(
                        "https://cdn.muapi.ai/outputs/video.mp4",
                        "muapi_videos",
                        "muapi",
                    )

        get.assert_called_once_with(
            "https://cdn.muapi.ai/outputs/video.mp4",
            stream=True,
            timeout=300,
            allow_redirects=False,
        )
        self.assertIn("redirects are not allowed", result["ui"]["text"][0])

    def test_run_saves_allowlisted_video_inside_output_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            response = FakeResponse()
            with patch.object(saver.folder_paths, "get_output_directory", return_value=temp_dir):
                with patch.object(saver.requests, "get", return_value=response) as get:
                    with patch.object(saver.MuAPIVideoSaver, "_load", return_value=("frames", 1)):
                        result = saver.MuAPIVideoSaver().run(
                            "https://cdn.muapi.ai/outputs/video.mp4",
                            "muapi_videos",
                            "muapi",
                        )

            saved_path = Path(result["result"][1])
            self.assertEqual(saved_path.parent, Path(temp_dir).resolve() / "muapi_videos")
            self.assertEqual(result["ui"]["gifs"][0]["subfolder"], "muapi_videos")
            self.assertTrue(saved_path.is_file())
            get.assert_called_once_with(
                "https://cdn.muapi.ai/outputs/video.mp4",
                stream=True,
                timeout=300,
                allow_redirects=False,
            )


if __name__ == "__main__":
    unittest.main()
