#!/usr/bin/env python3
"""
Generate Jekyll artifact pages from the archive manifest.

Reads manifest.json and creates one markdown file per artifact in docs/_artifacts/
with YAML frontmatter and transcription content.
"""

import json
import csv
import re
from pathlib import Path
from typing import Optional, Dict, List

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = PROJECT_ROOT / "output" / "archive" / "manifest.json"
ARCHIVE_PATH = PROJECT_ROOT / "output" / "archive"
INVENTORY_PATH = PROJECT_ROOT / "csv" / "images_inventory_labeled.csv"
ARTIFACTS_OUTPUT = PROJECT_ROOT / "docs" / "_artifacts"

# GitHub CDN base URLs
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/zmuhls/csa/main"
THUMB_PATH = f"{GITHUB_RAW_BASE}/derived/thumbs"
FULL_PATH = f"{GITHUB_RAW_BASE}/raw/scans/img"


def load_image_id_to_filename() -> Dict[str, str]:
    """Load mapping from image IDs (img_0001) to filenames (IMG_0625.jpeg)."""
    mapping = {}
    with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["id"]] = row["filename"]
    return mapping


def extract_decade(subject: str, notes: str) -> Optional[str]:
    """Extract decade from subject or notes (e.g., '1845' -> '1840s')."""
    text = f"{subject} {notes}"
    # Look for 4-digit years
    years = re.findall(r'\b(1[89]\d{2})\b', text)
    if years:
        year = int(years[0])
        decade = (year // 10) * 10
        return f"{decade}s"
    return None


def extract_county(location: str) -> Optional[str]:
    """Extract county name from location string."""
    if not location:
        return None
    # Check for "X County" pattern
    match = re.search(r'(\w+)\s+County', location, re.IGNORECASE)
    if match:
        return match.group(1).title() + " County"
    return None


def sanitize_title(title: str) -> str:
    """Escape quotes and clean up title for YAML."""
    if not title:
        return "Untitled Document"
    # Escape double quotes
    title = title.replace('"', '\\"')
    # Remove newlines
    title = title.replace('\n', ' ').replace('\r', '')
    return title.strip()


def get_transcription(artifact_path: str) -> str:
    """Read transcription file for an artifact."""
    trans_path = ARCHIVE_PATH / artifact_path / "transcription.txt"
    if trans_path.exists():
        content = trans_path.read_text(encoding="utf-8")
        return content.strip()
    return ""


def generate_artifact_page(artifact: dict, image_mapping: dict) -> str:
    """Generate markdown content for a single artifact."""
    artifact_id = artifact["artifact_group_id"]
    subject = artifact.get("subject", "")
    location = artifact.get("location_guess", "")
    notes = artifact.get("notes", "")
    item_type = artifact.get("item_type", "document_page")
    collection = artifact.get("collection", "documents")
    confidence = artifact.get("average_confidence", 0.0)
    word_count = artifact.get("word_count", 0)
    source_images = artifact.get("source_images", [])
    is_research = artifact.get("is_research", False)

    # Build source images array with URLs
    images_yaml = []
    for img_id in source_images:
        filename = image_mapping.get(img_id, f"{img_id}.jpeg")
        # URL encode spaces in filenames
        safe_filename = filename.replace(" ", "%20")
        images_yaml.append({
            "id": img_id,
            "filename": filename,
            "thumbnail": f"{THUMB_PATH}/{safe_filename}",
            "full": f"{FULL_PATH}/{safe_filename}"
        })

    # Format images for YAML
    images_lines = []
    for img in images_yaml:
        images_lines.append(f'  - id: "{img["id"]}"')
        images_lines.append(f'    filename: "{img["filename"]}"')
        images_lines.append(f'    thumbnail: "{img["thumbnail"]}"')
        images_lines.append(f'    full: "{img["full"]}"')
    images_yaml_str = "\n".join(images_lines) if images_lines else "  []"

    # Extract metadata
    decade = extract_decade(subject, notes)
    county = extract_county(location)

    # Get transcription
    transcription = get_transcription(artifact["path"])

    # Build frontmatter
    frontmatter = f'''---
layout: artifact
artifact_id: "{artifact_id}"
title: "{sanitize_title(subject)}"
item_type: "{item_type}"
location: "{sanitize_title(location)}"
collection: "{collection}"
is_research: {str(is_research).lower()}
confidence: {confidence}
word_count: {word_count}
'''

    if decade:
        frontmatter += f'decade: "{decade}"\n'
    if county:
        frontmatter += f'county: "{county}"\n'
    if notes:
        # Escape notes for YAML multiline
        notes_escaped = notes.replace('"', '\\"').replace('\n', ' ')
        frontmatter += f'notes: "{notes_escaped}"\n'

    frontmatter += f'''source_images:
{images_yaml_str}
---

{transcription}
'''

    return frontmatter


def main():
    """Generate all artifact pages."""
    print("Loading manifest...")
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print("Loading image ID mapping...")
    image_mapping = load_image_id_to_filename()

    # Ensure output directory exists
    ARTIFACTS_OUTPUT.mkdir(parents=True, exist_ok=True)

    artifacts = manifest.get("artifacts", [])
    print(f"Generating {len(artifacts)} artifact pages...")

    for artifact in artifacts:
        artifact_id = artifact["artifact_group_id"]
        content = generate_artifact_page(artifact, image_mapping)

        # Write markdown file
        output_path = ARTIFACTS_OUTPUT / f"{artifact_id}.md"
        output_path.write_text(content, encoding="utf-8")

    print(f"Done! Generated {len(artifacts)} pages in {ARTIFACTS_OUTPUT}")


if __name__ == "__main__":
    main()
