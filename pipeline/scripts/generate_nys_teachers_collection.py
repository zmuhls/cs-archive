#!/usr/bin/env python3
"""
Generate NYS Teachers Association curated collection with accurate dates.

Extracts dates from OCR output and inventory metadata to create a chronologically
organized collection of documents related to the New York State Teachers Association.
"""

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

# Import local date extractor
import sys
sys.path.insert(0, str(Path(__file__).parent))
from date_extractor import get_best_date, extract_date_range, is_modern_item_type

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Configuration
CSV_PATH = PROJECT_ROOT / 'csv' / 'images_inventory_labeled.csv'
OCR_TEXT_DIR = PROJECT_ROOT / 'output' / 'ocr' / 'text'
OCR_METADATA_DIR = PROJECT_ROOT / 'output' / 'ocr' / 'metadata'
OUTPUT_PATH = PROJECT_ROOT / 'output' / 'collections' / 'nys-teachers-association.md'
GITHUB_REPO = "zmuhls/cs-archive"
BRANCH = "main"


def load_inventory() -> List[dict]:
    """Load and filter inventory for NYSTA-related items."""
    items = []

    with CSV_PATH.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Filter for NYSTA-related items
            title = row.get('item_title', '').lower()
            subject = row.get('subject', '').lower()
            notes = row.get('notes', '').lower()

            combined = f"{title} {subject} {notes}"

            if any(phrase in combined for phrase in [
                'new york state teachers',
                'n.y. state teachers',
                'nysta',
                'n.y.s. teachers',
                'nys teachers',
            ]):
                items.append(row)

    print(f"Found {len(items)} NYSTA-related items")
    return items


def load_ocr_text(filename: str) -> Optional[str]:
    """Load OCR text for a given image filename."""
    if not filename:
        return None

    # Convert IMG_0625.jpeg -> IMG_0625.txt
    base_name = Path(filename).stem
    text_path = OCR_TEXT_DIR / f"{base_name}.txt"

    if text_path.exists():
        return text_path.read_text(encoding='utf-8')

    return None


def load_ocr_metadata(filename: str) -> float:
    """Load OCR metadata confidence score."""
    if not filename:
        return 0.0

    base_name = Path(filename).stem
    meta_path = OCR_METADATA_DIR / f"{base_name}.json"

    if meta_path.exists():
        try:
            with meta_path.open('r') as f:
                meta = json.load(f)
                return meta.get('confidence', 0.0)
        except:
            return 0.0

    return 0.0


def enrich_with_dates(items: List[dict]) -> List[dict]:
    """Add extracted_date and date_source fields to each item."""
    enriched = []

    for item in items:
        filename = item.get('filename', '')
        ocr_text = load_ocr_text(filename)
        ocr_confidence = load_ocr_metadata(filename)

        year, source, confidence = get_best_date(item, ocr_text, ocr_confidence)

        # Add enriched fields
        enriched_item = item.copy()
        enriched_item['extracted_date'] = year
        enriched_item['date_source'] = source
        enriched_item['date_confidence'] = confidence

        # Mark uncertain dates
        if year and (confidence < 0.7 or 'uncertain' in source):
            enriched_item['date_uncertain'] = True
        else:
            enriched_item['date_uncertain'] = False

        enriched.append(enriched_item)

    return enriched


def group_by_decade(items: List[dict]) -> Dict[str, List[dict]]:
    """Group items by decade based on extracted_date."""
    decades = defaultdict(list)

    for item in items:
        year = item.get('extracted_date')

        if year:
            # Handle year ranges - use first year per user decision
            decade = (year // 10) * 10
            decade_key = f"{decade}s"
            decades[decade_key].append(item)
        else:
            decades['undated'].append(item)

    # Sort decades chronologically
    sorted_decades = {}
    for key in sorted(decades.keys()):
        if key != 'undated':
            sorted_decades[key] = sorted(decades[key], key=lambda x: x.get('extracted_date', 0))

    # Add undated at end
    if 'undated' in decades:
        sorted_decades['undated'] = sorted(decades['undated'], key=lambda x: x.get('filename', ''))

    return sorted_decades


def group_by_theme(items: List[dict]) -> Dict[str, List[dict]]:
    """Group items by theme based on item_type and content."""
    themes = {
        'Founding & Early Advocacy': [],
        'Annual Meetings & Proceedings': [],
        'Membership & Organization': [],
        'Advocacy & Policy': [],
        'Publications & Periodicals': [],
        'Bound Volumes & Archival Notes': [],
    }

    for item in items:
        item_type = item.get('item_type', '')
        title = item.get('item_title', '').lower()
        subject = item.get('subject', '').lower()

        # Categorize by keywords and type
        if any(word in title for word in ['founding', '1845', 'formation', 'established']):
            if item.get('extracted_date') and item['extracted_date'] <= 1860:
                themes['Founding & Early Advocacy'].append(item)

        if any(word in title + subject for word in ['proceedings', 'meeting', 'annual', 'session', 'minutes']):
            themes['Annual Meetings & Proceedings'].append(item)

        if any(word in title + subject for word in ['membership', 'officers', 'members', 'organization', 'district']):
            themes['Membership & Organization'].append(item)

        if any(word in title + subject for word in ['address', 'proposal', 'advocacy', 'legislation', 'policy']):
            themes['Advocacy & Policy'].append(item)

        if any(word in title + subject for word in ['newsletter', 'publication', 'magazine', 'periodical', 'history']):
            themes['Publications & Periodicals'].append(item)

        if item_type == 'notecard' or 'bound volume' in title:
            themes['Bound Volumes & Archival Notes'].append(item)

    # Remove empty themes and deduplicate
    filtered_themes = {}
    for theme, theme_items in themes.items():
        if theme_items:
            # Deduplicate by ID
            seen = set()
            unique_items = []
            for item in theme_items:
                item_id = item.get('id')
                if item_id not in seen:
                    seen.add(item_id)
                    unique_items.append(item)

            filtered_themes[theme] = sorted(unique_items, key=lambda x: (x.get('extracted_date') or 9999, x.get('filename', '')))

    return filtered_themes


def format_thumbnail_url(filename: str) -> str:
    """Generate GitHub raw URL for thumbnail."""
    if not filename:
        return ""

    # Remove any directory path, just get the filename
    base_filename = Path(filename).name

    return f"https://raw.githubusercontent.com/{GITHUB_REPO}/{BRANCH}/derived/thumbs/{base_filename}"


def format_fullsize_url(filename: str) -> str:
    """Generate GitHub blob URL for full-size image."""
    if not filename:
        return ""

    # Remove any directory path, just get the filename
    base_filename = Path(filename).name

    return f"https://github.com/{GITHUB_REPO}/blob/{BRANCH}/raw/scans/Kheel Center/img/{base_filename}"


def format_item_markdown(item: dict, show_artifact_id: bool = False, indent: bool = False) -> str:
    """Format a single item as markdown with thumbnail on separate line."""
    year = item.get('extracted_date')
    uncertain = item.get('date_uncertain', False)
    title = item.get('item_title', '').strip() or item.get('subject', '').strip() or 'Untitled'
    location = item.get('location_guess', '')
    filename = item.get('filename', '')
    artifact_id = item.get('artifact_group_id', '')

    # Format date
    if year:
        date_str = f"{year}?" if uncertain else f"{year}"
    else:
        date_str = "Undated"

    # Format image URLs - thumbnail for display, full-size for link
    thumb_url = format_thumbnail_url(filename)
    fullsize_url = format_fullsize_url(filename)
    base_filename = Path(filename).stem if filename else 'Unknown'

    # Build markdown with thumbnail on separate indented line
    lines = []

    # First line: link with date and location
    link_text = f"{date_str}"
    if location:
        link_text += f" — {location}"
    if show_artifact_id and artifact_id:
        link_text += f" ({artifact_id})"

    lines.append(f"- [{link_text}]({fullsize_url})")

    # Second line: thumbnail (indented)
    if thumb_url and fullsize_url:
        lines.append(f"  [![{base_filename}]({thumb_url})]({fullsize_url})")

    return "\n".join(lines)


def format_chronological_section(decade_items: Dict[str, List[dict]]) -> str:
    """Generate markdown for chronological section."""
    lines = [
        "## Chronology (By Decade)",
        "",
    ]

    for decade, items in decade_items.items():
        if decade == 'undated':
            lines.append("### Undated")
        else:
            lines.append(f"### {decade.capitalize()}")

        lines.append("")

        for item in items:
            lines.append(format_item_markdown(item))
            lines.append("")

    return "\n".join(lines)


def format_thematic_section(theme_items: Dict[str, List[dict]]) -> str:
    """Generate markdown for thematic section."""
    lines = [
        "## Thematic Groupings",
        "",
    ]

    for theme, items in theme_items.items():
        lines.append(f"### {theme}")
        lines.append("")

        # Group by artifact_group_id within theme
        by_artifact = defaultdict(list)
        for item in items:
            artifact_id = item.get('artifact_group_id', item.get('id', ''))
            by_artifact[artifact_id].append(item)

        for artifact_id, artifact_items in sorted(by_artifact.items()):
            for item in artifact_items:
                lines.append(format_item_markdown(item, show_artifact_id=True))
                lines.append("")

    return "\n".join(lines)


def generate_markdown(items: List[dict]) -> str:
    """Generate complete markdown file."""
    # Group items
    by_decade = group_by_decade(items)
    by_theme = group_by_theme(items)

    # Build Table of Contents
    toc_lines = [
        "## Table of Contents",
        "",
    ]

    # Add decades to TOC
    for decade in by_decade.keys():
        if decade == 'undated':
            toc_lines.append(f"- [Undated](#undated) ({len(by_decade[decade])} items)")
        else:
            toc_lines.append(f"- [{decade.capitalize()}](#{decade}) ({len(by_decade[decade])} items)")

    toc_lines.append("")

    # Add themes to TOC
    toc_lines.append("**Thematic Groupings:**")
    for theme in by_theme.keys():
        anchor = theme.lower().replace(' ', '-').replace('&', '')
        toc_lines.append(f"- [{theme}](#{anchor}) ({len(by_theme[theme])} items)")

    toc = "\n".join(toc_lines)

    # Build markdown
    sections = [
        "<!-- This file is auto-generated by scripts/generate_nys_teachers_collection.py -->",
        "",
        "# New York State Teachers' Association — Curated Collection",
        "",
        "This collection gathers materials across the archive that explicitly reference the New York State Teachers' Association (NYSTA), spanning 1845-1940s. Each entry links to the digitized artifact with a thumbnail preview.",
        "",
        "---",
        "",
        toc,
        "",
        "---",
        "",
        format_chronological_section(by_decade),
        "---",
        "",
        format_thematic_section(by_theme),
        "---",
        "",
        "## Notes",
        "",
        "- **Scope**: Items include explicit \"New York State Teachers' Association,\" \"N.Y. State Teachers' Association,\" \"NYSTA,\" or clear NYS context.",
        "- **Sources**: Derived from `csv/images_inventory_labeled.csv` and OCR text outputs.",
        "- **Dates**: Extracted from OCR text and metadata. Uncertain dates marked with `?`.",
        "- **Regenerate**: Run `python scripts/generate_nys_teachers_collection.py` to refresh.",
        ""
    ]

    return "\n".join(sections)


def generate_validation_report(items: List[dict]) -> str:
    """Generate validation report for review."""
    lines = [
        "# NYS Teachers Association Collection - Date Validation Report",
        "",
        f"Total items: {len(items)}",
        ""
    ]

    # Count by date source
    by_source = defaultdict(int)
    uncertain_count = 0

    for item in items:
        source = item.get('date_source', 'unknown')
        by_source[source] += 1

        if item.get('date_uncertain', False):
            uncertain_count += 1

    lines.append("## Date Sources")
    lines.append("")
    for source, count in sorted(by_source.items(), key=lambda x: -x[1]):
        pct = (count / len(items)) * 100
        lines.append(f"- {source}: {count} ({pct:.1f}%)")

    lines.append("")
    lines.append(f"## Uncertain Dates: {uncertain_count}")
    lines.append("")

    # List uncertain items
    uncertain_items = [item for item in items if item.get('date_uncertain', False)]
    for item in uncertain_items[:20]:  # Show first 20
        year = item.get('extracted_date', 'None')
        filename = item.get('filename', '')
        title = item.get('item_title', '')
        lines.append(f"- [{year}?] {filename}: {title}")

    lines.append("")
    lines.append(f"... and {len(uncertain_items) - 20} more" if len(uncertain_items) > 20 else "")

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("NYS Teachers Association Collection Generator")
    print("=" * 70)
    print()

    # Load and filter inventory
    items = load_inventory()
    print()

    # Enrich with dates
    print("Extracting dates from OCR and metadata...")
    items = enrich_with_dates(items)

    # Count date sources
    dated = sum(1 for item in items if item.get('extracted_date'))
    undated = len(items) - dated
    print(f"  Dated items: {dated}")
    print(f"  Undated items: {undated}")
    print()

    # Generate markdown
    print("Generating collection markdown...")
    markdown = generate_markdown(items)

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(markdown, encoding='utf-8')
    print(f"  ✓ Written to: {OUTPUT_PATH}")
    print()

    # Generate validation report
    print("Generating validation report...")
    report = generate_validation_report(items)
    report_path = PROJECT_ROOT / 'output' / 'collections' / 'nys-teachers-validation.txt'
    report_path.write_text(report, encoding='utf-8')
    print(f"  ✓ Report: {report_path}")
    print()

    print("=" * 70)
    print("Done! Review the collection and validation report.")
    print("=" * 70)


if __name__ == '__main__':
    main()
