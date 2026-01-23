#!/usr/bin/env python3
"""
Link Audit Script for Common School Archive Jekyll Site

Audits all links within two degrees of separation from main navigation pages.
Detects broken links, improper baseurl handling, and pattern violations.

Usage:
    python scripts/link_audit.py [--build] [--check-external]
"""

import os
import re
import csv
import argparse
import subprocess
from pathlib import Path
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import urlparse
import urllib.request
import urllib.error


# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BASEURL = "/cs-archive"
SITE_DIR = PROJECT_ROOT / "_site"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Pages to audit (two degrees from main nav)
MAIN_NAV_PAGES = [
    "index.md",
    "about.md",
    "map.md",
    "search.md",
    "collections/index.md",
    "browse/index.md",
]

FIRST_DEGREE_DIRS = [
    "collections",
    "browse",
]

SECOND_DEGREE_DIRS = [
    "_artifacts",
]

# Directories to scan for source files
SCAN_DIRS = [
    "",  # root
    "collections",
    "browse",
    "_artifacts",
    "_layouts",
    "_includes",
    "assets/maps",
]

# Directories to exclude (already excluded from Jekyll build)
EXCLUDE_DIRS = ["docs", "output", "dev", "raw", "scripts", "node_modules", "vendor"]

# Issue patterns to detect
PATTERNS = {
    "hardcoded_baseurl": {
        "regex": r'(?:href|src)=["\']\/cs-archive\/[^"\']*["\']',
        "description": "Hardcoded /cs-archive/ path (should use relative_url filter)",
        "severity": "warning",
    },
    "hardcoded_domain": {
        "regex": r'zmuhls\.github\.io\/cs-archive',
        "description": "Hardcoded GitHub Pages domain",
        "severity": "warning",
    },
    "external_cdn_image": {
        "regex": r'raw\.githubusercontent\.com\/zmuhls\/cs-archive',
        "description": "External GitHub CDN URL for image (could use local path)",
        "severity": "info",
    },
    "absolute_path_html": {
        "regex": r'(?:href|src)=["\']\/(?!\/)[^"\']+["\']',
        "description": "Absolute path in HTML (may need relative_url filter)",
        "severity": "info",
    },
    "markdown_absolute_link": {
        "regex": r'\]\(\/[^)]+\)',
        "description": "Absolute path in Markdown link (should use relative_url filter)",
        "severity": "warning",
    },
}


class LinkExtractor(HTMLParser):
    """Extract href and src attributes from HTML."""

    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "a" and "href" in attrs_dict:
            self.links.append(attrs_dict["href"])
        elif tag in ("img", "script", "link") and "src" in attrs_dict:
            self.images.append(attrs_dict["src"])
        elif tag == "link" and "href" in attrs_dict:
            self.images.append(attrs_dict["href"])


def find_source_files():
    """Find all source files to audit."""
    files = []
    extensions = {".md", ".html", ".js"}

    for scan_dir in SCAN_DIRS:
        dir_path = PROJECT_ROOT / scan_dir if scan_dir else PROJECT_ROOT
        if not dir_path.exists():
            continue

        for ext in extensions:
            if scan_dir:
                pattern = f"**/*{ext}"
            else:
                pattern = f"*{ext}"

            for file_path in dir_path.glob(pattern):
                # Skip excluded directories
                rel_path = file_path.relative_to(PROJECT_ROOT)
                if any(part in EXCLUDE_DIRS for part in rel_path.parts):
                    continue
                files.append(file_path)

    return files


def scan_file_for_patterns(file_path):
    """Scan a file for problematic link patterns."""
    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
    except Exception as e:
        return [{"line": 0, "issue_type": "read_error", "match": str(e), "severity": "error"}]

    for pattern_name, pattern_info in PATTERNS.items():
        regex = re.compile(pattern_info["regex"], re.IGNORECASE)

        for line_num, line in enumerate(lines, 1):
            for match in regex.finditer(line):
                issues.append({
                    "line": line_num,
                    "issue_type": pattern_name,
                    "match": match.group(0),
                    "severity": pattern_info["severity"],
                    "description": pattern_info["description"],
                })

    return issues


def extract_links_from_html(html_file):
    """Extract all links from an HTML file."""
    try:
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return [], []

    parser = LinkExtractor()
    try:
        parser.feed(content)
    except Exception:
        pass

    return parser.links, parser.images


def build_site():
    """Build the Jekyll site."""
    print("Building Jekyll site...")
    result = subprocess.run(
        ["bundle", "exec", "jekyll", "build"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Build failed: {result.stderr}")
        return False
    print("Build complete.")
    return True


def collect_site_links():
    """Collect all links from the built site."""
    if not SITE_DIR.exists():
        print(f"Site directory not found: {SITE_DIR}")
        return {}, {}

    all_links = defaultdict(list)
    all_images = defaultdict(list)

    for html_file in SITE_DIR.glob("**/*.html"):
        rel_path = html_file.relative_to(SITE_DIR)
        links, images = extract_links_from_html(html_file)

        for link in links:
            all_links[str(rel_path)].append(link)
        for img in images:
            all_images[str(rel_path)].append(img)

    return dict(all_links), dict(all_images)


def validate_internal_link(link, site_dir):
    """Check if an internal link resolves to an existing file."""
    if not link or link.startswith(("#", "mailto:", "tel:", "javascript:")):
        return True, "skipped"

    parsed = urlparse(link)

    # External link
    if parsed.scheme in ("http", "https"):
        return True, "external"

    # Remove baseurl prefix if present
    path = parsed.path
    if path.startswith(BASEURL):
        path = path[len(BASEURL):]

    # Remove leading slash
    if path.startswith("/"):
        path = path[1:]

    # Handle root path
    if not path or path == "":
        path = "index.html"

    # Try exact path
    target = site_dir / path
    if target.exists():
        return True, "ok"

    # Try with index.html
    if target.is_dir() or not path.endswith(".html"):
        index_target = site_dir / path / "index.html"
        if index_target.exists():
            return True, "ok"

    # Try with .html extension
    html_target = site_dir / f"{path}.html"
    if html_target.exists():
        return True, "ok"

    return False, "broken"


def check_external_link(url, timeout=5):
    """Check if an external URL is reachable."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status < 400, response.status
    except urllib.error.HTTPError as e:
        return e.code < 400, e.code
    except Exception as e:
        return False, str(e)


def generate_report(pattern_issues, link_issues, output_path):
    """Generate CSV report of all issues."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_file", "line", "issue_type", "severity", "link_found", "status", "description"])

        # Pattern issues from source files
        for file_path, issues in pattern_issues.items():
            for issue in issues:
                writer.writerow([
                    str(file_path),
                    issue["line"],
                    issue["issue_type"],
                    issue["severity"],
                    issue["match"],
                    "pattern_violation",
                    issue.get("description", ""),
                ])

        # Link validation issues from built site
        for source, issues in link_issues.items():
            for issue in issues:
                writer.writerow([
                    source,
                    "",
                    "broken_link" if issue["status"] == "broken" else "link_check",
                    "error" if issue["status"] == "broken" else "info",
                    issue["link"],
                    issue["status"],
                    "",
                ])

    return output_path


def print_summary(pattern_issues, link_issues):
    """Print a summary of findings."""
    total_pattern_issues = sum(len(issues) for issues in pattern_issues.values())
    total_broken_links = sum(
        1 for issues in link_issues.values()
        for issue in issues
        if issue["status"] == "broken"
    )

    # Count by severity
    severity_counts = defaultdict(int)
    for issues in pattern_issues.values():
        for issue in issues:
            severity_counts[issue["severity"]] += 1

    # Count by issue type
    type_counts = defaultdict(int)
    for issues in pattern_issues.values():
        for issue in issues:
            type_counts[issue["issue_type"]] += 1

    print("\n" + "=" * 60)
    print("LINK AUDIT SUMMARY")
    print("=" * 60)
    print(f"\nFiles scanned: {len(pattern_issues)}")
    print(f"Total pattern issues: {total_pattern_issues}")
    print(f"Broken internal links: {total_broken_links}")

    print("\nIssues by severity:")
    for severity in ["error", "warning", "info"]:
        if severity_counts[severity]:
            print(f"  {severity}: {severity_counts[severity]}")

    print("\nIssues by type:")
    for issue_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {issue_type}: {count}")

    print("\n" + "=" * 60)


def check_live_site_links(base_url, pages_to_check, timeout=10):
    """Check links on the live GitHub Pages site."""
    print(f"\nChecking live site at {base_url}...")

    results = {}
    checked_urls = set()

    for page in pages_to_check:
        url = f"{base_url}{page}"
        if url in checked_urls:
            continue
        checked_urls.add(url)

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = response.status
                results[page] = {"status": status, "ok": status < 400}
        except urllib.error.HTTPError as e:
            results[page] = {"status": e.code, "ok": False}
        except Exception as e:
            results[page] = {"status": str(e), "ok": False}

    return results


def main():
    parser = argparse.ArgumentParser(description="Audit links in Jekyll site")
    parser.add_argument("--build", action="store_true", help="Build site before auditing")
    parser.add_argument("--check-external", action="store_true", help="Check external URLs (slow)")
    parser.add_argument("--check-live", action="store_true", help="Check links on live GitHub Pages site")
    parser.add_argument("--output", default="output/link_audit_report.csv", help="Output CSV path")
    args = parser.parse_args()

    print("Starting link audit...")
    print(f"Project root: {PROJECT_ROOT}")

    # Step 1: Find and scan source files for pattern issues
    print("\nStep 1: Scanning source files for pattern issues...")
    source_files = find_source_files()
    print(f"Found {len(source_files)} source files to scan")

    pattern_issues = {}
    for file_path in source_files:
        rel_path = file_path.relative_to(PROJECT_ROOT)
        issues = scan_file_for_patterns(file_path)
        if issues:
            pattern_issues[rel_path] = issues

    print(f"Found pattern issues in {len(pattern_issues)} files")

    # Step 2: Build site if requested
    if args.build:
        print("\nStep 2: Building Jekyll site...")
        if not build_site():
            print("Skipping link validation due to build failure")
            link_issues = {}
        else:
            print("\nStep 3: Validating links in built site...")
            all_links, all_images = collect_site_links()

            link_issues = defaultdict(list)
            total_links = sum(len(links) for links in all_links.values())
            print(f"Found {total_links} links to validate")

            for source, links in all_links.items():
                for link in links:
                    valid, status = validate_internal_link(link, SITE_DIR)
                    if not valid or status == "broken":
                        link_issues[source].append({"link": link, "status": status})

                    # Check external links if requested
                    if args.check_external and status == "external":
                        ext_valid, ext_status = check_external_link(link)
                        if not ext_valid:
                            link_issues[source].append({"link": link, "status": f"external_{ext_status}"})
    else:
        print("\nSkipping site build (use --build to enable)")
        link_issues = defaultdict(list)

    # Step 4: Generate report
    print("\nGenerating report...")
    output_path = PROJECT_ROOT / args.output
    output_path.parent.mkdir(exist_ok=True)
    generate_report(pattern_issues, link_issues, output_path)
    print(f"Report saved to: {output_path}")

    # Step 5: Check live site if requested
    if args.check_live:
        print("\nStep 5: Checking live GitHub Pages site...")
        live_base = "https://zmuhls.github.io/cs-archive"

        # Main nav + first/second degree pages to check
        pages_to_check = [
            "/",
            "/about/",
            "/map/",
            "/search/",
            "/collections/",
            "/collections/nys-teachers-association/",
            "/collections/local-district-governance/",
            "/collections/administrative-data/",
            "/collections/district-consolidation/",
            "/collections/district-consolidation-by-county/",
            "/browse/",
            "/browse/by-decade/",
            "/browse/by-type/",
            "/browse/by-county/",
            "/browse/by-location/",
        ]

        # Add sample artifact pages
        artifact_samples = [
            "/artifacts/AG001/",
            "/artifacts/S0001/",
            "/artifacts/CG0001/",
            "/artifacts/S0045/",
        ]
        pages_to_check.extend(artifact_samples)

        live_results = check_live_site_links(live_base, pages_to_check)

        # Report live check results
        broken_live = [(p, r) for p, r in live_results.items() if not r["ok"]]
        print(f"Checked {len(live_results)} pages on live site")
        print(f"Broken pages: {len(broken_live)}")

        if broken_live:
            print("\nBroken pages on live site:")
            for page, result in broken_live:
                print(f"  {page}: {result['status']}")

        # Add to link_issues for report
        for page, result in live_results.items():
            if not result["ok"]:
                link_issues[f"LIVE:{page}"].append({
                    "link": f"{live_base}{page}",
                    "status": f"http_{result['status']}",
                })

    # Print summary
    print_summary(pattern_issues, link_issues)


if __name__ == "__main__":
    main()
