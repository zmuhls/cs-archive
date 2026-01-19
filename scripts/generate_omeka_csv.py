#!/usr/bin/env python3
"""
Generate OMEKA import CSV from collection markdown files and consolidated artifacts.

Parses:
- output/collections/district-consolidation-by-county.md
- output/collections/nys-teachers-association.md

And matches items to:
- csv/images_inventory_labeled.csv
- output/archive/documents/{artifact_group_id}/

Output:
- output/omeka/items_import.csv (Dublin Core fields for OMEKA CSV Import plugin)
"""

import csv
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ARCHIVE_DIR = OUTPUT_DIR / "archive" / "documents"
COLLECTIONS_DIR = OUTPUT_DIR / "collections"
CSV_DIR = PROJECT_ROOT / "csv"
OMEKA_DIR = OUTPUT_DIR / "omeka"

# Create output directory
OMEKA_DIR.mkdir(parents=True, exist_ok=True)

# Type mapping: item_type -> OMEKA dc:type
ITEM_TYPE_MAP = {
    "document_page": "Text",
    "notecard": "Text",
    "ledger_or_register": "Dataset",
    "form": "Dataset",
    "letter": "Text",
    "pamphlet_or_brochure": "Text",
    "report": "Text",
    "meeting_minutes": "Text",
    "map_or_diagram": "Image",
    "photograph_of_display": "Image",
    "envelope_or_folder": "Text",
    "cover_or_title_page": "Text",
    "blank_or_unreadable": "Text",
}

# Collection assignment rules (based on session_group_id prefixes)
COLLECTION_RULES = {
    "CG": "District Consolidation Records",  # County Groups
    "S": "NYS Teachers' Association",         # General Sessions
    "AG": "NYS Teachers' Association",        # Advocacy Groups
}


def load_inventory() -> Dict[str, Dict]:
    """Load images_inventory_labeled.csv and return dict keyed by artifact_group_id."""
    inventory = {}
    inventory_path = CSV_DIR / "images_inventory_labeled.csv"

    with open(inventory_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            artifact_id = row.get('artifact_group_id')
            if artifact_id:
                if artifact_id not in inventory:
                    inventory[artifact_id] = []
                inventory[artifact_id].append(row)

    return inventory


def load_artifact_metadata(artifact_id: str) -> Optional[Dict]:
    """Load metadata.json for an artifact group."""
    metadata_path = ARCHIVE_DIR / artifact_id / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def load_artifact_transcription(artifact_id: str) -> str:
    """Load transcription.txt for an artifact group."""
    trans_path = ARCHIVE_DIR / artifact_id / "transcription.txt"
    if trans_path.exists():
        with open(trans_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def extract_image_filename(url: str) -> str:
    """Extract filename from GitHub URL."""
    # e.g., https://github.com/zmuhls/cs-archive/blob/main/raw/scans/img/IMG_0625.jpeg -> IMG_0625.jpeg
    parts = url.split('/')
    if parts:
        return parts[-1]
    return ""


def parse_district_consolidation() -> List[Dict]:
    """Parse District Consolidation markdown file."""
    items = []
    md_path = COLLECTIONS_DIR / "district-consolidation-by-county.md"

    if not md_path.exists():
        print(f"Warning: {md_path} not found")
        return items

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match collection entries
    # [Page N - Title](URL) followed by thumbnail
    # District Consolidation links to table extraction markdown files
    pattern = r'\- \[Page (\d+) - ([^\]]+)\]\(([^\)]+)\)'

    for match in re.finditer(pattern, content):
        page_num = match.group(1)
        title = match.group(2)
        url = match.group(3)

        # Convert markdown file reference to table thumbnail filename
        # URL is like: https://github.com/zmuhls/cs-archive/blob/main/output/ocr/tables/markdown/District-Consolidation-Data_100-116_page_3.md
        # We want: District-Consolidation-Data_100-116_page_3.jpg
        if "District-Consolidation-Data" in url:
            # Extract page number from URL
            thumb_filename = f"District-Consolidation-Data_100-116_page_{page_num}.jpg"
        else:
            # Fallback
            thumb_filename = extract_image_filename(url).replace('.md', '.jpg')

        items.append({
            'filename': thumb_filename,
            'table_page': page_num,
            'title': f'Page {page_num} - {title}',
            'collection': 'District Consolidation Records',
            'date': None,
            'location': None,
            'is_table': True,
        })

    return items


def parse_nys_local_records() -> List[Dict]:
    """Parse NYS Local Records collection from PDF OCR outputs."""
    items = []

    # Define the series we're including
    nys_series = {
        'South-Kortright-Roll-13': {
            'series': 'A4645',
            'title': 'South-Kortright Roll',
            'location': 'Delaware County',
        },
        'District-Notecard-Records': {
            'series': 'B0594',
            'title': 'District Notecard Records',
            'location': None,
        },
        'Amityville-Records': {
            'series': 'A4456',
            'title': 'Amityville Records',
            'location': 'Suffolk County',
        },
    }

    ocr_text_dir = PROJECT_ROOT / "output" / "ocr" / "text"

    for pdf_name, info in nys_series.items():
        # Find all page files for this PDF
        pattern = f"{pdf_name}_page_*.txt"
        page_files = sorted(ocr_text_dir.glob(pattern))

        for page_file in page_files:
            # Extract page number
            match = re.search(r'_page_(\d+)\.txt$', page_file.name)
            page_num = int(match.group(1)) if match else 0

            # Read transcription for description
            try:
                text = page_file.read_text(encoding='utf-8')[:500]
            except:
                text = ""

            # Extract date from text if possible
            date_match = re.search(r'\b(18\d{2}|19[0-4]\d)\b', text)
            date = date_match.group(1) if date_match else None

            items.append({
                'filename': page_file.name.replace('.txt', '.jpg'),
                'pdf_name': pdf_name,
                'page_number': page_num,
                'title': f"{info['title']} - Page {page_num}",
                'collection': "NYS Archives Local District Records",
                'date': date,
                'location': info['location'],
                'series': info['series'],
                'description': text.replace('\n', ' ').strip(),
                'is_pdf_page': True,
            })

    return items


def parse_nys_teachers() -> List[Dict]:
    """Parse NYS Teachers' Association markdown file."""
    items = []
    md_path = COLLECTIONS_DIR / "nys-teachers-association.md"

    if not md_path.exists():
        print(f"Warning: {md_path} not found")
        return items

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match items: [Date or Title](URL)
    # Look for markdown link patterns in the chronology section
    pattern = r'\- \[([^\]]+)\]\(([^\)]+)\)\s*\n.*?\n'

    # Split by decade sections to organize chronologically
    sections = re.split(r'^### (19\d0s|20\d0s|Undated|Chronology)', content, flags=re.MULTILINE)

    current_section = None
    for i, section_text in enumerate(sections):
        if i % 2 == 1:  # Odd indices are headers
            current_section = section_text.strip()
            continue

        # Find all links in this section
        for match in re.finditer(pattern, section_text):
            label = match.group(1)
            url = match.group(2)
            filename = extract_image_filename(url)

            # Extract date from label
            date_match = re.match(r'(\d{4}\??)', label)
            date = date_match.group(1) if date_match else current_section

            # Extract location if present
            location_match = re.search(r'—\s*([^()]+)', label)
            location = location_match.group(1).strip() if location_match else None

            items.append({
                'filename': filename,
                'title': label,
                'collection': "NYS Teachers' Association",
                'date': date,
                'location': location,
            })

    return items


def find_artifact_for_image(filename: str, inventory: Dict) -> Optional[str]:
    """Find artifact_group_id for a given image filename."""
    for artifact_id, rows in inventory.items():
        for row in rows:
            if row.get('filename') == filename:
                return artifact_id
    return None


def get_github_raw_url(filename: str, is_table: bool = False) -> str:
    """Generate GitHub raw content URL for an image or table."""
    if is_table:
        # Table thumbnail images are in output/ocr/tables/thumbs/
        return f"https://raw.githubusercontent.com/zmuhls/cs-archive/main/output/ocr/tables/thumbs/{filename}"
    else:
        # Regular images are in raw/scans/img/
        return f"https://raw.githubusercontent.com/zmuhls/cs-archive/main/raw/scans/img/{filename}"


def extract_decade(date_str: Optional[str]) -> Optional[str]:
    """Extract decade from date string (e.g., '1881' -> '1880s')."""
    if not date_str:
        return None

    # Remove ? suffix
    date_str = date_str.rstrip('?')

    if date_str == "Undated":
        return "Undated"

    # Try to parse year
    match = re.match(r'(\d{4})', date_str)
    if match:
        year = int(match.group(1))
        decade = (year // 10) * 10
        return f"{decade}s"

    return None


def generate_csv_row(item: Dict, inventory: Dict, artifact_metadata: Optional[Dict]) -> Optional[Dict]:
    """Generate CSV row for an item."""
    filename = item.get('filename')
    is_table = item.get('is_table', False)
    collection = item.get('collection', 'Other')

    # Handle table items (District Consolidation) differently
    if is_table:
        return {
            'collection': collection,
            'title': item.get('title', filename),
            'date': item.get('date') or '',
            'description': f"Extracted table showing district consolidation data for {item.get('title', 'New York State')}.",
            'type': 'Dataset',
            'spatial': item.get('location') or '',
            'subject': 'District Consolidation; Tables',
            'source': 'NYS Archives District Consolidation Data',
            'identifier': f"table_page_{item.get('table_page', '0')}",
            'file': get_github_raw_url(filename, is_table=True),
        }

    # Handle PDF page items (NYS Local Records)
    is_pdf_page = item.get('is_pdf_page', False)
    if is_pdf_page:
        series = item.get('series', '')
        pdf_name = item.get('pdf_name', '')
        page_num = item.get('page_number', 0)

        # Build subject tags
        subjects = ['Local School Records', f'NYS Archives Series {series}']
        if item.get('location'):
            subjects.append(item.get('location'))
        date = item.get('date')
        if date:
            decade = (int(date) // 10) * 10
            subjects.append(f'{decade}s')

        return {
            'collection': collection,
            'title': item.get('title', filename),
            'date': item.get('date') or '',
            'description': item.get('description', '')[:500],
            'type': 'Text',
            'spatial': item.get('location') or '',
            'subject': '; '.join(subjects),
            'source': f'NYS Archives Series {series}',
            'identifier': f'{pdf_name}_page_{page_num}',
            'file': f'https://raw.githubusercontent.com/zmuhls/cs-archive/main/output/ocr/text/{pdf_name}_page_{page_num}.txt',
        }

    # Handle regular image items (Teachers' Association)
    # Find artifact for this image
    artifact_id = find_artifact_for_image(filename, inventory)
    if not artifact_id:
        # Try without .jpeg extension for some images
        alt_filename = filename.replace('.jpeg', '').replace('.jpg', '')
        artifact_id = find_artifact_for_image(alt_filename, inventory)

    if not artifact_id:
        print(f"Warning: No artifact found for {filename}")
        return None

    # Load metadata
    metadata = artifact_metadata.get(artifact_id) if artifact_metadata else None
    if not metadata:
        metadata = load_artifact_metadata(artifact_id)

    if not metadata:
        print(f"Warning: No metadata for {artifact_id}")
        return None

    # Load transcription
    transcription = load_artifact_transcription(artifact_id)

    # Build description from transcription (first 500 chars)
    description = transcription[:500] + "..." if len(transcription) > 500 else transcription
    if not description:
        description = metadata.get('notes', '')

    # Extract decade for subject tags
    decade = extract_decade(item.get('date'))

    # Build subject tags
    subjects = []
    if metadata.get('subject'):
        subjects.append(metadata.get('subject'))
    if decade and decade != "Undated":
        subjects.append(decade)
    if item.get('location'):
        subjects.append(item.get('location'))

    # Determine item type
    item_type_raw = metadata.get('item_type', 'document_page')
    item_type_omeka = ITEM_TYPE_MAP.get(item_type_raw, 'Text')

    # Determine source
    if artifact_id.startswith('CG'):
        source = "NYS Archives District Consolidation Data"
    elif artifact_id.startswith('AG'):
        source = "NYS Teachers' Association Advocacy Materials"
    else:
        source = "NYS Teachers' Association Proceedings"

    return {
        'collection': collection,
        'title': item.get('title', metadata.get('subject', filename)),
        'date': item.get('date') or '',
        'description': description,
        'type': item_type_omeka,
        'spatial': item.get('location') or '',
        'subject': '; '.join(subjects),
        'source': source,
        'identifier': artifact_id,
        'file': get_github_raw_url(filename, is_table=False),
    }


def main():
    """Generate OMEKA CSV."""
    print("Loading inventory...")
    inventory = load_inventory()
    print(f"  Loaded {len(inventory)} artifacts from inventory")

    # Pre-load all metadata to avoid repeated file reads
    print("Pre-loading artifact metadata...")
    all_metadata = {}
    for artifact_id in inventory.keys():
        all_metadata[artifact_id] = load_artifact_metadata(artifact_id)
    print(f"  Loaded metadata for {len(all_metadata)} artifacts")

    print("\nParsing collection markdown files...")

    # Parse all three collections
    dc_items = parse_district_consolidation()
    print(f"  District Consolidation: {len(dc_items)} items")

    teachers_items = parse_nys_teachers()
    print(f"  NYS Teachers' Association: {len(teachers_items)} items")

    local_records_items = parse_nys_local_records()
    print(f"  NYS Local Records: {len(local_records_items)} items")

    total_items = len(dc_items) + len(teachers_items) + len(local_records_items)
    print(f"  Total: {total_items} items")

    # Generate CSV rows
    print("\nGenerating CSV rows...")
    csv_rows = []
    skipped = 0

    for item_list in [dc_items, teachers_items, local_records_items]:
        for item in item_list:
            row = generate_csv_row(item, inventory, all_metadata)
            if row:
                csv_rows.append(row)
            else:
                skipped += 1

    print(f"  Generated {len(csv_rows)} rows ({skipped} skipped)")

    # Write CSV
    output_path = OMEKA_DIR / "items_import.csv"
    fieldnames = ['collection', 'title', 'date', 'description', 'type', 'spatial', 'subject', 'source', 'identifier', 'file']

    print(f"\nWriting CSV to {output_path}...")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"  ✓ Wrote {len(csv_rows)} items")
    print(f"\nDone! CSV ready for OMEKA import.")


if __name__ == '__main__':
    main()
