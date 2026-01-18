# Common School Archive of New York State

Preserving and making accessible New York State’s 19th–early 20th century common school records: minutes, ledgers, letters, tables, and publications.

> “We the trustees of the district in said town in conformity with the act for the support of common schools do certify and report that the whole time any school has been kept in our district is eleven months of their fourths and the amount of money received in our district from the commissioners of Common Schools.”

**Project Status:** Active Development  
**Last Updated:** January 2026

---

## About the Archive

- Purpose: document governance, administration, and professionalization in NYS public education through primary sources.
- Scope: handwritten pages, typed records, notecards, meeting minutes, tables, reports, and ephemera (1840s–1940s).
- Archival sources: NYS Archives series (e.g., A4645, B0594, B0494) and other repositories (e.g., Cornell’s Kheel Center), plus locally photographed artifacts in `raw/`.
- Processing: multimodal AI (Qwen VL Plus) for transcription, classification, and metadata; outputs are versioned in‑repo for auditability.

---

## Collections

- NYS Teachers Association
  - Curated overview: `collections/nys-teachers-association.md`
  - Generated collection (items & links): `output/collections/nys-teachers-association.md`
  - Related: meeting locations map `map.md`

- Local District Governance Records
  - Overview and stats: `collections/nys-local-records.md`
  - Browse by document type/period: `browse/index.md`

- District Administrative Data & Statistics
  - Overview: `collections/district-consolidation.md`
  - Browse by county (curated): `collections/district-consolidation-by-county.md`
  - Browse by county (generated): `output/collections/district-consolidation-by-county.md`
  - Tables index and bulk data: `output/ocr/tables/`

Complementary navigation pages: `about.md`, `browse/index.md`, `search.md`, `map.md`.

---

## One‑Stop Link Hub

Use this section as a quick index to the most useful pages, data, and scripts in this repository.

### Curated Collections

- Collections overview: `collections/index.md`
- NYS Teachers Association: `collections/nys-teachers-association.md`
- Local District Governance Records: `collections/nys-local-records.md`
- District Administrative Data (overview): `collections/district-consolidation.md`
- District Consolidation by County (curated): `collections/district-consolidation-by-county.md`
- NYSTA (generated, with items): `output/collections/nys-teachers-association.md`
- Consolidation by County (generated): `output/collections/district-consolidation-by-county.md`

### Browse, Search, Map

- Browse hub: `browse/index.md`
- By decade: `browse/by-decade.md`
- By document type: `browse/by-type.md`
- By county: `browse/by-county.md`
- By location: `browse/by-location.md`
- Full‑text search: `search.md`
- Meeting locations & county overlays: `map.md`

### Data Outputs

- OCR text: `output/ocr/text/`
- OCR metadata (JSON): `output/ocr/metadata/`
- Table extractions (human‑readable): `output/ocr/tables/markdown/`
- Table extractions (CSV): `output/ocr/tables/csv/`
- Table extractions (JSON): `output/ocr/tables/json/`
- Consolidated artifacts: `output/archive/documents/`
- Archive manifest (catalog): `output/archive/manifest.json`

### Inventories, Prompts, and Labels

- Image inventory: `csv/images_inventory.csv`
- Labeled inventory: `csv/images_inventory_labeled.csv`
- Labeling prompts/responses: `prompts/`

### Developer & Project Docs

- Project map (site): `index.md`
- About the archive: `about.md`
- Agent guidelines: `AGENTS.md`
- Dev Kanban and reference: `CLAUDE.md`
- Development log: `DEVLOG.md`
- Open tasks and notes: `TODO.md`

---

## Build & Reproduce

Environment setup:

```bash
pip install -r requirements.txt
```

Key commands:

```bash
# Inventory photos
python scripts/build_images_inventory.py

# Generate thumbnails
python scripts/generate_thumbnails.py

# Run OCR
python process_archive.py --collection all
python process_archive.py --collection images
```

Outputs appear in `output/ocr/` and `output/archive/`; spot‑check counts and success rate in console logs.
