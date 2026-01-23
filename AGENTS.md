# Repository Guidelines

## Project Structure

```
cs-archive/
├── _artifacts/              # Jekyll collection (curated artifact pages)
├── _config.yml              # Jekyll site configuration
├── _data/                   # Jekyll data files (navigation, manifest)
├── _includes/               # Reusable template components
├── _layouts/                # Page layouts (artifact, browse, single)
├── assets/                  # Site assets (CSS, JS, maps)
├── browse/                  # Browse pages (decade, type, county, location)
├── collections/             # Collection overview pages
├── index.md, about.md, map.md, search.md
│
├── pipeline/                # Python processing code
│   ├── ocr.py               # QwenVLOCR engine class
│   ├── process_archive.py   # Batch orchestrator
│   ├── ocr_config.yaml      # Prompts and API settings
│   ├── requirements.txt     # Python dependencies
│   └── scripts/             # Utility scripts
│
├── csv/                     # Data inventories
├── raw/                     # Source scans (Git LFS)
├── derived/thumbs/          # Thumbnails (Git LFS, served by Jekyll)
├── output/                  # Processing output (OCR, reports, collections)
├── prompts/                 # LLM labeling requests/responses
├── logs/                    # Processing logs
├── tinker-cookbook/          # ML fine-tuning toolkit (separate project)
└── dev/                     # OMEKA theme development
```

## Build & Development Commands

### Jekyll Site
```bash
bundle install
bundle exec jekyll serve       # http://localhost:4000/cs-archive/
bundle exec jekyll build
```

### OCR Pipeline
```bash
cd pipeline  # or run from root with full paths

# Full pipeline (in order)
python pipeline/scripts/build_images_inventory.py
python pipeline/scripts/generate_thumbnails.py
python pipeline/scripts/prepare_image_label_requests.py
python pipeline/scripts/batch_label_images.py
python pipeline/scripts/merge_image_labels.py
python pipeline/scripts/dedupe_images_inventory.py
python pipeline/process_archive.py --collection images
python pipeline/scripts/consolidate_artifacts.py
python pipeline/scripts/generate_archive_manifest.py

# Process specific collections
python pipeline/process_archive.py --collection all
python pipeline/process_archive.py --collection kheel
python pipeline/process_archive.py --collection nys
```

### Install Python Dependencies
```bash
pip install -r pipeline/requirements.txt
```

## Coding Style

- Python 3.10+; PEP 8; 4-space indent; type hints where practical.
- snake_case for files/functions; PascalCase for classes; CONSTANTS in caps.
- Prefer `pathlib.Path`, `loguru` for logging, and small single-purpose functions.
- All pipeline scripts resolve paths via `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent`.
- Keep config in `pipeline/ocr_config.yaml`; credentials in `.env` (never committed).

## Testing

- No formal test suite. Verify changes with:
  - `python pipeline/process_archive.py --collection images` on a small subset
  - Check outputs in `output/ocr/`
  - `bundle exec jekyll build` for site changes

## Commit & PR Guidelines

- Imperative mood, concise, scoped prefix when helpful (e.g., `pipeline:`, `site:`, `ocr:`).
- Do not commit large binaries or secrets.
- PRs: include purpose, commands used, before/after notes.

## Agent-Specific Instructions

- Do not move or edit files under `raw/`; regenerate derived assets via scripts.
- Keep changes minimal and focused.
- Use `output/` for generated files and document how to regenerate.
- OCR transcriptions live in `output/ocr/markdown/` and are viewable on GitHub directly.
- For image URLs in markdown, use `media.githubusercontent.com` (not `raw.githubusercontent.com`) for Git LFS files.

## After Any Changes

1. **DEVLOG.md** - Append a dated entry (what changed, key decisions, next steps).
2. **CLAUDE.md** - Update the Kanban section (move items between Backlog/In Progress/Done).
