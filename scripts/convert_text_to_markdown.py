#!/usr/bin/env python3
"""Convert OCR text files to structured markdown format."""

import json
import os
import re
from pathlib import Path
from datetime import datetime

TEXT_DIR = Path("output/ocr/text")
METADATA_DIR = Path("output/ocr/metadata")
MARKDOWN_DIR = Path("output/ocr/markdown")
THUMBS_DIR = Path("derived/thumbs")
TABLES_THUMBS_DIR = Path("output/ocr/tables/thumbs")
TABLES_IMAGES_DIR = Path("output/ocr/tables/images")
NYS_IMAGES_DIR = Path("tinker-cookbook/data/nys_archives/images")

# Relative path prefix from output/ocr/markdown/ to project root
REL_PREFIX = "../../.."

def get_metadata_filename(txt_filename: str) -> str:
    """Convert text filename to metadata filename pattern."""
    # Remove _qwen-vl-plus from filename for metadata lookup
    base = txt_filename.replace(".txt", "").replace("_qwen-vl-plus", "")
    return f"{base}.json"

def find_image_for_file(txt_filename: str) -> tuple[str, str] | None:
    """Find corresponding image file and return (local_path, relative_url)."""
    base = txt_filename.replace(".txt", "").replace("_qwen-vl-plus", "")

    # Check for IMG_ files in derived/thumbs
    if "IMG_" in txt_filename:
        match = re.search(r'(IMG_\d+)', txt_filename)
        if match:
            img_name = match.group(1)
            for ext in ['.jpeg', '.jpg']:
                thumb_path = THUMBS_DIR / f"{img_name}{ext}"
                if thumb_path.exists():
                    rel_url = f"{REL_PREFIX}/derived/thumbs/{img_name}{ext}"
                    return str(thumb_path), rel_url

    # Check for other files with numeric IDs in derived/thumbs
    if txt_filename.startswith("70914"):
        base_name = txt_filename.replace(".txt", "")
        for ext in ['.jpeg', '.jpg']:
            thumb_path = THUMBS_DIR / f"{base_name}{ext}"
            if thumb_path.exists():
                rel_url = f"{REL_PREFIX}/derived/thumbs/{base_name}{ext}"
                return str(thumb_path), rel_url

    # Check NYS Archives images (Amityville, District-Notecard, South-Kortright)
    nys_collections = {
        "Amityville-Records": "Amityville-Records",
        "District-Notecard": "District-Notecard-Records",
        "South-Kortright": "South-Kortright-Roll-13",
    }
    for prefix, folder in nys_collections.items():
        if prefix in txt_filename:
            # Extract page number
            match = re.search(r'page_(\d+)', txt_filename)
            if match:
                page_num = match.group(1)
                for ext in ['.png', '.jpg', '.jpeg']:
                    img_path = NYS_IMAGES_DIR / folder / f"page_{page_num}{ext}"
                    if img_path.exists():
                        rel_url = f"{REL_PREFIX}/tinker-cookbook/data/nys_archives/images/{folder}/page_{page_num}{ext}"
                        return str(img_path), rel_url

    # Check tables/images for District Consolidation
    if "District-Consolidation" in txt_filename:
        for img_dir, url_path in [(TABLES_IMAGES_DIR, "../tables/images"), (TABLES_THUMBS_DIR, "../tables/thumbs")]:
            for ext in ['.jpg', '.png', '.jpeg']:
                img_name = base + ext
                img_path = img_dir / img_name
                if img_path.exists():
                    return str(img_path), f"{url_path}/{img_name}"

    return None

def extract_title_from_content(content: str, filename: str) -> str:
    """Extract a reasonable title from the content or filename."""
    # Try to get first meaningful line
    lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('```')]
    if lines:
        first_line = lines[0][:80]
        if len(first_line) > 10:
            return first_line

    # Fall back to filename
    base = filename.replace(".txt", "").replace("_qwen-vl-plus", "")
    return base.replace("_", " ").replace("-", " ")

def convert_to_markdown(txt_path: Path) -> str:
    """Convert a text file to structured markdown."""
    # Read text content
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Clean content - remove wrapping code blocks if present
    content_clean = content.strip()
    if content_clean.startswith('```') and content_clean.endswith('```'):
        content_clean = content_clean[3:].lstrip()
        if content_clean.endswith('```'):
            content_clean = content_clean[:-3].rstrip()

    # Try to load metadata
    metadata_name = get_metadata_filename(txt_path.name)
    metadata_path = METADATA_DIR / metadata_name

    metadata = {}
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

    # Extract info
    title = extract_title_from_content(content_clean, txt_path.name)
    source_file = metadata.get("source_file", txt_path.name)
    processed_at = metadata.get("processed_at", datetime.now().isoformat())
    model = metadata.get("model", "qwen/qwen-vl-plus")
    confidence = metadata.get("confidence", "N/A")

    # Determine document type from filename
    if "Amityville" in txt_path.name:
        doc_type = "Meeting Minutes"
        collection = "Amityville Board of Education Records"
    elif "IMG_" in txt_path.name:
        doc_type = "Historical Document"
        collection = "Kheel Center Collection"
    else:
        doc_type = "Document"
        collection = "CS Archive"

    # Find image
    image_info = find_image_for_file(txt_path.name)

    # Build markdown
    md_lines = [
        f"# {title}",
        "",
        f"**Document Type:** {doc_type}",
        "",
        f"**Collection:** {collection}",
        "",
        f"**Source:** {Path(source_file).name}",
        "",
        f"**Model:** {model}",
        "",
        f"**Confidence:** {confidence}",
        "",
        f"**Processed:** {processed_at}",
        "",
    ]

    if image_info:
        local_path, github_url = image_info
        md_lines.extend([
            f"**Source Image:** [📄 {Path(local_path).name}]({github_url})",
            "",
        ])

    md_lines.extend([
        "---",
        "",
    ])

    if image_info:
        local_path, github_url = image_info
        md_lines.extend([
            "## Source Document",
            "",
            f"![{title}]({github_url})",
            "",
            "---",
            "",
        ])

    md_lines.extend([
        "## Transcription",
        "",
        content_clean,
        ""
    ])

    return "\n".join(md_lines)

def main():
    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)

    txt_files = list(TEXT_DIR.glob("*.txt"))
    print(f"Found {len(txt_files)} text files to convert")

    converted = 0
    skipped = 0
    with_images = 0

    for txt_path in txt_files:
        # Skip backup files
        if ".backup" in txt_path.name:
            skipped += 1
            continue


        md_name = txt_path.name.replace(".txt", ".md")
        md_path = MARKDOWN_DIR / md_name

        try:
            md_content = convert_to_markdown(txt_path)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            converted += 1
            if find_image_for_file(txt_path.name):
                with_images += 1
        except Exception as e:
            print(f"Error converting {txt_path.name}: {e}")

    print(f"Converted: {converted}, With images: {with_images}, Skipped: {skipped}")

if __name__ == "__main__":
    main()
