import os
import tempfile
from embedid.core import (
    embed_watermark,
    remove_watermark,
    scramble_metadata,
    extract_watermark,
    descramble_metadata,
)

def test_watermark_lifecycle():
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py', encoding='utf-8')
    temp_file.write("# Sample Python file\nprint('Hello, world!')\n")
    temp_path = temp_file.name
    temp_file.close()

    meta = {"author": "James The Giblet"}
    comment_prefix = "#"

    try:
        # Step 1: Embed watermark
        _, encoded = scramble_metadata(meta)
        success = embed_watermark(temp_path, encoded, comment_prefix)
        assert success, "Failed to embed watermark"

        # Step 2: Verify watermark by extracting and descrambling
        extracted_encoded = extract_watermark(temp_path, comment_prefix)
        assert extracted_encoded is not None, "Failed to extract watermark"
        decoded_meta = descramble_metadata(extracted_encoded)
        assert decoded_meta['author'] == meta['author'], "Watermark verification failed"

        # Step 3: Remove watermark
        removed = remove_watermark(temp_path, comment_prefix)
        assert removed, "Failed to remove watermark"
        cleaned_content = extract_watermark(temp_path, comment_prefix)
        assert cleaned_content is None, "Watermark not removed correctly"

    finally:
        # Cleanup
        os.remove(temp_path)