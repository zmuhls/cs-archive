#!/usr/bin/env python3
"""Generate comprehensive markdown files for each PDF collection."""

import re
from pathlib import Path
from collections import defaultdict

TEXT_DIR = Path("output/ocr/text")
MARKDOWN_DIR = Path("output/ocr/markdown")
NYS_IMAGES_DIR = Path("tinker-cookbook/data/nys_archives/images")
TABLES_IMAGES_DIR = Path("output/ocr/tables/images")

GITHUB_MEDIA_BASE = "https://media.githubusercontent.com/media/zmuhls/cs-archive/main"

# Collection definitions: prefix -> (folder_name, display_name, image_folder, description)
COLLECTIONS = {
    "Amityville-Records": {
        "display_name": "Amityville Board of Education Records",
        "image_folder": "tinker-cookbook/data/nys_archives/images/Amityville-Records",
        "description": "Meeting minutes and administrative records from the Amityville Union Free School District, documenting local education governance in Long Island, New York.",
        "doc_type": "Meeting Minutes",
        "source": "NYS Archives Series A4456"
    },
    "District-Consolidation-Data_100-116": {
        "display_name": "District Consolidation Data (Counties 100-116)",
        "image_folder": "output/ocr/tables/images",
        "description": "Statistical tables documenting school district consolidation across New York State counties, including Central Rural Schools formation dates and district reorganization records.",
        "doc_type": "Statistical Tables",
        "source": "NYS Archives Series B0494"
    },
    "District-Notecard-Records": {
        "display_name": "District Notecard Records",
        "image_folder": "tinker-cookbook/data/nys_archives/images/District-Notecard-Records",
        "description": "Index notecards cataloging school district information, used by NYS Education Department for administrative tracking.",
        "doc_type": "Administrative Notecards",
        "source": "NYS Archives Series B0594"
    },
    "South-Kortright-Roll-13": {
        "display_name": "South Kortright School District Records (Roll 13)",
        "image_folder": "tinker-cookbook/data/nys_archives/images/South-Kortright-Roll-13",
        "description": "Microfilm records from South Kortright Central School District in Delaware County, including meeting minutes and administrative correspondence.",
        "doc_type": "School District Records",
        "source": "NYS Archives Series A4645"
    },
    "Toward-Better-Schools": {
        "display_name": "Toward Better Schools",
        "image_folder": None,
        "description": "Publication discussing school improvement and educational reform in New York State.",
        "doc_type": "Educational Publication",
        "source": "Kheel Center Collection"
    }
}

def extract_page_number(filename: str) -> int:
    """Extract page number from filename."""
    match = re.search(r'page_(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0

def get_image_url(collection_key: str, page_num: int) -> str | None:
    """Get GitHub media URL for a page image."""
    config = COLLECTIONS.get(collection_key)
    if not config or not config["image_folder"]:
        return None

    folder = config["image_folder"]

    # Check for different naming patterns
    if "tables" in folder:
        # District Consolidation uses full filename
        img_name = f"{collection_key}_page_{page_num}.jpg"
        local_path = Path(folder) / img_name
        if local_path.exists():
            return f"{GITHUB_MEDIA_BASE}/{folder}/{img_name}"
    else:
        # NYS Archives uses page_N.png
        for ext in ['.png', '.jpg', '.jpeg']:
            img_name = f"page_{page_num}{ext}"
            local_path = Path(folder) / img_name
            if local_path.exists():
                return f"{GITHUB_MEDIA_BASE}/{folder}/{img_name}"

    return None

def read_text_content(txt_path: Path) -> str:
    """Read and clean text content from file."""
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    # Remove wrapping code blocks
    if content.startswith('```'):
        content = content[3:].lstrip()
        if content.endswith('```'):
            content = content[:-3].rstrip()

    return content

def generate_comprehensive_markdown(collection_key: str, page_files: list[Path]) -> str:
    """Generate comprehensive markdown for a collection."""
    config = COLLECTIONS[collection_key]

    # Sort by page number
    page_files.sort(key=lambda p: extract_page_number(p.name))

    lines = [
        f"# {config['display_name']}",
        "",
        f"**Document Type:** {config['doc_type']}",
        "",
        f"**Source:** {config['source']}",
        "",
        f"**Total Pages:** {len(page_files)}",
        "",
        "## Description",
        "",
        config['description'],
        "",
        "---",
        "",
        "## Table of Contents",
        "",
    ]

    # Generate TOC
    for txt_path in page_files:
        page_num = extract_page_number(txt_path.name)
        lines.append(f"- [Page {page_num}](#page-{page_num})")

    lines.extend(["", "---", ""])

    # Generate content for each page
    for txt_path in page_files:
        page_num = extract_page_number(txt_path.name)
        content = read_text_content(txt_path)
        image_url = get_image_url(collection_key, page_num)

        lines.extend([
            f"## Page {page_num}",
            "",
        ])

        if image_url:
            lines.extend([
                f"![Page {page_num}]({image_url})",
                "",
            ])

        lines.extend([
            "### Transcription",
            "",
            content,
            "",
            "---",
            "",
        ])

    return "\n".join(lines)

def main():
    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)

    # Group text files by collection
    collections = defaultdict(list)

    for txt_path in TEXT_DIR.glob("*.txt"):
        # Skip backup and complete files
        if ".backup" in txt_path.name or "_complete" in txt_path.name:
            continue

        # Match to collection
        for collection_key in COLLECTIONS:
            if collection_key in txt_path.name and "page_" in txt_path.name:
                collections[collection_key].append(txt_path)
                break

    # Generate comprehensive markdown for each collection
    for collection_key, page_files in collections.items():
        if not page_files:
            continue

        print(f"Generating {collection_key}: {len(page_files)} pages")

        md_content = generate_comprehensive_markdown(collection_key, page_files)
        md_path = MARKDOWN_DIR / f"{collection_key}_comprehensive.md"

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"  -> {md_path}")

    print(f"\nGenerated {len(collections)} comprehensive markdown files")

if __name__ == "__main__":
    main()
