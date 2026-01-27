# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Digital humanities archive for the Common School system of New York State (1800s-1900s). Contains handwritten documents, typed records, statistical charts, and administrative correspondence. Uses multimodal AI (Qwen VL Plus via OpenRouter) to transcribe, classify, and extract metadata.

## Development Commands

### Jekyll Site (Local Development)

```bash
# Install Ruby dependencies (requires Ruby 3.3.4 via RVM)
bundle install

# Start local development server at http://localhost:4000/cs-archive/
bundle exec jekyll serve

# Build only (no server)
bundle exec jekyll build
```

Site deploys via GitHub Actions (`.github/workflows/jekyll-gh-pages.yml`) to GitHub Pages on push to main.

### Full OCR Pipeline (in order)

```bash
# 1. Ingest images and build inventory
python pipeline/scripts/build_images_inventory.py

# 2. Generate thumbnails for LLM labeling
python pipeline/scripts/generate_thumbnails.py

# 3. Prepare LLM labeling requests
python pipeline/scripts/prepare_image_label_requests.py

# 4. Run automated LLM labeling (uses OPENROUTER_KEY)
python pipeline/scripts/batch_label_images.py

# 5. Merge labels into inventory
python pipeline/scripts/merge_image_labels.py

# 6. Deduplicate inventory entries
python pipeline/scripts/dedupe_images_inventory.py

# 7. Run OCR (resumes from where it left off)
python pipeline/process_archive.py --collection images

# 8. Consolidate artifacts and generate manifest
python pipeline/scripts/consolidate_artifacts.py
python pipeline/scripts/generate_archive_manifest.py
```

### OCR Processing

```bash
python pipeline/process_archive.py --collection all      # All collections
python pipeline/process_archive.py --collection images   # Loose images only
python pipeline/process_archive.py --collection kheel    # Kheel Center PDFs
python pipeline/process_archive.py --collection nys      # NYS Archives PDFs
```

## Architecture Overview

### Processing Pipeline

```text
raw/scans/Kheel Center/img/
  → pipeline/scripts/build_images_inventory.py      → csv/images_inventory.csv
  → pipeline/scripts/generate_thumbnails.py         → derived/thumbs/
  → pipeline/scripts/prepare_image_label_requests.py → prompts/images_label_requests.jsonl
  → pipeline/scripts/batch_label_images.py          → prompts/images_label_responses.jsonl
  → pipeline/scripts/merge_image_labels.py          → csv/images_inventory_labeled.csv
  → pipeline/process_archive.py                     → output/ocr/text/, output/ocr/metadata/
  → pipeline/scripts/consolidate_artifacts.py       → output/archive/documents/, output/archive/research/
  → pipeline/scripts/generate_archive_manifest.py   → output/archive/manifest.json
```

### Core Components

1. **`pipeline/ocr.py`** - QwenVLOCR class
   - Async API calls with retry logic
   - PDF-to-image at 300 DPI
   - Document-type-specific prompts
   - Confidence scoring via [?] and [illegible] markers

2. **`pipeline/process_archive.py`** - Batch orchestrator
   - Reads from `csv/images_inventory_labeled.csv`
   - Maps `item_type` to OCR prompts (letter→handwritten, form→table_form, etc.)
   - Resume capability: skips already-processed images

3. **`pipeline/scripts/consolidate_artifacts.py`** - Post-OCR processing
   - Groups outputs by `artifact_group_id`
   - Merges sequential pages, culls duplicates (>85% text similarity)
   - Routes research notes to `output/archive/research/`

### Jekyll Site Structure

```text
_config.yml          # Site config (theme: minimal-mistakes-jekyll, remote_theme for GH Pages)
_data/navigation.yml # Sidebar and header nav
_layouts/            # Custom layouts (artifact.html, browse.html)
_includes/           # Reusable components (artifact-card.html)
assets/maps/         # Leaflet map JS
collections/         # Collection overview pages
browse/              # Browse by decade/type/county/location
index.md, about.md, map.md, search.md  # Top-level pages
derived/thumbs/      # Thumbnails served via `include:` in _config.yml
```

### Image Storage & Git LFS

**CRITICAL: All images are stored with Git LFS.** This affects how images can be accessed.

#### Directory Structure

| Directory | Contents | Git LFS |
| --- | --- | --- |
| `raw/scans/Kheel Center/img/` | Original high-res scans (JPEG) | Yes |
| `derived/thumbs/` | 512px thumbnails for web display | Yes |

#### Git LFS Configuration (`.gitattributes`)

```text
raw/**/*.jpeg filter=lfs diff=lfs merge=lfs -text
derived/**/*.jpeg filter=lfs diff=lfs merge=lfs -text
```

#### Correct Image URL Patterns

**For Jekyll templates** (`_layouts/`, `_includes/`, `*.md` with Liquid):

```liquid
{{ '/derived/thumbs/IMG_0625.jpeg' | relative_url }}
```

This generates `/cs-archive/derived/thumbs/IMG_0625.jpeg` which Jekyll serves correctly.

**For artifact frontmatter** (`_artifacts/*.md`):

```yaml
source_images:
  - filename: "IMG_0625.jpeg"  # Preferred - used by templates
    thumbnail: "https://..."    # Fallback only
    full: "https://..."         # For lightbox/full-size view
```

The `_includes/artifact-card.html` template checks for `filename` first:

```liquid
{% if first_img.filename %}
  {% assign thumb_src = '/derived/thumbs/' | append: first_img.filename | relative_url %}
{% else %}
  {% assign thumb_src = first_img.thumbnail %}
{% endif %}
```

#### URLs That DO NOT Work for Git LFS Files

**NEVER use `raw.githubusercontent.com` for LFS files:**

```text
# BROKEN - Returns LFS pointer text, not image binary
https://raw.githubusercontent.com/zmuhls/cs-archive/main/derived/thumbs/IMG_0625.jpeg
```

This returns:

```text
version https://git-lfs.github.com/spec/v1
oid sha256:211b289311d44c2c9398b679f07ead7b85d1a4efb8be0dd2c8371e5d21f10e9f
size 72037
```

#### URLs That Work for Git LFS Files

1. **GitHub Pages (preferred for Jekyll site):**

   ```text
   https://zmuhls.github.io/cs-archive/derived/thumbs/IMG_0625.jpeg
   ```

   Requires `derived/thumbs` to be included in Jekyll build (see `_config.yml`).

2. **GitHub Media URL (for external references):**

   ```text
   https://media.githubusercontent.com/media/zmuhls/cs-archive/main/derived/thumbs/IMG_0625.jpeg
   ```

   This endpoint serves actual LFS file content.

3. **GitHub blob with ?raw=true (redirects to media URL):**

   ```text
   https://github.com/zmuhls/cs-archive/blob/main/derived/thumbs/IMG_0625.jpeg?raw=true
   ```

#### Jekyll Config for Images

In `_config.yml`:

```yaml
exclude:
  - derived/        # Exclude parent directory
include:
  - derived/thumbs  # But include thumbs subdirectory
```

**Note:** The `include` directive overrides `exclude` for specified paths. GitHub Actions workflow has `lfs: true` to checkout actual files during build.

#### When Generating Collection Pages

Scripts that generate collection markdown (e.g., `pipeline/scripts/generate_nys_teachers_collection.py`) should use:

1. **For Jekyll-rendered pages:** Use `relative_url` filter with local paths
2. **For static markdown:** Use GitHub Media URLs, NOT raw.githubusercontent.com

Example fix for collection generation scripts:
```python
# WRONG - LFS pointer returned
thumbnail_url = f"https://raw.githubusercontent.com/zmuhls/cs-archive/main/derived/thumbs/{filename}"

# CORRECT - Actual image served
thumbnail_url = f"https://media.githubusercontent.com/media/zmuhls/cs-archive/main/derived/thumbs/{filename}"
```

### Key Data Files

| File | Purpose |
| --- | --- |
| `csv/images_inventory.csv` | Raw inventory from ingestion |
| `csv/images_inventory_labeled.csv` | Inventory with LLM classifications |
| `prompts/images_label_requests.jsonl` | LLM labeling requests |
| `prompts/images_label_responses.jsonl` | LLM labeling responses |
| `output/archive/manifest.json` | Final artifact catalog |
| `_data/manifest.json` | Jekyll-accessible artifact catalog |
| `DEVLOG.md` | Chronological development history |
| `AGENTS.md` | Instructions for AI agents |

### Item Type Vocabulary

12 controlled types: `document_page`, `notecard`, `ledger_or_register`, `form`, `letter`, `pamphlet_or_brochure`, `report`, `meeting_minutes`, `map_or_diagram`, `photograph_of_display`, `envelope_or_folder`, `cover_or_title_page`, `blank_or_unreadable`

## API Configuration

- **Model**: `qwen/qwen-vl-plus` via OpenRouter
- **Auth**: `OPENROUTER_KEY` in `.env`
- **Settings**: 4000 max tokens, 0.1 temperature, 3 retries with exponential backoff
- **Batch size**: 5 concurrent requests

## Historical Document Handling

OCR prompts preserve 19th century characteristics:

- Period spelling and abbreviations ("inst." for instant, "&c" for etc.)
- Archaic terms (selectmen, freeholders, trustees)
- Uncertainty markers: [?] for unclear, [illegible] for unreadable
- Annotations: [stamp: ...], [handwritten: ...], [different hand: ...]

---

## OMEKA Classic Integration

### Overview

Collections are published to OMEKA Classic using the "Thanks, Roy" theme. Three curated collections are available:

1. **NYS Teachers' Association (1845-1940s)** - Proceedings, membership materials, advocacy documents
2. **District Consolidation Records** - County-by-county tables from NYS Archives Series B0494
3. **NYS Archives Local District Records** - Meeting minutes, notecards, and administrative records from Series A4645, B0594, A4456

### Docker Deployment

OMEKA runs in Docker with MySQL backend:

```bash
# Start OMEKA and MySQL
cd /tmp && docker-compose -f docker-compose.yml up -d

# Access OMEKA at http://localhost:8001
# Admin login: admin / omeka123456

# Stop services
docker-compose down
```

Configuration files: `/tmp/docker-compose.yml`, `/tmp/Dockerfile`

### OMEKA CSV Generation

Transform collections into OMEKA-compatible CSV:

```bash
python pipeline/scripts/generate_omeka_csv.py
# Output: output/omeka/items_import.csv (355 items across 3 collections)

# Generate individual collection markdown files:
python pipeline/scripts/generate_nys_teachers_collection.py
python pipeline/scripts/generate_county_collection.py
python pipeline/scripts/generate_nys_local_records_collection.py

# Process Amityville PDF separately (665 pages):
python pipeline/scripts/process_amityville.py
```

**CSV Schema:**

- Maps consolidated artifacts to Dublin Core metadata
- Distinguishes table items (Dataset type), PDF pages (Text type), and image items (Text type)
- Generates GitHub CDN URLs for images, table thumbnails, and OCR text files
- Columns: collection, title, date, description, type, spatial, subject, source, identifier, file

**Key Functions:**

- `parse_district_consolidation()` - Extracts table metadata from markdown
- `parse_nys_teachers()` - Extracts teacher association items
- `parse_nys_local_records()` - Extracts NYS Archives PDF page items
- `find_artifact_for_image()` - Maps filenames to artifact metadata
- `get_github_raw_url()` - Generates GitHub CDN URLs with path differentiation

### Theme Customization

The "Thanks, Roy" theme in `dev/omeka/` has been modified:

**[dev/omeka/index.php](dev/omeka/index.php):**

- Added featured collections grid to homepage
- Grid displays both collection cards with descriptions and explore links

**[dev/omeka/css/style.css](dev/omeka/css/style.css):**

- Added responsive CSS Grid layout (`repeat(auto-fit, minmax(300px, 1fr))`)
- Styled `.collection-card` with hover effects
- Mobile-first design with flexbox for card content

### Import Workflow

1. Create collections in OMEKA admin (assigns IDs 1 and 2)
2. Upload CSV via CSV Import plugin
3. Plugin maps CSV columns to Dublin Core elements
4. 249 items imported from consolidated artifacts + tables

**Documentation:**

- `output/omeka/OMEKA_SETUP_GUIDE.md` - Step-by-step configuration
- `output/omeka/THEME_MODIFICATIONS.md` - Technical details
- `output/omeka/README.md` - Overview of integration package

---

## Location Mapping

Geographic data extracted to `output/locations/` for spatial visualization:

| File | Description |
| --- | --- |
| `LOCATION_MAP.md` | Master documentation with coordinates and next steps |
| `nysta-meetings.geojson` | 16 NYSTA meeting sites (1881-1927) |

Leaflet map at `dev/leaflet/archive-map.html` displays both NYSTA meetings (red markers) and consolidation counties (blue markers) with layer toggles and clickable sidebar.

---

## Current Work: OMEKA Publishing & Human Review

### In Progress
<!-- Move items here when actively working on them -->

### Backlog

#### Stage 4: Human-in-the-Loop Review

- Create `pipeline/scripts/generate_review_queues.py` (hallucination detection, low-confidence flagging)
- Create `csv/ocr_review_queue.csv` template
- Create `pipeline/scripts/apply_corrections.py` for correction ingestion
- Document review workflow in CLAUDE.md

#### Stage 5: Multi-Model Ensemble

- Abstract OCR class for multiple backends in `pipeline/ocr.py`
- Add `qwen/qwen-vl-max` as secondary model via OpenRouter
- Add Mistral OCR as tertiary model via OpenRouter
- Create `pipeline/scripts/ensemble_ocr.py` for comparative runs
- Add consensus scoring to metadata schema
- Test ensemble on 10 challenging documents

#### Site Maintenance

- Evaluate and deprecate/merge the legacy `docs/` Jekyll copy in favor of root build (Actions-driven). [Partially done: marked legacy, added README/notice]
- Commit `_artifacts/` directory to git (currently untracked, causing 404s on live site).
- Fix collection page image URLs to use `media.githubusercontent.com` instead of `raw.githubusercontent.com`.

---

### Done

#### 2026-01-27 — District Consolidation Comprehensive Fix

- Updated image URLs in `output/comprehensive/District-Consolidation-Data_100-116_comprehensive.md` from `raw.githubusercontent.com` to repository-relative paths (`../ocr/tables/images/...`) so images render correctly on GitHub.
- Note: Broader backlog item remains to standardize all collection markdown to avoid `raw` URLs and use `media.githubusercontent.com` for any LFS-backed assets.

#### 2026-01-22 — Directory Reorganization

- Moved all Python code into `pipeline/` (ocr.py, process_archive.py, ocr_config.yaml, requirements.txt, scripts/)
- Updated PROJECT_ROOT path resolution in all 32+ scripts
- Moved comprehensive markdown exports to `output/comprehensive/`
- Updated `_config.yml` exclude list to reference `pipeline/`
- Rewrote AGENTS.md with current structure
- Updated all CLAUDE.md path references

#### 2026-01-18 — Link Audit & Image Documentation

- Created `pipeline/scripts/link_audit.py` for automated link pattern detection and live site validation
- Documented Git LFS image handling in CLAUDE.md (critical for future sessions)
- Identified critical issues: `_artifacts/` untracked, LFS images not rendering via `raw.githubusercontent.com`
- Generated `output/link_audit_report.csv` (1,062 issues) and `output/LINK_AUDIT_SUMMARY.md`

#### 2026-01-19 — Jekyll Site & GitHub Pages

- Add Jekyll site with Minimal Mistakes theme to project root
- Configure GitHub Actions deployment (`.github/workflows/jekyll-gh-pages.yml`)
- Publish `derived/thumbs` via `_config.yml` include; use local thumbs in cards/galleries
- Convert internal links to `relative_url` in index/browse/collections pages
- Add homepage collection images; standardize "NYS Teachers' Association" naming
- Integrate map page with theme layout (remove standalone W3.CSS styling)

#### 2026-01-19 — Map Page Fixes (Leaflet)

- Fix partial/half rendering and off-centered map by invalidating size on load/resize/tab changes
- Increase map height to viewport-relative with min/max bounds (70vh, 420–800px)
- Prevent markdown-style text from visually bleeding into the map area; convert note to HTML and style as a subtle `.location-note`

#### 2026-01-19 — Mark legacy `docs/` copy

- Added `docs/README.md` with deprecation notice and canonical site link
- Updated `docs/index.md` title and banner to point to https://zmuhls.github.io/cs-archive/

#### 2026-01-18 — README Overhaul

- Added collection overviews, cross-links to browse/search/map, outputs, inventories, prompts, and developer docs

#### 2025-01-17 — NYS Archives Local Records Collection

- Created third collection from Series A4645, B0594, A4456
- Created `pipeline/scripts/generate_nys_local_records_collection.py` and `pipeline/scripts/process_amityville.py`
- Updated `pipeline/scripts/generate_omeka_csv.py` to include new collection (355 total items)

#### 2025-01-16 — OMEKA Integration

- Created `pipeline/scripts/generate_omeka_csv.py` for CSV import preparation (249 items)
- Generated Dublin Core metadata mapping; modified "Thanks, Roy" theme

#### 2024-12-24 — Artifact Collation

- Added artifact_link_type, artifact_confidence, needs_review columns to inventory
- Created `pipeline/scripts/refine_artifact_groups.py` for text-similarity-based grouping
