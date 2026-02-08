#!/usr/bin/env python3
"""
Download and extract Plesk Extensions Guide documentation.

This script downloads the Plesk extensions guide ZIP file and extracts it
to the html/ folder. It also ensures the storage/ directory exists with
proper permissions for the vector database.
"""

import os
import sys
import urllib.request
import zipfile
from pathlib import Path

# Constants
DOCS_URL = "https://docs.plesk.com/en-US/obsidian/zip/extensions-guide.zip"
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
HTML_DIR = PROJECT_ROOT / "html"
STORAGE_DIR = PROJECT_ROOT / "storage"
ZIP_FILE = PROJECT_ROOT / "extensions-guide.zip"


def download_docs():
    """Download the Plesk extensions guide ZIP file."""
    print(f"Downloading Plesk Extensions Guide from {DOCS_URL}...")
    try:
        urllib.request.urlretrieve(DOCS_URL, ZIP_FILE)
        print(f"✓ Downloaded successfully to {ZIP_FILE}")
        return True
    except Exception as e:
        print(f"✗ Failed to download: {e}")
        return False


def extract_docs():
    """Extract the ZIP file to the html/ folder."""
    if not ZIP_FILE.exists():
        print(f"✗ ZIP file not found: {ZIP_FILE}")
        return False

    print(f"Extracting to {HTML_DIR}...")
    try:
        # Create html directory if it doesn't exist
        HTML_DIR.mkdir(exist_ok=True)

        with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
            zip_ref.extractall(HTML_DIR)

        print(f"✓ Extracted successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to extract: {e}")
        return False


def setup_storage_dir():
    """Create and set permissions for the storage/ directory."""
    print(f"Setting up storage directory at {STORAGE_DIR}...")
    try:
        STORAGE_DIR.mkdir(exist_ok=True)
        # Ensure readable and writable by owner
        os.chmod(STORAGE_DIR, 0o755)
        print(f"✓ Storage directory ready")
        return True
    except Exception as e:
        print(f"✗ Failed to setup storage directory: {e}")
        return False


def cleanup_zip():
    """Remove the downloaded ZIP file."""
    try:
        if ZIP_FILE.exists():
            ZIP_FILE.unlink()
            print(f"✓ Cleaned up {ZIP_FILE}")
    except Exception as e:
        print(f"⚠ Warning: Could not remove {ZIP_FILE}: {e}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Plesk Extensions Guide Documentation Setup")
    print("=" * 60)
    print()

    # Download documentation
    if not download_docs():
        sys.exit(1)

    print()

    # Extract documentation
    if not extract_docs():
        sys.exit(1)

    print()

    # Setup storage directory
    if not setup_storage_dir():
        sys.exit(1)

    print()

    # Cleanup
    cleanup_zip()

    print()
    print("=" * 60)
    print("✓ Setup complete! You can now start the MCP server.")
    print("=" * 60)


if __name__ == "__main__":
    main()
