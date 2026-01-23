#!/usr/bin/env python3
"""
Cleanup excessive [illegible] markers and repeated content in OCR outputs.

Handles:
1. Consecutive [illegible] markers (3+ in a row)
2. Repeated full lines (model hallucination loops)
3. Repeated section blocks (header + [illegible] + divider patterns)

Usage:
    python scripts/cleanup_illegible_markers.py --dry-run
    python scripts/cleanup_illegible_markers.py --artifacts  # Clean _artifacts/*.md
    python scripts/cleanup_illegible_markers.py --threshold 50
"""

import re
from pathlib import Path
from typing import List, Tuple
import json
from datetime import datetime
from difflib import SequenceMatcher

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def similarity(a: str, b: str) -> float:
    """Calculate text similarity ratio."""
    return SequenceMatcher(None, a.strip(), b.strip()).ratio()


def is_repeated_line(line: str, prev_lines: list, threshold: float = 0.90) -> bool:
    """Check if line is a repeat of recent lines."""
    line_stripped = line.strip()
    if not line_stripped or len(line_stripped) < 20:
        return False
    for prev in prev_lines[-5:]:
        if similarity(line_stripped, prev.strip()) >= threshold:
            return True
    return False


def clean_repeated_lines(text: str) -> Tuple[str, int]:
    """Remove consecutive repeated lines. Returns (cleaned_text, lines_removed)."""
    lines = text.split('\n')
    result = []
    removed = 0
    seen_repeated = False
    prev_content_lines = []
    in_frontmatter = False
    frontmatter_count = 0

    for line in lines:
        stripped = line.strip()

        # Track YAML frontmatter (skip processing inside it)
        if stripped == '---':
            frontmatter_count += 1
            in_frontmatter = (frontmatter_count == 1)
            result.append(line)
            continue

        # Don't process lines inside frontmatter
        if in_frontmatter or frontmatter_count < 2:
            result.append(line)
            continue

        # Keep empty lines unless in repeat mode
        if not stripped:
            if not seen_repeated:
                result.append(line)
            continue

        # Check if this line repeats recent content
        if is_repeated_line(line, prev_content_lines):
            if not seen_repeated:
                seen_repeated = True
            removed += 1
            continue
        else:
            if seen_repeated:
                result.append("")
                result.append("[repeated content truncated]")
                result.append("")
                seen_repeated = False

            result.append(line)
            prev_content_lines.append(line)
            if len(prev_content_lines) > 5:
                prev_content_lines.pop(0)

    if seen_repeated:
        result.append("")
        result.append("[repeated content truncated]")

    return '\n'.join(result), removed


def clean_repeated_blocks(text: str) -> Tuple[str, int]:
    """Remove repeated header/[illegible]/divider blocks. Returns (cleaned, count)."""
    # Pattern: **HEADER** + [illegible] + * * * repeated 3+ times
    pattern = re.compile(
        r'((\*\*[A-Z][A-Z\s]+\*\*)\s*\n\s*\[illegible\]\s*\n\s*\* \* \*\s*\n?){3,}',
        re.MULTILINE
    )

    count = 0
    def replace_block(match):
        nonlocal count
        blocks = match.group(0)
        # Count how many blocks
        block_count = len(re.findall(r'\*\*[A-Z][A-Z\s]+\*\*', blocks))
        count += block_count - 1

        # Extract header from first block
        header_match = re.search(r'\*\*([A-Z][A-Z\s]+)\*\*', blocks)
        header = header_match.group(1) if header_match else "SECTION"

        return f"**{header}**\n\n[illegible - {block_count} similar sections]\n\n"

    cleaned = pattern.sub(replace_block, text)
    return cleaned, count


def consolidate_illegible_markers(text: str) -> Tuple[str, dict]:
    """
    Consolidate consecutive [illegible] markers.

    Rules:
    1. Replace 3+ consecutive [illegible] lines with single marker + count
    2. Preserve single/double markers (legitimate illegible words)
    3. Track statistics for reporting
    4. Treat blank lines between [illegible] as part of the sequence

    Args:
        text: Original OCR text

    Returns:
        Tuple of (cleaned_text, statistics_dict)
    """
    lines = text.split('\n')
    cleaned_lines = []
    illegible_count = 0
    consecutive_count = 0
    pending_blanks = 0  # Track blank lines between illegible markers
    blocks_consolidated = 0
    total_markers_removed = 0

    for line in lines:
        stripped = line.strip()

        # Track blank lines (might be between illegible markers)
        if not stripped:
            if consecutive_count > 0:
                pending_blanks += 1
            else:
                cleaned_lines.append(line)
            continue

        # Check if line is just [illegible] marker
        if stripped == '[illegible]':
            consecutive_count += 1
            illegible_count += 1
            pending_blanks = 0  # Reset - blank lines were part of sequence
        else:
            # If we had 3+ consecutive markers, consolidate
            if consecutive_count >= 3:
                cleaned_lines.append(f'[illegible - {consecutive_count} consecutive lines unreadable]')
                cleaned_lines.append('')
                blocks_consolidated += 1
                total_markers_removed += (consecutive_count - 1)
            elif consecutive_count > 0:
                # Keep 1-2 markers as-is (legitimate illegible words)
                for _ in range(consecutive_count):
                    cleaned_lines.append('[illegible]')
                    cleaned_lines.append('')

            consecutive_count = 0
            pending_blanks = 0
            cleaned_lines.append(line)

    # Handle trailing illegible markers
    if consecutive_count >= 3:
        cleaned_lines.append(f'[illegible - {consecutive_count} consecutive lines unreadable]')
        blocks_consolidated += 1
        total_markers_removed += (consecutive_count - 1)
    elif consecutive_count > 0:
        for _ in range(consecutive_count):
            cleaned_lines.append('[illegible]')
            cleaned_lines.append('')

    cleaned_text = '\n'.join(cleaned_lines)

    # Remove excessive blank lines (max 2 consecutive)
    cleaned_text = re.sub(r'\n\n\n+', '\n\n', cleaned_text)

    stats = {
        'original_illegible_count': illegible_count,
        'blocks_consolidated': blocks_consolidated,
        'markers_removed': total_markers_removed,
        'markers_remaining': illegible_count - total_markers_removed,
        'original_length': len(text),
        'cleaned_length': len(cleaned_text),
        'size_reduction': len(text) - len(cleaned_text),
        'reduction_percentage': round((1 - len(cleaned_text) / len(text)) * 100, 2) if text else 0
    }

    return cleaned_text, stats


def cleanup_file(file_path: Path, dry_run: bool = False, is_artifact: bool = False) -> dict:
    """
    Clean up a single file.

    Args:
        file_path: Path to text file
        dry_run: If True, analyze but don't modify
        is_artifact: If True, apply repeated line/block cleaning

    Returns:
        Dictionary with cleanup results
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        original_text = f.read()

    # For artifacts, also clean repeated content
    lines_removed = 0
    blocks_removed = 0
    if is_artifact:
        cleaned_text, blocks_removed = clean_repeated_blocks(original_text)
        cleaned_text, lines_removed = clean_repeated_lines(cleaned_text)
        # Also consolidate illegible markers
        cleaned_text, stats = consolidate_illegible_markers(cleaned_text)
    else:
        cleaned_text, stats = consolidate_illegible_markers(original_text)

    # Add extra stats for artifacts
    stats['lines_removed'] = lines_removed
    stats['blocks_removed'] = blocks_removed

    has_changes = (stats['blocks_consolidated'] > 0 or lines_removed > 0 or blocks_removed > 0)

    result = {
        'file': str(file_path.name),
        'full_path': str(file_path),
        'original_size': len(original_text),
        'cleaned_size': len(cleaned_text),
        'size_reduction': len(original_text) - len(cleaned_text),
        'stats': stats
    }

    if not dry_run and has_changes:
        # Backup original (skip for artifacts - use git instead)
        if not is_artifact:
            backup_path = file_path.with_suffix('.txt.backup')
            if not backup_path.exists():
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_text)
                result['backed_up'] = str(backup_path)
            else:
                result['backed_up'] = f"{backup_path} (already exists)"

        # Write cleaned version
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

        result['action'] = 'cleaned'
    else:
        result['action'] = 'skipped' if not has_changes else 'dry_run'

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Clean up excessive [illegible] markers and repeated content in OCR outputs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be done
  python scripts/cleanup_illegible_markers.py --dry-run

  # Clean artifact markdown files
  python scripts/cleanup_illegible_markers.py --artifacts

  # Clean OCR text files with 50+ illegible markers
  python scripts/cleanup_illegible_markers.py --threshold 50

  # Clean all files (threshold 0)
  python scripts/cleanup_illegible_markers.py --threshold 0
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without modifying files'
    )
    parser.add_argument(
        '--artifacts',
        action='store_true',
        help='Clean _artifacts/*.md files instead of OCR text files'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=3,
        help='Only process files with N+ illegible markers (default: 3)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=PROJECT_ROOT / 'output' / 'ocr' / 'text',
        help='Directory containing OCR text files (default: output/ocr/text)'
    )

    args = parser.parse_args()

    # Determine directory and file pattern
    if args.artifacts:
        target_dir = PROJECT_ROOT / '_artifacts'
        file_pattern = '*.md'
        file_type = 'artifact'
    else:
        target_dir = args.output_dir
        file_pattern = '*.txt'
        file_type = 'text'

    if not target_dir.exists():
        print(f"ERROR: Directory not found: {target_dir}")
        return 1

    print("=" * 70)
    print("OCR CLEANUP - ILLEGIBLE MARKERS & REPEATED CONTENT")
    print("=" * 70)
    print()
    print(f"Directory:  {target_dir}")
    print(f"File type:  {file_pattern}")
    print(f"Threshold:  {args.threshold} [illegible] markers")
    print(f"Mode:       {'DRY RUN (no changes)' if args.dry_run else 'LIVE (will modify files)'}")
    print()
    print("-" * 70)
    print()

    results = []
    skipped_count = 0

    # Scan files
    print(f"Scanning for {file_pattern} files...")
    files = sorted(target_dir.glob(file_pattern))
    print(f"Found {len(files)} files")
    print()

    for file_path in files:
        # Skip backup files
        if '.backup' in file_path.suffixes:
            continue

        # Count illegible markers
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            count = content.count('[illegible]')

        if count >= args.threshold:
            print(f"Processing {file_path.name[:55]:55s} ({count:4d} markers)...", end=' ')
            result = cleanup_file(file_path, dry_run=args.dry_run, is_artifact=args.artifacts)
            results.append(result)

            has_changes = (
                result['stats']['blocks_consolidated'] > 0 or
                result['stats'].get('lines_removed', 0) > 0 or
                result['stats'].get('blocks_removed', 0) > 0
            )

            if has_changes:
                size_kb = result['size_reduction'] / 1024
                lines_rm = result['stats'].get('lines_removed', 0)
                blocks_rm = result['stats'].get('blocks_removed', 0)
                markers_rm = result['stats']['markers_removed']
                print(f"✓ -{size_kb:.1f} KB", end='')
                if lines_rm:
                    print(f" | -{lines_rm} lines", end='')
                if blocks_rm:
                    print(f" | -{blocks_rm} blocks", end='')
                if markers_rm:
                    print(f" | -{markers_rm} markers", end='')
                print()
            else:
                print("○ No changes needed")
        else:
            skipped_count += 1

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Files scanned:       {len(files)}")
    print(f"Below threshold:     {skipped_count}")
    print(f"Processed:           {len(results)}")

    if results:
        total_cleaned = sum(1 for r in results if r['action'] == 'cleaned')
        total_blocks = sum(r['stats']['blocks_consolidated'] for r in results)
        total_removed = sum(r['stats']['markers_removed'] for r in results)
        total_lines_rm = sum(r['stats'].get('lines_removed', 0) for r in results)
        total_blocks_rm = sum(r['stats'].get('blocks_removed', 0) for r in results)
        total_saved_bytes = sum(r['size_reduction'] for r in results)
        total_saved_kb = total_saved_bytes / 1024

        print(f"Files cleaned:       {total_cleaned}")
        if total_lines_rm:
            print(f"Repeated lines rm:   {total_lines_rm:,}")
        if total_blocks_rm:
            print(f"Repeated blocks rm:  {total_blocks_rm:,}")
        print(f"Illegible consol.:   {total_blocks}")
        print(f"Markers removed:     {total_removed:,}")
        print(f"Space saved:         {total_saved_kb:.1f} KB ({total_saved_bytes:,} bytes)")
        print()

        if args.dry_run:
            print("DRY RUN - No files were modified")
        else:
            if not args.artifacts:
                print(f"✓ Backups saved as *.txt.backup")
            print(f"✓ Cleaned files saved")

        # Top 10 most affected
        if len(results) > 0:
            print()
            print("Top 10 most affected files:")
            sorted_results = sorted(
                results,
                key=lambda r: r['size_reduction'],
                reverse=True
            )[:10]

            for i, r in enumerate(sorted_results, 1):
                size_kb = r['size_reduction'] / 1024
                print(f"  {i:2d}. {r['file'][:50]:50s} (-{size_kb:.1f} KB)")

    print()

    # Save report
    report_path = PROJECT_ROOT / 'output' / 'ocr' / 'reports' / 'illegible_cleanup_report.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'threshold': args.threshold,
            'dry_run': args.dry_run,
            'files_scanned': len(files),
            'files_below_threshold': skipped_count,
            'files_processed': len(results),
            'files_cleaned': sum(1 for r in results if r['action'] == 'cleaned'),
            'total_blocks_consolidated': sum(r['stats']['blocks_consolidated'] for r in results),
            'total_markers_removed': sum(r['stats']['markers_removed'] for r in results),
            'total_size_reduction_bytes': sum(r['size_reduction'] for r in results),
            'results': results
        }, f, indent=2)

    print(f"Report saved: {report_path}")
    print()
    print("=" * 70)

    return 0


if __name__ == '__main__':
    exit(main())
