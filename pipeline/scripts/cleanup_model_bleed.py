#!/usr/bin/env python3
"""
Clean up model response bleed-through from OCR text files.
Removes conversational preambles and trailing notes sections.
"""

import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

TEXT_DIR = PROJECT_ROOT / "output" / "ocr" / "text"

# Patterns to identify and remove from start of files
PREAMBLE_PATTERNS = [
    r"^Certainly!.*?adhering to the guidelines provided:\s*\n+---\s*\n+",
    r"^Here is the transcription.*?:\s*\n+---\s*\n+",
    r"^Below is a transcription.*?:\s*\n+---\s*\n+",
    r"^I'll transcribe.*?:\s*\n+---\s*\n+",
]

# Pattern to remove trailing notes section
NOTES_PATTERN = r"\n+---\s*\n+### Notes:.*$"


def clean_file(filepath: Path) -> bool:
    """Clean a single file. Returns True if changes were made."""
    content = filepath.read_text(encoding="utf-8")
    original = content

    # Remove preamble patterns
    for pattern in PREAMBLE_PATTERNS:
        content = re.sub(pattern, "", content, flags=re.DOTALL | re.IGNORECASE)

    # Remove trailing notes section
    content = re.sub(NOTES_PATTERN, "\n", content, flags=re.DOTALL)

    # Clean up excessive whitespace at start/end
    content = content.strip() + "\n"

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    # Find all qwen-vl-plus files (these have the bleed-through issue)
    files = list(TEXT_DIR.glob("*_qwen-vl-plus_*.txt"))

    cleaned = 0
    for filepath in files:
        if clean_file(filepath):
            print(f"Cleaned: {filepath.name}")
            cleaned += 1

    print(f"\nTotal: {cleaned} files cleaned out of {len(files)} checked")


if __name__ == "__main__":
    main()
