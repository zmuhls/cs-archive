# OCR Repetition Audit

**Date**: 2026-01-19
**Script**: `scripts/cleanup_illegible_markers.py`
**Total Cleaned**: 49 files (~225 KB reduced)

---

## Prominent Repetition Locations

### Artifact Files (Model Hallucination Loops)

| File | Issue | Reduction |
|------|-------|-----------|
| `_artifacts/S0026-018.md` | 67 repeated header+[illegible] blocks ("ART EDUCATION IN NEW YORK STATE") | 3.7 KB |
| `_artifacts/S0043_0014.md` | 43 repeated lines (partial sentence loop) | 4.9 KB |
| `_artifacts/AG004.md` | 25 repeated lines | 1.7 KB |
| `_artifacts/AG006.md` | 11 repeated lines | 1.1 KB |
| `_artifacts/S0030_001.md` | 5 consecutive [illegible] markers | 0.1 KB |
| `_artifacts/S0067-002.md` | 2 repeated lines | 0.1 KB |

### District Notecard Records (Series B0594)

Pages that were nearly 100% illegible (300 consecutive markers → consolidated to 1):

| File | Original Markers | Reduction % |
|------|-----------------|-------------|
| `District-Notecard-Records_page_32` | 300 | 98.8% |
| `District-Notecard-Records_page_46` | 300 | 98.8% |
| `District-Notecard-Records_page_51` | 300 | 98.8% |
| `District-Notecard-Records_page_56` | 300 | 98.8% |
| `District-Notecard-Records_page_59` | 300 | 98.8% |
| `District-Notecard-Records_page_9` | 300 | 98.8% |
| `District-Notecard-Records_page_5` | 276 | 89.0% |
| `District-Notecard-Records_page_50` | 275 | 90.8% |
| `District-Notecard-Records_page_54` | 297 | 97.3% |

**Complete file**: `District-Notecard-Records_complete.txt` — 2,637 markers removed (45.4% reduction)

### South-Kortright Roll-13 (Series A4645)

Pages that were nearly 100% illegible:

| File | Original Markers | Reduction % |
|------|-----------------|-------------|
| `South-Kortright-Roll-13_page_4` | 300 | 98.8% |
| `South-Kortright-Roll-13_page_5` | 300 | 98.8% |
| `South-Kortright-Roll-13_page_10` | 299 | 98.7% |
| `South-Kortright-Roll-13_page_11` | 300 | 98.8% |
| `South-Kortright-Roll-13_page_30` | 300 | 98.8% |

**Complete file**: `South-Kortright-Roll-13_complete.txt` — 1,494 markers removed (33.2% reduction)

### Amityville Records (Series A4456)

Pages with significant illegible content:

| File | Original Markers | Reduction % |
|------|-----------------|-------------|
| `Amityville-Records_page_584` | 298 | 98.2% |
| `Amityville-Records_page_586` | 298 | 98.0% |
| `Amityville-Records_page_380` | 243 | 94.9% |
| `Amityville-Records_page_484` | 215 | 82.4% |
| `Amityville-Records_page_478` | 192 | 75.1% |
| `Amityville-Records_page_501` | 201 | 73.9% |
| `Amityville-Records_page_15` | 197 | 70.2% |
| `Amityville-Records_page_242` | 232 | 64.0% |

**Complete file**: `Amityville-Records_complete.txt` — 1,864 markers removed (2.0% reduction)

### Individual Image Files (Kheel Center)

| File | Original Markers | Reduction % | Notes |
|------|-----------------|-------------|-------|
| `IMG_3465.txt` | 300 | 98.8% | Completely illegible |
| `IMG_3868.txt` | 292 | 96.9% | Nearly all illegible |
| `IMG_3327.txt` | 293 | 95.2% | Nearly all illegible |
| `IMG_3461.txt` | 290 | 93.4% | Nearly all illegible |
| `IMG_3849.txt` | 283 | 90.1% | Nearly all illegible |
| `IMG_3860.txt` | 267 | 83.5% | Mostly illegible |
| `IMG_3853.txt` | 249 | 75.3% | Mostly illegible |
| `IMG_8541.txt` | 216 | 61.4% | Partially illegible |
| `IMG_3475.txt` | 165 | 37.1% | Some content preserved |

---

## Recommendations

1. **Re-OCR candidates**: Pages with 90%+ illegible content may benefit from re-processing with different model settings or image enhancement
2. **Review notecards**: District Notecard pages 32, 46, 51, 56, 59, 9 appear to be blank or severely degraded
3. **Image quality check**: Individual images with 90%+ illegible markers should be reviewed for scan quality issues
4. **Artifact review**: S0026-018.md and S0043_0014.md should be manually reviewed - the model hallucinated content loops

---

## Archived

# Archive Reorganization TODO

## Overview

This document outlines the reorganization of the Common School Archive collections to align thematic content across all curation platforms (OMEKA Classic, Jekyll/GitHub Pages, consolidated artifacts, and OMEKA CSV exports).

**Status**: 🟡 Planning Phase
**Priority**: High
**Estimated Items**: ~1,020 total across 3 collections

---

## Target Collection Structure

### Collection 1: NYS Teachers Association (UNCHANGED)
- **Status**: ✅ Complete
- **Items**: ~249 items
- **Theme**: Teacher advocacy, proceedings, membership materials
- **Time Period**: 1845-1940s
- **Files**:
  - `output/collections/nys-teachers-association.md`
  - OMEKA CSV: rows with `collection=NYS Teachers Association (1845-1940s)`

### Collection 2: Local District Governance Records (NEW)
- **Status**: 🔴 Not Started
- **Items**: ~708 items (665 Amityville + 43 South-Kortright)
- **Theme**: Meeting minutes, board decisions, governance evolution
- **Sub-collections**:
  - **Amityville Board of Education Minutes** (665 pages, 1930s, Series A4456)
    - Suburban/consolidated district governance
    - Depression-era school administration
    - Formalized board procedures and committees
  - **South-Kortright District Minutes** (43 pages, 1810s-1820s, Series A4645)
    - Rural one-room school governance
    - Early common school administration
    - Informal governance structures

**Research Value**:
- Compare rural vs. suburban governance across 100+ year timespan
- Track bureaucratic modernization
- Study Depression-era school finance and labor relations
- Analyze women's civic participation (Mrs. Florence Hartman, Grace Burns)

### Collection 3: District Administrative Data & Statistics (NEW)
- **Status**: 🔴 Not Started
- **Items**: ~163 items (63 notecards + 100+ consolidation tables)
- **Theme**: Reference data, registries, statistical reports
- **Sub-collections**:
  - **District Notecard Index** (63 pages, Series B0594)
    - Registration and name change records
    - Administrative actions documentation
    - Index cards from NYS Education Department
  - **County Consolidation Tables** (100+ pages, Series B0494)
    - Statistical data on district mergers by county
    - Central Rural Schools, Union Free Schools, Town School Units
    - Quantitative consolidation analysis

**Research Value**:
- Geographic/spatial analysis of consolidation patterns
- Quantitative research on district mergers
- Administrative record-keeping evolution
- Cross-reference with governance decisions

---

## Implementation Tasks

### Phase 1: Collection Markdown Files

- [ ] **Create `scripts/generate_governance_collection.py`**
  - Merge Amityville + South-Kortright
  - Output: `output/collections/local-district-governance.md`
  - Group by time period (1810s-1820s vs. 1930s)
  - Include metadata: series, page count, date ranges
  - Add research themes section
  - Generate stats report

- [ ] **Create `scripts/generate_administrative_data_collection.py`**
  - Merge District Notecards + County Consolidation Tables
  - Output: `output/collections/district-administrative-data.md`
  - Group by data type (index cards vs. statistical tables)
  - Include geographic organization for consolidation tables
  - Add data dictionary/schema documentation
  - Generate stats report

- [ ] **Update existing collection generators**
  - Verify `scripts/generate_nys_teachers_collection.py` unchanged
  - Archive/deprecate `scripts/generate_nys_local_records_collection.py`
  - Archive/deprecate `scripts/generate_county_collection.py`

### Phase 2: OMEKA CSV Regeneration

- [ ] **Update `scripts/generate_omeka_csv.py`**
  - Modify `parse_nys_local_records()` function to split into two collections:
    - Parse Amityville + South-Kortright → Collection 2
    - Parse District Notecards → Collection 3
  - Modify `parse_district_consolidation()` to be part of Collection 3
  - Update collection names in CSV output:
    - Collection 1: `NYS Teachers Association (1845-1940s)` (unchanged)
    - Collection 2: `Local District Governance Records (1810s-1930s)` (NEW)
    - Collection 3: `District Administrative Data & Statistics` (NEW)
  - Add sub-collection identifiers in `subject` field:
    - "Amityville Board Minutes" / "South-Kortright Minutes"
    - "District Notecards" / "County Consolidation Tables"
  - Generate new `output/omeka/items_import.csv` (~1,020 items)

- [ ] **Create OMEKA import guide**
  - Document 3-collection structure
  - Update `output/omeka/OMEKA_SETUP_GUIDE.md`
  - Add collection descriptions for OMEKA admin interface
  - Update CSV Import plugin mapping instructions

### Phase 3: OMEKA Theme Customization

- [ ] **Update `dev/omeka/index.php`**
  - Add Collection 2 card: "Local District Governance Records"
    - Description: "Board meeting minutes from rural and suburban districts (1810s-1930s)"
    - Highlight: "Compare early one-room school governance with Depression-era administration"
  - Add Collection 3 card: "District Administrative Data & Statistics"
    - Description: "Index cards, registries, and consolidation statistics"
    - Highlight: "Quantitative data for spatial and temporal analysis"
  - Update Collection 1 card (if needed)

- [ ] **Update `dev/omeka/css/style.css`**
  - Ensure 3-column grid layout works with new collections
  - Test responsive design with 3 collection cards

- [ ] **Test Docker deployment**
  - `cd /tmp && docker-compose up -d`
  - Verify 3 collections display correctly
  - Test collection browse pages
  - Verify item detail pages

### Phase 4: Jekyll/GitHub Pages (Future)

- [ ] **Create Jekyll collection configuration**
  - `_config.yml`: Define 3 collections
  - Create `_collections/governance/*.md` (708 items)
  - Create `_collections/administrative-data/*.md` (163 items)
  - Keep `_collections/teachers-association/*.md` (249 items)

- [ ] **Design collection index pages**
  - `/collections/governance/index.html`
  - `/collections/administrative-data/index.html`
  - `/collections/teachers-association/index.html`

- [ ] **Create comparative analysis pages**
  - `/analysis/rural-vs-suburban-governance.html`
  - `/analysis/consolidation-patterns.html`
  - `/analysis/women-in-governance.html`

### Phase 5: Consolidated Artifacts Update

- [ ] **Update `scripts/consolidate_artifacts.py`**
  - Add collection assignment logic based on source series:
    - A4456 (Amityville) → Collection 2
    - A4645 (South-Kortright) → Collection 2
    - B0594 (Notecards) → Collection 3
    - B0494 (Consolidation) → Collection 3
  - Update output directory structure:
    - `output/archive/governance/` (Collection 2)
    - `output/archive/administrative-data/` (Collection 3)
    - `output/archive/teachers-association/` (Collection 1)

- [ ] **Update `scripts/generate_archive_manifest.py`**
  - Add `collection` field to manifest schema
  - Add `sub_collection` field (e.g., "Amityville Board Minutes")
  - Generate collection-level statistics
  - Update `output/archive/manifest.json`

### Phase 6: Documentation & Validation

- [ ] **Update CLAUDE.md**
  - Document 3-collection structure
  - Update "Current Work" section
  - Add collection descriptions to "Key Data Files"
  - Update OMEKA Integration section

- [ ] **Update README.md** (if exists)
  - Describe 3-collection organization
  - Add collection summaries
  - Link to collection markdown files

- [ ] **Create collection comparison matrix**
  - Document: `output/COLLECTION_COMPARISON.md`
  - Table showing themes, items, date ranges, research questions
  - Cross-reference guide

- [ ] **Validation checks**
  - Verify all 1,020 items accounted for
  - Check for duplicate entries
  - Validate GitHub CDN URLs
  - Test OMEKA CSV import
  - Verify collection totals match OCR page counts

### Phase 7: Search & Discovery Tools

- [ ] **Create thematic search query library**
  - Document: `scripts/queries/governance_queries.md`
    - Rural vs. suburban governance patterns
    - Women in governance (trustees, committee members)
    - Depression-era economic stress
    - Bureaucratic formalization
  - Document: `scripts/queries/administrative_queries.md`
    - Consolidation by county/decade
    - District name changes
    - Registration patterns

- [ ] **Create interactive timeline**
  - Tool: `dev/timeline/collection-timeline.html`
  - Visualize governance records chronologically
  - Toggle between Amityville and South-Kortright
  - Overlay with consolidation milestones

- [ ] **Create spatial visualization**
  - Extend `dev/leaflet/archive-map.html`
  - Add layer for Amityville (Suffolk County)
  - Add layer for South-Kortright (Delaware County)
  - Add consolidation county polygons from Collection 3

---

## File Inventory

### Files to Create
```
scripts/generate_governance_collection.py
scripts/generate_administrative_data_collection.py
output/collections/local-district-governance.md
output/collections/local-district-governance-stats.txt
output/collections/district-administrative-data.md
output/collections/district-administrative-data-stats.txt
output/omeka/items_import_v2.csv (backup old version)
output/COLLECTION_COMPARISON.md
scripts/queries/governance_queries.md
scripts/queries/administrative_queries.md
dev/timeline/collection-timeline.html
```

### Files to Update
```
scripts/generate_omeka_csv.py (major refactor)
scripts/consolidate_artifacts.py
scripts/generate_archive_manifest.py
dev/omeka/index.php
dev/omeka/css/style.css
output/omeka/OMEKA_SETUP_GUIDE.md
CLAUDE.md
README.md (if exists)
dev/leaflet/archive-map.html
```

### Files to Archive/Deprecate
```
scripts/generate_nys_local_records_collection.py → archive/
scripts/generate_county_collection.py → archive/
output/collections/nys-local-records.md → archive/
output/collections/district-consolidation-by-county.md → archive/
```

---

## Collection Statistics

### Current State (3 collections, mixed organization)
| Collection | Items | Status |
|------------|-------|--------|
| NYS Teachers Association | 249 | ✅ Complete |
| NYS Local Records (mixed) | 106 | 🔴 Needs split |
| District Consolidation | 100+ | 🔴 Needs merge |
| **Total** | **~355** | |

### Target State (3 collections, thematic organization)
| Collection | Items | Status |
|------------|-------|--------|
| NYS Teachers Association | 249 | ✅ Ready |
| Local District Governance | 708 | 🔴 Not started |
| District Administrative Data | 163 | 🔴 Not started |
| **Total** | **~1,120** | |

**Growth**: +765 items from adding Amityville (665 pages)

---

## Research Questions Enabled by Reorganization

### Collection 2: Governance Records

**Temporal Comparison**:
- How did governance formalize from 1810s (South-Kortright) to 1930s (Amityville)?
- What governance structures persisted across 100+ years?

**Urban/Rural Differences**:
- Board composition: elected trustees vs. informal selectmen?
- Meeting frequency and formality?
- Committee structure evolution?

**Gender & Civic Participation**:
- Women trustees in Amityville (Mrs. Hartman, Grace Burns)
- Gender in South-Kortright records?

**Economic Context**:
- Depression-era salary negotiations (Amityville 1932-1933)
- Agricultural economy in South-Kortright?

### Collection 3: Administrative Data

**Geographic Patterns**:
- Which counties consolidated most aggressively?
- Urban vs. rural consolidation rates?
- Regional clusters in notecard registrations?

**Temporal Patterns**:
- Consolidation timeline across NYS
- Peak years for district mergers?
- Name change patterns over time?

**Quantitative Analysis**:
- Consolidation type distribution (Central Rural vs. Union Free vs. Town Units)
- Districts per county before/after consolidation
- Registration actions by decade (notecards)

### Cross-Collection Analysis

**Governance → Administrative Outcomes**:
- Do Amityville board decisions align with consolidation trends?
- Link South-Kortright governance to county consolidation data?

**Teachers Association → Local Governance**:
- Do NYSTA advocacy positions appear in board minutes?
- Salary negotiation language comparison?

**All Three Collections**:
- Build complete picture of Common School → Modern Public Education transition
- Micro (board minutes) → Meso (advocacy) → Macro (statewide statistics)

---

## Implementation Priority

### High Priority (Do First)
1. ✅ Create TODO.md (this file)
2. ⬜ Create `scripts/generate_governance_collection.py`
3. ⬜ Create `scripts/generate_administrative_data_collection.py`
4. ⬜ Update `scripts/generate_omeka_csv.py`
5. ⬜ Update CLAUDE.md with new structure

### Medium Priority (Do Soon)
6. ⬜ Update OMEKA theme files (`dev/omeka/`)
7. ⬜ Create collection comparison matrix
8. ⬜ Generate new OMEKA CSV (~1,120 items)
9. ⬜ Test Docker OMEKA deployment

### Low Priority (Do Later)
10. ⬜ Create Jekyll collections (future platform)
11. ⬜ Build interactive timeline
12. ⬜ Extend spatial visualization
13. ⬜ Create thematic query libraries

---

## Notes & Caveats

### Why This Organization?

**Governance vs. Administration Split**:
- **Governance** = decision-making processes, debates, votes, temporal narratives
- **Administration** = outcomes, statistics, reference data, lookup tables

This distinction:
- Mirrors archival practice (correspondence vs. registers)
- Enables different research methods (qualitative vs. quantitative)
- Separates process from product

**Temporal Diversity in Collection 2**:
- 100+ year gap between South-Kortright and Amityville is INTENTIONAL
- Enables comparative analysis of governance evolution
- Shows continuity and change in school administration

**Geographic Coherence in Collection 3**:
- Both notecards and consolidation tables are statewide datasets
- Enable spatial analysis and mapping
- Natural fit for GIS/cartographic research

### Potential Issues

**OMEKA Collection Limits**:
- Check OMEKA Classic collection item limits
- May need pagination or sub-collection browsing

**CSV Import Size**:
- 1,120 items is large but manageable
- Test import performance in Docker environment
- Consider chunking if needed

**GitHub CDN URLs**:
- Verify all 665 Amityville pages have valid URLs
- Check for any URL pattern changes
- Test random sample of URLs before full import

---

## Success Criteria

- [ ] All 1,120 items organized into 3 thematic collections
- [ ] OMEKA CSV imports without errors
- [ ] Docker OMEKA displays all 3 collections correctly
- [ ] Collection markdown files generated and accurate
- [ ] CLAUDE.md reflects new structure
- [ ] No duplicate or missing items in reorganization
- [ ] Research questions documented for each collection
- [ ] Cross-collection comparison matrix complete

---

**Last Updated**: 2026-01-18
**Status**: Planning Phase - Awaiting Implementation
