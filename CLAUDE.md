# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Digital humanities archive for the Common School system of New York State (1800s-1900s). Contains handwritten documents, typed records, statistical charts, and administrative correspondence. Uses multimodal AI (Qwen VL Plus via OpenRouter) to transcribe, classify, and extract metadata.

## Development Commands

### Full Pipeline (in order)

```bash
# 1. Ingest images and build inventory
python scripts/build_images_inventory.py

# 2. Generate thumbnails for LLM labeling
python scripts/generate_thumbnails.py

# 3. Prepare LLM labeling requests
python scripts/prepare_image_label_requests.py

# 4. Run automated LLM labeling (uses OPENROUTER_KEY)
python scripts/batch_label_images.py

# 5. Merge labels into inventory
python scripts/merge_image_labels.py

# 6. Deduplicate inventory entries
python scripts/dedupe_images_inventory.py

# 7. Run OCR (resumes from where it left off)
python process_archive.py --collection images

# 8. Consolidate artifacts and generate manifest
python scripts/consolidate_artifacts.py
python scripts/generate_archive_manifest.py
```

### OCR Processing

```bash
python process_archive.py --collection all      # All collections
python process_archive.py --collection images   # Loose images only
python process_archive.py --collection kheel    # Kheel Center PDFs
python process_archive.py --collection nys      # NYS Archives PDFs
```

## Architecture Overview

### Processing Pipeline

```text
raw/scans/img/     →  build_images_inventory.py  →  csv/images_inventory.csv
                   →  generate_thumbnails.py     →  derived/thumbs/
                   →  prepare_image_label_requests.py → prompts/images_label_requests.jsonl
                   →  batch_label_images.py      →  prompts/images_label_responses.jsonl
                   →  merge_image_labels.py      →  csv/images_inventory_labeled.csv
                   →  process_archive.py         →  output/ocr/text/, output/ocr/metadata/
                   →  consolidate_artifacts.py   →  output/archive/documents/, output/archive/research/
                   →  generate_archive_manifest.py → output/archive/manifest.json
```

### Core Components

1. **`ocr.py`** - QwenVLOCR class
   - Async API calls with retry logic
   - PDF-to-image at 300 DPI
   - Document-type-specific prompts
   - Confidence scoring via [?] and [illegible] markers

2. **`process_archive.py`** - Batch orchestrator
   - Reads from `csv/images_inventory_labeled.csv`
   - Maps `item_type` to OCR prompts (letter→handwritten, form→table_form, etc.)
   - Resume capability: skips already-processed images

3. **`scripts/consolidate_artifacts.py`** - Post-OCR processing
   - Groups outputs by `artifact_group_id`
   - Merges sequential pages, culls duplicates (>85% text similarity)
   - Routes research notes to `output/archive/research/`

### Key Data Files

| File | Purpose |
| --- | --- |
| `csv/images_inventory.csv` | Raw inventory from ingestion |
| `csv/images_inventory_labeled.csv` | Inventory with LLM classifications |
| `prompts/images_label_requests.jsonl` | LLM labeling requests |
| `prompts/images_label_responses.jsonl` | LLM labeling responses |
| `output/archive/manifest.json` | Final artifact catalog |
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
python scripts/generate_omeka_csv.py
# Output: output/omeka/items_import.csv (355 items across 3 collections)

# Generate individual collection markdown files:
python scripts/generate_nys_teachers_collection.py
python scripts/generate_county_collection.py
python scripts/generate_nys_local_records_collection.py

# Process Amityville PDF separately (665 pages):
python scripts/process_amityville.py
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

- Create `scripts/generate_review_queues.py` (hallucination detection, low-confidence flagging)
- Create `csv/ocr_review_queue.csv` template
- Create `scripts/apply_corrections.py` for correction ingestion
- Document review workflow in CLAUDE.md

#### Stage 5: Multi-Model Ensemble

- Abstract OCR class for multiple backends in `ocr.py`
- Add `qwen/qwen-vl-max` as secondary model via OpenRouter
- Add Mistral OCR as tertiary model via OpenRouter
- Create `scripts/ensemble_ocr.py` for comparative runs
- Add consensus scoring to metadata schema
- Test ensemble on 10 challenging documents

### Done

#### Stage 1: Artifact Collation (2024-12-24)

- Added new columns to inventory CSV schema (artifact_link_type, artifact_confidence, needs_review, parent_artifact_id)
- Created `scripts/refine_artifact_groups.py` for text-similarity-based grouping
- Created `scripts/migrate_inventory_schema.py` for existing data migration
- Updated `consolidate_artifacts.py` to handle different link types
- Tested on sample session S0026 (19 items)
- Generated `csv/artifact_review_queue.csv` with 14 items for review

#### Stage 3: OMEKA Integration (2025-01-16)

- Created `scripts/generate_omeka_csv.py` for CSV import preparation (249 items)
- Generated Dublin Core metadata mapping (collection, title, date, description, type, spatial, subject, source, identifier, file)
- Created collection introductions and about page content
- Modified "Thanks, Roy" theme with featured collections grid and responsive CSS
- Provided Docker setup (MySQL + PHP + Apache) and OMEKA installation guide
- Package ready for manual OMEKA configuration and CSV import

#### Stage 3b: NYS Archives Local Records Collection (2025-01-17)

- Created third collection: "NYS Archives Local District Records" from Series A4645, B0594, A4456
- Created `scripts/generate_nys_local_records_collection.py` for collection markdown generation
- Created `scripts/process_amityville.py` for separate processing of 665-page Amityville PDF
- Updated `scripts/generate_omeka_csv.py` to include new collection (355 total items)
- Generated `output/collections/nys-local-records.md` with 106 pages from South-Kortright Roll and District Notecards
- Amityville-Records.pdf pending OCR processing (run `python scripts/process_amityville.py`)
