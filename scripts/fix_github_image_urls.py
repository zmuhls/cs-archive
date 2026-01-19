#!/usr/bin/env python3
"""
Convert relative image paths in collection markdown files to GitHub media CDN URLs.

GitHub LFS files need to use media.githubusercontent.com URLs to display in markdown previews.
"""

import re
from pathlib import Path

COLLECTIONS_DIR = Path('output/collections')
GITHUB_REPO = "zmuhls/cs-archive"
BRANCH = "main"

def convert_relative_to_media_url(relative_path: str) -> str:
    """
    Convert relative path to GitHub media CDN URL.

    Example:
        ../../raw/scans/img/IMG_0625.jpeg
        → https://media.githubusercontent.com/media/zmuhls/cs-archive/main/raw/scans/img/IMG_0625.jpeg
    """
    # Remove leading ../../ or similar
    clean_path = relative_path.replace('../', '')

    return f"https://media.githubusercontent.com/media/{GITHUB_REPO}/{BRANCH}/{clean_path}"


def extract_filename_from_url(url: str) -> str:
    """Extract filename from Dropbox URL, GitHub URL, or relative path."""
    # Handle existing GitHub URLs (media.githubusercontent.com or github.com)
    if 'githubusercontent.com' in url or ('github.com' in url and '/blob/' in url):
        # Extract path after /main/ or /blob/main/
        match = re.search(r'/(?:blob/)?main/(.+?)(?:\?|$)', url)
        if match:
            return match.group(1)

    # Handle Dropbox URLs
    if 'dropbox.com' in url:
        # Extract path between domain and query string
        match = re.search(r'/scans/img/([^?]+)', url)
        if match:
            return f"raw/scans/img/{match.group(1)}"

    # Handle derived/thumbs paths
    if 'derived/thumbs' in url:
        match = re.search(r'derived/thumbs/([^?]+)', url)
        if match:
            return f"derived/thumbs/{match.group(1)}"

    # Handle relative paths
    return url.replace('../', '')


def update_markdown_file(md_file: Path) -> int:
    """
    Update image links in a markdown file.

    Returns number of replacements made.
    """
    content = md_file.read_text(encoding='utf-8')
    original_content = content

    # Pattern for markdown image links: [![alt](path)](path)
    # Handles both Dropbox URLs and relative paths

    def replace_link(match):
        alt_text = match.group(1)
        thumb_path = match.group(2)
        full_path = match.group(3)

        # Extract filenames
        thumb_clean = extract_filename_from_url(thumb_path)
        full_clean = extract_filename_from_url(full_path)

        # Thumbnail displays via media CDN
        thumb_url = f"https://media.githubusercontent.com/media/{GITHUB_REPO}/{BRANCH}/{thumb_clean}"

        # Link goes to GitHub's blob view (for viewing the file)
        full_url = f"https://github.com/{GITHUB_REPO}/blob/{BRANCH}/{full_clean}"

        return f"[![{alt_text}]({thumb_url})]({full_url})"

    # Pattern matches the full structure: [![alt](thumb)](link) [text](textlink)
    # We'll replace it with just: [![alt](thumb)](link)
    full_pattern = r'\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)\s+\[[^\]]+\]\([^)]+\)'
    content = re.sub(full_pattern, replace_link, content)

    # Count total changes
    num_changes = len(re.findall(full_pattern, original_content))

    if content != original_content:
        md_file.write_text(content, encoding='utf-8')

    return num_changes


def main():
    print("Fixing GitHub image URLs in collection markdown files...")
    print("-" * 70)

    if not COLLECTIONS_DIR.exists():
        print(f"Error: {COLLECTIONS_DIR} not found")
        return

    md_files = list(COLLECTIONS_DIR.glob('*.md'))

    if not md_files:
        print(f"No markdown files found in {COLLECTIONS_DIR}")
        return

    print(f"Found {len(md_files)} collection files\n")

    total_changes = 0
    for md_file in md_files:
        num_changes = update_markdown_file(md_file)
        if num_changes > 0:
            print(f"✓ {md_file.name}: updated {num_changes} image links")
            total_changes += num_changes
        else:
            print(f"  {md_file.name}: no changes needed")

    print("\n" + "=" * 70)
    print(f"Total: {total_changes} image links updated")
    print("\nImages will now display properly on GitHub!")
    print("Commit and push these changes:")
    print("  git add output/collections/")
    print("  git commit -m \"fix image urls for github lfs display\"")
    print("  git push origin main")


if __name__ == '__main__':
    main()
