import unittest
import tempfile
import os
from embedid import core, manifest


class TestEmbedIDCore(unittest.TestCase):
    def setUp(self):
        self.meta = {
            "author": "James The Giblet",
            "tool": "EmbedID",
            "remix_of": "flux-engine-v2",
            "agent": "Copilot-M365",
            "timestamp": "2025-08-15T18:22:00Z"
        }
        self.comment_prefix = "#"
        self.test_file = tempfile.NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8")
        self.test_file.write("print('Hello world')\n")
        self.test_file.close()

    def tearDown(self):
        os.remove(self.test_file.name)
        manifest_path = self.test_file.name + ".embedid.json"
        if os.path.exists(manifest_path):
            os.remove(manifest_path)

    def test_scramble_and_descramble(self):
        wm_id, encoded = core.scramble_metadata(self.meta)
        decoded = core.descramble_metadata(encoded)
        self.assertEqual(decoded["author"], self.meta["author"])
        self.assertEqual(decoded["tool"], self.meta["tool"])

    def test_embed_and_extract_watermark(self):
        _, encoded = core.scramble_metadata(self.meta)
        success = core.embed_watermark(self.test_file.name, encoded, self.comment_prefix)
        self.assertTrue(success)
        extracted = core.extract_watermark(self.test_file.name, self.comment_prefix)
        self.assertEqual(extracted, encoded)

    def test_remove_watermark(self):
        _, encoded = core.scramble_metadata(self.meta)
        core.embed_watermark(self.test_file.name, encoded, self.comment_prefix)
        removed = core.remove_watermark(self.test_file.name, self.comment_prefix)
        self.assertTrue(removed)
        extracted = core.extract_watermark(self.test_file.name, self.comment_prefix)
        self.assertIsNone(extracted)

    def test_get_watermark_id(self):
        wm_id, encoded = core.scramble_metadata(self.meta)
        core.embed_watermark(self.test_file.name, encoded, self.comment_prefix)
        extracted_id = core.get_watermark_id(self.test_file.name, self.comment_prefix)
        self.assertEqual(extracted_id, wm_id)

    def test_manifest_write(self):
        wm_id, _ = core.scramble_metadata(self.meta)
        manifest.write_manifest(self.test_file.name, wm_id, "add", self.comment_prefix, self.meta)
        manifest_path = self.test_file.name + ".embedid.json"
        self.assertTrue(os.path.exists(manifest_path))
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = f.read()
            self.assertIn("EmbedID", data)
            self.assertIn("James The Giblet", data)

    def test_manifest_read_and_validate(self):
        wm_id, _ = core.scramble_metadata(self.meta)
        manifest.write_manifest(self.test_file.name, wm_id, "add", self.comment_prefix, self.meta)
        manifest_path = self.test_file.name + ".embedid.json"
        data = manifest.read_manifest(manifest_path)
        self.assertTrue(manifest.validate_manifest(data))
        self.assertEqual(data["id"], wm_id)
        self.assertEqual(data["metadata"]["author"], self.meta["author"])


if __name__ == "__main__":
    unittest.main()