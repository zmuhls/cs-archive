#!/usr/bin/env python3
"""
Clean up OCR hallucination repetitions from artifact markdown files.
Detects repeated phrases and collapses them to single occurrences.
"""

import re
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

ARTIFACTS_DIR = PROJECT_ROOT / "_artifacts"

# Minimum phrase length (words) to consider
MIN_PHRASE_WORDS = 5
# Minimum phrase length (chars) to consider
MIN_PHRASE_CHARS = 20
# Minimum repetitions to trigger cleanup
MIN_REPETITIONS = 4


def extract_content_after_frontmatter(text: str) -> tuple[str, str]:
    """Split markdown into frontmatter and content."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = f"---{parts[1]}---"
            content = parts[2]
            return frontmatter, content
    return "", text


def find_repeated_phrases(text: str) -> list[tuple[str, int]]:
    """Find phrases that repeat excessively."""
    words = text.split()
    if len(words) < MIN_PHRASE_WORDS * 2:
        return []

    phrase_counts = Counter()

    # Build n-grams of MIN_PHRASE_WORDS words
    for i in range(len(words) - MIN_PHRASE_WORDS + 1):
        phrase = " ".join(words[i:i + MIN_PHRASE_WORDS])
        if len(phrase) >= MIN_PHRASE_CHARS:
            phrase_counts[phrase] += 1

    # Filter to phrases that repeat excessively
    repeated = [(phrase, count) for phrase, count in phrase_counts.items()
                if count >= MIN_REPETITIONS]

    # Sort by count descending
    repeated.sort(key=lambda x: -x[1])

    return repeated


def clean_illegible_spam(text: str) -> tuple[str, int]:
    """Clean up excessive [illegible] markers."""
    # Pattern: [illegible] repeated 4+ times with only whitespace between
    pattern = r"(\[illegible\]\s*){4,}"
    matches = list(re.finditer(pattern, text))
    removed = sum(m.group().count("[illegible]") - 1 for m in matches)
    text = re.sub(pattern, "[illegible] ", text)
    return text, removed


def clean_year_spam(text: str) -> tuple[str, int]:
    """Clean up year repetition like '1940 1940 1940'."""
    pattern = r"(\b\d{4}\b)(\s+\1){3,}"
    matches = list(re.finditer(pattern, text))
    removed = sum(m.group().count(m.group(1)) - 1 for m in matches)
    text = re.sub(pattern, r"\1", text)
    return text, removed


def clean_marker_spam(text: str) -> tuple[str, int]:
    """Clean up repeated markdown markers like **[illegible]** --- **[illegible]**."""
    # Pattern for repeated illegible with formatting
    pattern = r"(\*{0,2}\[illegible\]\*{0,2}\s*[-—]*\s*){3,}"
    matches = list(re.finditer(pattern, text))
    removed = len(matches) * 2  # rough estimate
    text = re.sub(pattern, "[illegible] ", text)
    return text, removed


def collapse_repetitions(text: str, max_iterations: int = 20) -> tuple[str, int]:
    """
    Collapse repeated phrases to single occurrence.
    Returns (cleaned_text, repetitions_removed).
    """
    total_removed = 0

    # First, clean special patterns
    text, removed = clean_illegible_spam(text)
    total_removed += removed

    text, removed = clean_year_spam(text)
    total_removed += removed

    text, removed = clean_marker_spam(text)
    total_removed += removed

    # Then handle general phrase repetition
    for iteration in range(max_iterations):
        repeated = find_repeated_phrases(text)
        if not repeated:
            break

        made_change = False
        for phrase, count in repeated[:5]:  # Try top 5 phrases
            if count < MIN_REPETITIONS:
                continue

            # Escape for regex
            escaped = re.escape(phrase)

            # Try multiple patterns for repetition
            patterns = [
                # Direct repetition with whitespace/punctuation
                f"({escaped})(?:\\s*[.,;:!?\\-—]*\\s*{escaped})+",
                # Repetition with newlines
                f"({escaped})(?:\\s*\\n\\s*{escaped})+",
            ]

            for pattern in patterns:
                new_text = re.sub(pattern, r"\1", text, flags=re.MULTILINE)
                if new_text != text:
                    removed = text.count(phrase) - new_text.count(phrase)
                    total_removed += removed
                    text = new_text
                    made_change = True
                    break

            if made_change:
                break

        if not made_change:
            break

    # Clean up excessive whitespace
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    text = re.sub(r' {3,}', '  ', text)

    return text, total_removed


def clean_file(filepath: Path, dry_run: bool = False) -> tuple[bool, int, list]:
    """
    Clean a single artifact file.
    Returns (changed, repetitions_removed, issues_found).
    """
    content = filepath.read_text(encoding="utf-8")
    frontmatter, body = extract_content_after_frontmatter(content)

    # Find issues before cleaning
    issues = find_repeated_phrases(body)

    if not issues:
        return False, 0, []

    # Clean the body
    cleaned_body, removed = collapse_repetitions(body)

    if removed == 0:
        return False, 0, issues

    if not dry_run:
        # Reconstruct and write
        new_content = frontmatter + cleaned_body
        filepath.write_text(new_content, encoding="utf-8")

    return True, removed, issues


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Clean OCR repetition hallucinations")
    parser.add_argument("--dry-run", action="store_true", help="Report issues without fixing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    if not ARTIFACTS_DIR.exists():
        print(f"Error: {ARTIFACTS_DIR} not found")
        return

    files = list(ARTIFACTS_DIR.glob("*.md"))
    print(f"Scanning {len(files)} artifact files...")

    total_cleaned = 0
    total_removed = 0
    all_issues = []

    for filepath in sorted(files):
        changed, removed, issues = clean_file(filepath, dry_run=args.dry_run)

        if issues:
            all_issues.append((filepath.name, issues))
            if args.verbose or args.dry_run:
                print(f"\n{filepath.name}:")
                for phrase, count in issues[:3]:
                    print(f"  \"{phrase[:40]}...\" x{count}")

        if changed:
            total_cleaned += 1
            total_removed += removed
            if not args.dry_run:
                print(f"Cleaned: {filepath.name} (-{removed} repetitions)")

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Summary:")
    print(f"  Files with issues: {len(all_issues)}")
    print(f"  Files cleaned: {total_cleaned}")
    print(f"  Repetitions removed: {total_removed}")


if __name__ == "__main__":
    main()
