import sys
import tempfile
import unittest
import os
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

if "torch" not in sys.modules:
    try:
        import torch  # noqa: F401
    except ModuleNotFoundError:
        torch_stub = ModuleType("torch")
        torch_stub.zeros = lambda *args, **kwargs: None
        sys.modules["torch"] = torch_stub

import muapi_nodes as nodes


class FakeResponse:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {"url": "https://cdn.muapi.ai/uploads/file"}


class MuAPIUploadSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.original_cwd = Path.cwd()
        os.chdir(self.root)
        self.input_dir = self.root / "input"
        self.output_dir = self.root / "output"
        self.input_dir.mkdir()
        self.output_dir.mkdir()
        self.folder_patches = (
            patch.object(
                nodes.folder_paths,
                "get_input_directory",
                return_value=str(self.input_dir),
            ),
            patch.object(
                nodes.folder_paths,
                "get_output_directory",
                return_value=str(self.output_dir),
            ),
        )
        for folder_patch in self.folder_patches:
            folder_patch.start()

    def tearDown(self):
        for folder_patch in reversed(self.folder_patches):
            folder_patch.stop()
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()

    def test_relative_input_and_output_paths_are_confined(self):
        input_file = self.input_dir / "clip.mp4"
        output_file = self.output_dir / "render.mp4"
        input_file.touch()
        output_file.touch()

        self.assertEqual(
            nodes._confined_upload_path("input/clip.mp4"), str(input_file.resolve())
        )
        self.assertEqual(
            nodes._confined_upload_path("output/render.mp4"), str(output_file.resolve())
        )

    def test_absolute_parent_and_symlink_escape_paths_are_rejected(self):
        outside_file = self.root / "secret.txt"
        outside_file.write_text("do not upload", encoding="utf-8")
        symlink = self.input_dir / "linked-secret.txt"
        symlink.symlink_to(outside_file)

        for unsafe_path in (
            str(outside_file),
            "../secret.txt",
            "input/../secret.txt",
            r"input\..\secret.txt",
            "input/linked-secret.txt",
        ):
            with self.subTest(unsafe_path=unsafe_path):
                with self.assertRaises(ValueError):
                    nodes._confined_upload_path(unsafe_path)

    def test_upload_file_confines_path_before_open_or_network(self):
        with patch.object(nodes.requests, "post") as post:
            with self.assertRaisesRegex(ValueError, "Upload path"):
                nodes._upload_file("test-key", "../secret.txt")
        post.assert_not_called()

    def test_upload_file_uses_confined_path_and_expected_mime(self):
        input_file = self.input_dir / "clip.mp3"
        input_file.write_bytes(b"audio")
        with patch.object(nodes.requests, "post", return_value=FakeResponse()) as post:
            result = nodes._upload_file("test-key", "input/clip.mp3")

        self.assertEqual(result, "https://cdn.muapi.ai/uploads/file")
        post.assert_called_once()
        upload = post.call_args.kwargs["files"]["file"]
        self.assertEqual(upload[0], "clip.mp3")
        self.assertEqual(upload[2], "audio/mpeg")

    def test_generic_node_rejects_unconfined_file_before_upload(self):
        with patch.object(nodes, "_upload_file") as upload:
            with self.assertRaises(ValueError):
                nodes.MuAPIGenerate().run(
                    "seedance-v2.0-t2v",
                    '{"image_url":"__file_path_1__"}',
                    api_key="test-key",
                    file_path_1="../secret.txt",
                )
        upload.assert_not_called()

    def test_image_to_video_rejects_unconfined_reference_before_upload(self):
        with patch.object(
            nodes, "_upload_image", return_value="https://cdn.muapi.ai/image"
        ):
            with patch.object(nodes, "_upload_file") as upload:
                with self.assertRaises(ValueError):
                    nodes.MuAPIImageToVideo().run(
                        "custom",
                        "prompt",
                        "16:9",
                        "basic",
                        5,
                        api_key="test-key",
                        image_1=object(),
                        custom_endpoint="kling-v3.0-omni-reference",
                        video_file_1="../secret.mp4",
                    )
        upload.assert_not_called()

    def test_lipsync_rejects_unconfined_audio_before_upload(self):
        with patch.object(nodes, "_upload_file") as upload:
            with self.assertRaises(ValueError):
                nodes.MuAPILipsync().run(
                    "sync-lipsync",
                    "https://cdn.muapi.ai/video.mp4",
                    "",
                    api_key="test-key",
                    audio_file_path="../secret.wav",
                )
        upload.assert_not_called()


if __name__ == "__main__":
    unittest.main()
