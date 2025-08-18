import argparse
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from embedid import cli, core


class TestEmbedIDCli(unittest.TestCase):
    def setUp(self):
        """Set up a temporary file for testing."""
        self.test_file = tempfile.NamedTemporaryFile(
            delete=False, mode="w+", encoding="utf-8", suffix=".py"
        )
        self.test_file.write("def hello():\n    print('Hello world')\n")
        self.test_file.close()
        self.comment_prefix = "#"

    def tearDown(self):
        """Clean up the temporary file and any manifest."""
        os.remove(self.test_file.name)
        manifest_path = self.test_file.name + ".embedid.json"
        if os.path.exists(manifest_path):
            os.remove(manifest_path)

    def test_cli_add_and_verify(self):
        """Test the 'add' and 'verify' commands via the CLI handler."""
        # Test Add
        add_args = argparse.Namespace(
            file=self.test_file.name,
            author="Test Author",
            tool="Test Tool",
            remix_of=None,
            agent=None,
            comment_prefix=self.comment_prefix,
        )

        f = io.StringIO()
        with redirect_stdout(f):
            cli.handle_add(add_args)
        output = f.getvalue()

        self.assertIn("[+] Watermark embedded", output)
        self.assertTrue(os.path.exists(self.test_file.name + ".embedid.json"))

        # Test Verify
        verify_args = argparse.Namespace(
            file=self.test_file.name,
            comment_prefix=self.comment_prefix,
            verbose=True,
            json=False,
        )

        f = io.StringIO()
        with redirect_stdout(f):
            cli.handle_verify(verify_args)
        output = f.getvalue()

        self.assertIn("[OK] Verified EmbedID", output)
        self.assertIn("author: Test Author", output)

    def test_cli_id_and_remove(self):
        """Test the 'id' and 'remove' commands via the CLI handler."""
        # Add a watermark first to test id and remove
        meta = {"author": "Test Author"}
        _, encoded = core.scramble_metadata(meta)
        core.embed_watermark(self.test_file.name, encoded, self.comment_prefix)

        # Test ID
        id_args = argparse.Namespace(file=self.test_file.name, comment_prefix=self.comment_prefix)
        f = io.StringIO()
        with redirect_stdout(f):
            cli.handle_id(id_args)
        self.assertIn("[ID]", f.getvalue())

        # Test Remove
        remove_args = argparse.Namespace(file=self.test_file.name, comment_prefix=self.comment_prefix)
        f = io.StringIO()
        with redirect_stdout(f):
            cli.handle_remove(remove_args)
        self.assertIn("[+] Watermark removed", f.getvalue())
        # Verify it's gone
        self.assertIsNone(core.extract_watermark(self.test_file.name, self.comment_prefix))

    def test_cli_file_not_found(self):
        """Test that CLI commands handle non-existent files gracefully."""
        non_existent_file = "no_such_file.py"
        commands_to_test = [
            cli.handle_add,
            cli.handle_verify,
            cli.handle_id,
            cli.handle_remove,
        ]
        for handler in commands_to_test:
            args = argparse.Namespace(file=non_existent_file, comment_prefix="#", author="test")
            f = io.StringIO()
            with redirect_stdout(f):
                handler(args)
            self.assertIn(f"[ERROR] File not found: {non_existent_file}", f.getvalue())