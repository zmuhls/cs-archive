#!/usr/bin/env python3
"""
Extract structured data from notecard OCR output.

This script demonstrates parsing plain text notecard transcriptions
into structured JSON format with:
- School/district identification
- Location information (county, town)
- Chronological timeline of administrative events
- Event categorization (admission, merger, name change, etc.)

Run with: python scripts/extract_notecard_structure.py [notecard_text_file]
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def parse_date(date_str: str) -> Optional[Dict[str, str]]:
    """
    Parse various date formats found in notecards.

    Examples:
        "4 F. 1923" -> February 4, 1923
        "1 May 1923" -> May 1, 1923
        "R 9 Jan 1880" -> January 9, 1880 (R prefix for "Registered")
        "6/26/64" -> June 26, 1964

    Returns dict with:
        - date_raw: original string
        - date_parsed: ISO format (if possible)
        - date_year: year (if extractable)
    """
    result = {
        "date_raw": date_str.strip(),
        "date_parsed": None,
        "date_year": None
    }

    # Extract year with regex
    year_match = re.search(r'\b(18\d{2}|19\d{2}|20\d{2})\b', date_str)
    if year_match:
        result["date_year"] = int(year_match.group(1))

    # Try to parse common formats
    date_clean = date_str.strip()

    # Remove prefixes like "R " (Registered)
    date_clean = re.sub(r'^[A-Z]\s+', '', date_clean)

    # Format: "6/26/64"
    if re.match(r'\d{1,2}/\d{1,2}/\d{2,4}', date_clean):
        parts = date_clean.split('/')
        month, day = int(parts[0]), int(parts[1])
        year = int(parts[2])
        if year < 100:
            year = 1900 + year if year >= 50 else 2000 + year
        result["date_parsed"] = f"{year:04d}-{month:02d}-{day:02d}"
        result["date_year"] = year

    return result


def categorize_event(event_text: str) -> str:
    """
    Categorize an event based on keywords in the description.

    Categories:
        - admission_application
        - admitted
        - merged
        - name_change
        - re_registered
        - advanced_status
        - charter_granted
        - ranked
        - provisionally_chartered
        - other
    """
    text_lower = event_text.lower()

    if 'application' in text_lower and 'admission' in text_lower:
        return 'admission_application'
    elif 'admitted' in text_lower:
        return 'admitted'
    elif 'merged' in text_lower or 'consolidated' in text_lower:
        return 'merged'
    elif 'name' in text_lower and 'chang' in text_lower:
        return 'name_change'
    elif 're-registered' in text_lower or 'reregistered' in text_lower:
        return 're_registered'
    elif 'advanced' in text_lower or 'adv.' in text_lower:
        return 'advanced_status'
    elif 'charter' in text_lower and 'grant' in text_lower:
        return 'charter_granted'
    elif 'ranked' in text_lower:
        return 'ranked'
    elif 'prov' in text_lower and 'chart' in text_lower:
        return 'provisionally_chartered'
    else:
        return 'other'


def parse_notecard_text(text: str) -> List[Dict]:
    """
    Parse plain text notecard transcription into structured format.

    Returns list of card objects, each with:
        - school_name: name and location
        - county: extracted county name
        - timeline: list of event objects
    """
    cards = []

    # Split by horizontal rule separator
    card_blocks = text.split('---')

    for block in card_blocks:
        block = block.strip()
        if not block:
            continue

        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if not lines:
            continue

        # First line is typically the header
        header = lines[0]

        # Extract county from header (e.g., "(Monroe Co.)")
        county_match = re.search(r'\(([^)]+)\s+Co\.?\)', header)
        county = county_match.group(1) if county_match else None

        # Parse timeline entries
        timeline = []
        for line in lines[1:]:
            # Skip annotation-only lines
            if line.startswith('[') and line.endswith(']'):
                continue

            # Remove text type annotations
            clean_line = re.sub(r'\[(?:typed|handwritten):\s*\]', '', line).strip()

            # Try to split date from event
            # Pattern: date at start, then dash or hyphen, then event description
            date_event_match = re.match(r'^(.+?)\s*[-–]\s*(.+)$', clean_line)

            if date_event_match:
                date_part = date_event_match.group(1).strip()
                event_part = date_event_match.group(2).strip()

                date_info = parse_date(date_part)
                event_type = categorize_event(event_part)

                timeline.append({
                    "date": date_info,
                    "event": event_part,
                    "event_type": event_type,
                    "raw_line": line
                })
            else:
                # No clear date-event split, add as-is
                timeline.append({
                    "date": None,
                    "event": clean_line,
                    "event_type": "other",
                    "raw_line": line
                })

        cards.append({
            "school_name": header,
            "county": county,
            "timeline": timeline
        })

    return cards


def process_notecard_file(text_path: Path) -> Dict:
    """
    Process a notecard OCR text file into structured JSON.

    Args:
        text_path: Path to OCR text file (e.g., District-Notecard-Records_page_10.txt)

    Returns:
        Structured data with metadata and parsed cards
    """
    with open(text_path, 'r', encoding='utf-8') as f:
        text_content = f.read()

    # Parse cards from text
    cards = parse_notecard_text(text_content)

    # Extract page number from filename
    page_match = re.search(r'page_(\d+)', text_path.name)
    page_number = int(page_match.group(1)) if page_match else None

    return {
        "source_file": str(text_path),
        "page_number": page_number,
        "processed_at": datetime.now().isoformat(),
        "cards_count": len(cards),
        "cards": cards
    }


def main():
    """Demonstrate structured extraction on a sample notecard file."""

    if len(sys.argv) > 1:
        text_path = Path(sys.argv[1])
    else:
        # Default: use first available notecard file
        text_dir = PROJECT_ROOT / "output" / "ocr" / "text"
        notecard_files = sorted(text_dir.glob("District-Notecard-Records_page_*.txt"))

        if not notecard_files:
            print("ERROR: No notecard files found in output/ocr/text/")
            print("Run 'python scripts/process_notecards.py' first to generate OCR output.")
            return

        text_path = notecard_files[0]
        print(f"Using sample file: {text_path.name}")
        print()

    if not text_path.exists():
        print(f"ERROR: File not found: {text_path}")
        return

    # Process the file
    print(f"Processing: {text_path}")
    print()

    structured_data = process_notecard_file(text_path)

    # Display results
    print("=" * 70)
    print("STRUCTURED EXTRACTION RESULTS")
    print("=" * 70)
    print()
    print(f"Source: {structured_data['source_file']}")
    print(f"Page number: {structured_data['page_number']}")
    print(f"Cards found: {structured_data['cards_count']}")
    print()

    for i, card in enumerate(structured_data['cards'], 1):
        print(f"--- Card {i} ---")
        print(f"School: {card['school_name']}")
        print(f"County: {card['county']}")
        print(f"Timeline entries: {len(card['timeline'])}")
        print()

        for event in card['timeline']:
            if event['date']:
                date_str = event['date']['date_raw']
                year = event['date'].get('date_year', '????')
                print(f"  [{year}] {date_str}: {event['event']}")
                print(f"         Type: {event['event_type']}")
            else:
                print(f"  [????] {event['event']}")
            print()
        print()

    # Save JSON output
    output_path = text_path.parent.parent / "structured" / f"{text_path.stem}_structured.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print(f"Structured JSON saved to: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
