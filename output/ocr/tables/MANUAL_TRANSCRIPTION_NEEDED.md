# Manual Transcription Required

## Summary

**Automated extraction using Qwen VL Plus successfully processed 60 pages (51%).**

**56 pages require manual transcription** due to API response truncation at ~4000 characters. These are mostly large Consolidated Districts tables with 20+ rows.

## Failed Pages List

Pages requiring manual transcription (sorted by page number):

```
3, 4, 5, 8, 9, 13, 14, 17, 18, 21, 22, 25, 26, 27, 33, 36, 37, 38, 39,
42, 43, 44, 48, 50, 51, 52, 56, 57, 60, 61, 64, 67, 72, 73, 74, 78, 79,
83, 84, 87, 88, 91, 92, 93, 95, 96, 102, 103, 106, 107, 109, 110, 111,
112, 114, 115
```

**Total: 56 pages**

## Source Images

All page images are available at:
- **Location:** `output/ocr/tables/images/`
- **Format:** `District-Consolidation-Data_100-116_page_{N}.jpg`
- **Resolution:** 300 DPI

Example: `District-Consolidation-Data_100-116_page_3.jpg`

## Table Schema for Manual Entry

### Standard Fields

All tables should include these fields in the JSON output:

```json
{
  "metadata": {
    "source_pdf": "District-Consolidation-Data_100-116.pdf",
    "page_number": 3,
    "county": "County Name",
    "table_type": "union_free_schools|town_school_units|consolidated_districts|central_rural_schools",
    "transcribed_manually": true,
    "transcribed_by": "Your Name",
    "transcribed_at": "2025-12-31"
  },
  "table": {
    "headers": ["field1", "field2", "field3", ...],
    "rows": [
      {"field1": "value1", "field2": "value2", ...},
      {"field1": "value1", "field2": "value2", ...}
    ]
  }
}
```

### Common Table Types & Headers

#### Consolidated Districts (most common)
```json
{
  "headers": [
    "no_of_district",
    "name_of_town",
    "date_organizing_day",
    "date_organizing_month",
    "date_organizing_year",
    "date_approved_day",
    "date_approved_month",
    "date_approved_year",
    "no_new_district",
    "remarks"
  ]
}
```

#### Union Free Schools
```json
{
  "headers": [
    "no_of_district",
    "name_of_town",
    "date_organizing_day",
    "date_organizing_month",
    "date_organizing_year",
    "date_approved_day",
    "date_approved_month",
    "date_approved_year",
    "number_of_papers",
    "remarks"
  ]
}
```

#### Town School Units
```json
{
  "headers": [
    "no_of_unit",
    "name_of_town",
    "districts_included",
    "date_organizing",
    "date_approved",
    "remarks"
  ]
}
```

## Transcription Guidelines

### Data Entry Rules

1. **Preserve exact spelling** - Keep period abbreviations ("inst.", "Ag" for August)
2. **Blank cells** - Use `null` for empty cells
3. **Merged cells** - Repeat the value across rows
4. **Split dates** - Keep day/month/year separate if columns are split
5. **Combined dates** - Single field if written together (e.g., "6 July 1915")
6. **Unclear text** - Mark as `"[unclear]"` rather than guessing
7. **Nested data** - For Town Units, preserve full text like "U.F.S. 17 and 3, 6, 9..."

### File Naming

Save manually transcribed files to:
- **JSON:** `output/ocr/tables/json/District-Consolidation-Data_100-116_page_{N}.json`
- **CSV:** `output/ocr/tables/csv/District-Consolidation-Data_100-116_page_{N}.csv`

Match the naming convention of automated extractions.

## Example Manual Transcription

### Source Image
`output/ocr/tables/images/District-Consolidation-Data_100-116_page_3.jpg`

### JSON Output
```json
{
  "metadata": {
    "source_pdf": "District-Consolidation-Data_100-116.pdf",
    "source_pdf_path": "/Users/zacharymuhlbauer/Desktop/studio/projects/cs-archive/raw/scans/NYS Archives/B0494/District-Consolidation-Data_100-116.pdf",
    "page_number": 3,
    "page_image_path": "/Users/zacharymuhlbauer/Desktop/studio/projects/cs-archive/output/ocr/tables/images/District-Consolidation-Data_100-116_page_3.jpg",
    "processed_at": "2025-12-31T19:00:00.000000",
    "model": "manual",
    "county": "Broome",
    "table_type": "consolidated_districts",
    "transcribed_manually": true,
    "transcribed_by": "Your Name",
    "transcribed_at": "2025-12-31"
  },
  "table": {
    "headers": [
      "no_of_district",
      "name_of_town",
      "date_organizing",
      "date_approved",
      "no_new_district",
      "remarks"
    ],
    "rows": [
      {
        "no_of_district": "548",
        "name_of_town": "Fenton",
        "date_organizing": "6 July 1915",
        "date_approved": "5-22 Ag 1915",
        "no_new_district": "5 Fenton",
        "remarks": "Consol appealed 4 dist"
      }
    ]
  }
}
```

## Progress Tracking

Create a checklist as you complete pages:

```markdown
### Pages 1-20
- [ ] Page 3 - Broome County, Consolidated Districts
- [ ] Page 4
- [ ] Page 5
- [ ] Page 8
- [ ] Page 9
- [ ] Page 13
- [ ] Page 14
- [ ] Page 17
- [ ] Page 18

### Pages 21-40
- [ ] Page 21
- [ ] Page 22
- [ ] Page 25
- [ ] Page 26
- [ ] Page 27
- [ ] Page 33
- [ ] Page 36
- [ ] Page 37
- [ ] Page 38
- [ ] Page 39

### Pages 41-60
- [ ] Page 42
- [ ] Page 43
- [ ] Page 44
- [ ] Page 48
- [ ] Page 50
- [ ] Page 51
- [ ] Page 52
- [ ] Page 56
- [ ] Page 57
- [ ] Page 60

### Pages 61-80
- [ ] Page 61
- [ ] Page 64
- [ ] Page 67
- [ ] Page 72
- [ ] Page 73
- [ ] Page 74
- [ ] Page 78
- [ ] Page 79

### Pages 81-100
- [ ] Page 83
- [ ] Page 84
- [ ] Page 87
- [ ] Page 88
- [ ] Page 91
- [ ] Page 92
- [ ] Page 93
- [ ] Page 95
- [ ] Page 96

### Pages 101-116
- [ ] Page 102
- [ ] Page 103
- [ ] Page 106
- [ ] Page 107
- [ ] Page 109
- [ ] Page 110
- [ ] Page 111
- [ ] Page 112
- [ ] Page 114
- [ ] Page 115
```

## CSV Generation (Optional)

After creating the JSON, you can generate CSV automatically using:

```bash
python scripts/json_to_csv_converter.py --page 3
```

Or manually create CSV with these columns (example for Consolidated Districts):

```csv
source_pdf,page_number,county,table_type,row_index,no_of_district,name_of_town,date_organizing,date_approved,no_new_district,remarks
District-Consolidation-Data_100-116.pdf,3,Broome,consolidated_districts,1,548,Fenton,6 July 1915,5-22 Ag 1915,5 Fenton,Consol appealed 4 dist
```

## Estimated Effort

- **Average time per page:** 10-15 minutes (based on table complexity)
- **Total estimated time:** 9-14 hours for all 56 pages
- **Recommendation:** Transcribe in batches of 5-10 pages per session

## Quality Assurance

Before considering a page complete:

1. ✓ Count rows in source image vs JSON (must match exactly)
2. ✓ Verify all columns are present
3. ✓ Check county name is correct
4. ✓ Confirm table type classification
5. ✓ Spot-check 3-5 random entries for accuracy
6. ✓ Ensure JSON is valid (test with `python -m json.tool file.json`)
7. ✓ Generate CSV successfully

## Contact

If you have questions about transcription standards or encounter unusual table formats, document them in a separate `TRANSCRIPTION_NOTES.md` file for consistency across pages.
