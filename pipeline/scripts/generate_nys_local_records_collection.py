#!/usr/bin/env python3
"""
Generate NYS Archives Local District Records collection.

Processes OCR outputs from NYS Archives PDF collections:
- A4456: Amityville Records
- A4645: South-Kortright Roll
- B0594: District Notecard Records

Output: output/collections/nys-local-records.md
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Configuration
OCR_TEXT_DIR = PROJECT_ROOT / 'output' / 'ocr' / 'text'
OCR_METADATA_DIR = PROJECT_ROOT / 'output' / 'ocr' / 'metadata'
OUTPUT_PATH = PROJECT_ROOT / 'output' / 'collections' / 'nys-local-records.md'
GITHUB_REPO = "zmuhls/cs-archive"
BRANCH = "main"

# NYS Archives series to include (excluding B0494 which is in district consolidation)
NYS_LOCAL_SERIES = {
    'South-Kortright-Roll-13': {
        'series': 'A4645',
        'title': 'South-Kortright Roll',
        'description': 'School district meeting minutes and records from South Kortright, Delaware County (1810s-1820s)',
        'theme': 'Meeting Minutes & Governance',
    },
    'District-Notecard-Records': {
        'series': 'B0594',
        'title': 'District Notecard Records',
        'description': 'Index cards documenting school registration, name changes, and administrative actions',
        'theme': 'Administrative Records',
    },
    'Amityville-Records': {
        'series': 'A4456',
        'title': 'Amityville Records',
        'description': 'Local school district records from Amityville, Suffolk County',
        'theme': 'Local District Records',
    },
}


def find_processed_pdfs() -> Dict[str, List[Path]]:
    """Find all processed PDF pages in OCR output directory."""
    pdf_pages = defaultdict(list)

    if not OCR_TEXT_DIR.exists():
        print(f"Warning: OCR text directory not found: {OCR_TEXT_DIR}")
        return pdf_pages

    for text_file in OCR_TEXT_DIR.glob("*.txt"):
        filename = text_file.stem

        # Skip complete files (we'll use individual pages)
        if filename.endswith('_complete'):
            continue

        # Match pattern: {PDF_NAME}_page_{N}.txt
        for pdf_name in NYS_LOCAL_SERIES.keys():
            if filename.startswith(pdf_name):
                pdf_pages[pdf_name].append(text_file)

    # Sort pages by page number
    for pdf_name in pdf_pages:
        pdf_pages[pdf_name] = sorted(
            pdf_pages[pdf_name],
            key=lambda p: extract_page_number(p.stem)
        )

    return pdf_pages


def extract_page_number(filename: str) -> int:
    """Extract page number from filename like 'South-Kortright-Roll-13_page_5'."""
    match = re.search(r'_page_(\d+)$', filename)
    if match:
        return int(match.group(1))
    return 0


def load_page_text(text_path: Path) -> str:
    """Load OCR text from a page file."""
    try:
        return text_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading {text_path}: {e}")
        return ""


def extract_date_from_text(text: str) -> Optional[int]:
    """Extract year from OCR text."""
    # Look for 4-digit years in the 1800s-1900s
    years = re.findall(r'\b(18\d{2}|19[0-4]\d)\b', text)
    if years:
        # Return earliest year found
        return min(int(y) for y in years)
    return None


def extract_location_from_text(text: str) -> Optional[str]:
    """Extract location/county from OCR text."""
    # Common NY county patterns
    county_pattern = r'(\w+)\s+County'
    match = re.search(county_pattern, text)
    if match:
        return match.group(1) + " County"

    # Look for town names
    towns = ['Amityville', 'South Kortright', 'Rochester', 'Albany', 'Syracuse']
    for town in towns:
        if town.lower() in text.lower():
            return town

    return None


def analyze_page_content(text: str) -> Dict:
    """Analyze page content to extract metadata."""
    return {
        'date': extract_date_from_text(text),
        'location': extract_location_from_text(text),
        'length': len(text),
        'has_meeting': any(word in text.lower() for word in ['meeting', 'voted', 'trustees']),
        'has_school_name': any(word in text.lower() for word in ['school', 'district', 'academy']),
    }


def format_series_section(pdf_name: str, pages: List[Path]) -> str:
    """Format a series section with page summaries."""
    series_info = NYS_LOCAL_SERIES.get(pdf_name, {})
    series_id = series_info.get('series', 'Unknown')
    title = series_info.get('title', pdf_name)
    description = series_info.get('description', '')
    theme = series_info.get('theme', 'General')

    lines = [
        f"### {title}",
        "",
        f"**Series**: NYS Archives {series_id}",
        f"**Theme**: {theme}",
        f"**Pages**: {len(pages)}",
        "",
        description,
        "",
    ]

    # Group pages by decade if dates are available
    by_decade = defaultdict(list)
    undated = []

    for page_path in pages:
        text = load_page_text(page_path)
        analysis = analyze_page_content(text)
        page_num = extract_page_number(page_path.stem)

        page_info = {
            'page': page_num,
            'path': page_path,
            'date': analysis['date'],
            'location': analysis['location'],
            'preview': text[:200].replace('\n', ' ').strip() if text else '',
        }

        if analysis['date']:
            decade = (analysis['date'] // 10) * 10
            by_decade[f"{decade}s"].append(page_info)
        else:
            undated.append(page_info)

    # Output by decade
    if by_decade:
        lines.append("#### By Decade")
        lines.append("")

        for decade in sorted(by_decade.keys()):
            decade_pages = by_decade[decade]
            lines.append(f"**{decade}** ({len(decade_pages)} pages)")
            lines.append("")

            for page in decade_pages[:5]:  # Show first 5 per decade
                date_str = str(page['date']) if page['date'] else 'undated'
                loc_str = f" — {page['location']}" if page['location'] else ''
                preview = page['preview'][:100] + '...' if len(page['preview']) > 100 else page['preview']
                lines.append(f"- **Page {page['page']}** ({date_str}{loc_str}): {preview}")

            if len(decade_pages) > 5:
                lines.append(f"- *...and {len(decade_pages) - 5} more pages*")

            lines.append("")

    # Output undated
    if undated:
        lines.append(f"#### Undated ({len(undated)} pages)")
        lines.append("")

        for page in undated[:5]:
            preview = page['preview'][:100] + '...' if len(page['preview']) > 100 else page['preview']
            lines.append(f"- **Page {page['page']}**: {preview}")

        if len(undated) > 5:
            lines.append(f"- *...and {len(undated) - 5} more pages*")

        lines.append("")

    return "\n".join(lines)


def generate_collection_markdown(pdf_pages: Dict[str, List[Path]]) -> str:
    """Generate complete collection markdown."""
    # Calculate totals
    total_pages = sum(len(pages) for pages in pdf_pages.values())
    series_count = len(pdf_pages)

    # Build markdown
    sections = [
        "<!-- This file is auto-generated by scripts/generate_nys_local_records_collection.py -->",
        "",
        "# NYS Archives Local District Records",
        "",
        "This collection presents primary source materials from the New York State Archives documenting local school district governance, administration, and records from the 19th and early 20th centuries.",
        "",
        "---",
        "",
        "## Overview",
        "",
        f"- **Total Pages**: {total_pages}",
        f"- **Series**: {series_count}",
        "- **Source**: New York State Archives",
        "- **Time Period**: 1810s-1940s",
        "",
        "---",
        "",
        "## Table of Contents",
        "",
    ]

    # Add TOC entries
    for pdf_name in sorted(pdf_pages.keys()):
        series_info = NYS_LOCAL_SERIES.get(pdf_name, {})
        title = series_info.get('title', pdf_name)
        anchor = title.lower().replace(' ', '-')
        page_count = len(pdf_pages[pdf_name])
        sections.append(f"- [{title}](#{anchor}) ({page_count} pages)")

    sections.extend([
        "",
        "---",
        "",
        "## Series",
        "",
    ])

    # Add each series section
    for pdf_name in sorted(pdf_pages.keys()):
        pages = pdf_pages[pdf_name]
        sections.append(format_series_section(pdf_name, pages))
        sections.append("---")
        sections.append("")

    # Add notes
    sections.extend([
        "## Notes",
        "",
        "- **Source**: All materials are from the New York State Archives.",
        "- **OCR**: Text extracted using Qwen VL Plus via OpenRouter.",
        "- **Regenerate**: Run `python scripts/generate_nys_local_records_collection.py` to refresh.",
        "- **Add Amityville**: Run `python scripts/process_amityville.py` to process the 665-page Amityville PDF.",
        "",
    ])

    return "\n".join(sections)


def generate_stats_report(pdf_pages: Dict[str, List[Path]]) -> str:
    """Generate statistics report."""
    lines = [
        "# NYS Local Records Collection Statistics",
        "",
    ]

    for pdf_name, pages in sorted(pdf_pages.items()):
        series_info = NYS_LOCAL_SERIES.get(pdf_name, {})
        lines.append(f"## {series_info.get('title', pdf_name)}")
        lines.append(f"- Series: {series_info.get('series', 'Unknown')}")
        lines.append(f"- Pages: {len(pages)}")

        # Analyze content
        dates_found = 0
        locations_found = 0

        for page_path in pages:
            text = load_page_text(page_path)
            analysis = analyze_page_content(text)
            if analysis['date']:
                dates_found += 1
            if analysis['location']:
                locations_found += 1

        lines.append(f"- Pages with dates: {dates_found} ({dates_found/len(pages)*100:.1f}%)")
        lines.append(f"- Pages with locations: {locations_found} ({locations_found/len(pages)*100:.1f}%)")
        lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("NYS Archives Local District Records Collection Generator")
    print("=" * 70)
    print()

    # Find processed PDFs
    print("Scanning OCR outputs...")
    pdf_pages = find_processed_pdfs()

    if not pdf_pages:
        print("No processed PDF pages found!")
        print(f"Expected files in: {OCR_TEXT_DIR}")
        print("Run OCR first with: python process_archive.py --collection nys")
        return

    for pdf_name, pages in pdf_pages.items():
        series_info = NYS_LOCAL_SERIES.get(pdf_name, {})
        print(f"  {series_info.get('title', pdf_name)}: {len(pages)} pages")

    print()

    # Generate markdown
    print("Generating collection markdown...")
    markdown = generate_collection_markdown(pdf_pages)

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(markdown, encoding='utf-8')
    print(f"  Written to: {OUTPUT_PATH}")
    print()

    # Generate stats report
    print("Generating statistics report...")
    stats = generate_stats_report(pdf_pages)
    stats_path = PROJECT_ROOT / 'output' / 'collections' / 'nys-local-records-stats.txt'
    stats_path.write_text(stats, encoding='utf-8')
    print(f"  Report: {stats_path}")
    print()

    print("=" * 70)
    print("Done!")
    print("=" * 70)


if __name__ == '__main__':
    main()
