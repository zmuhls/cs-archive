# OMEKA Setup & Import Guide for Common School Archive

## Overview

This guide walks through the final steps to integrate the Common School Archive collections into your local OMEKA Classic instance. All data is ready—you now need to:

1. Verify OMEKA is running and configured
2. Create the two collections
3. Import the CSV data
4. Configure collection descriptions
5. Test the frontend

---

## Prerequisites

- OMEKA Classic installed and running locally (http://localhost or similar)
- Admin access to the OMEKA dashboard
- CSV Import plugin installed (Settings > Plugins)
- "Thanks, Roy" theme active (already installed in `dev/omeka/`)

---

## Step 1: Verify OMEKA Installation

### Check OMEKA Status

1. Visit your OMEKA instance: `http://localhost` (or your configured URL)
2. Log in to the admin panel with your credentials
3. Confirm you see: Dashboard > Collections > Items > Settings

### Check CSV Import Plugin

1. Go to **Settings** > **Plugins** in the admin panel
2. Look for "CSV Import" in the plugin list
3. If not installed:
   - Click "Find More Plugins"
   - Search for "CSV Import"
   - Install and activate

If the CSV Import plugin is not available, contact the OMEKA developers for installation instructions specific to your version.

---

## Step 2: Create Collections

### Collection 1: NYS Teachers' Association

1. Go to **Collections** in the admin panel
2. Click **Add a Collection**
3. Fill in:
   - **Title**: `NYS Teachers' Association (1845-1940s)`
   - **Description**: Copy from `output/omeka/collection_1_teachers.md`
   - **Public**: Check (yes)
4. Click **Add Collection**

Note the **collection ID** (visible in the URL or collection list)—it should be **1**

### Collection 2: District Consolidation Records

1. Click **Add a Collection** again
2. Fill in:
   - **Title**: `District Consolidation Records`
   - **Description**: Copy from `output/omeka/collection_2_consolidation.md`
   - **Public**: Check (yes)
3. Click **Add Collection**

Note the **collection ID** (should be **2**)

### ⚠️ Important

If the collection IDs are NOT 1 and 2, you must update `dev/omeka/index.php`:

- Find lines 16 and 22
- Replace `array('id' => 1)` with the actual Teachers' Association collection ID
- Replace `array('id' => 2)` with the actual District Consolidation collection ID

---

## Step 3: Import CSV Data

### Prepare Import

1. Go to **Plugins** in the admin panel
2. Click **CSV Import**
3. Click **Start Import**

### Upload CSV File

1. Click **Choose File**
2. Select: `/path/to/cs-archive/output/omeka/items_import.csv`
3. Click **Upload**

### Map CSV Columns to OMEKA Elements

The CSV Import plugin will display a preview with column headers. Map each column:

| CSV Column | OMEKA Element | Type |
|---|---|---|
| `collection` | Dublin Core: Relation | Text |
| `title` | Dublin Core: Title | Text |
| `date` | Dublin Core: Date | Text |
| `description` | Dublin Core: Description | Text |
| `type` | Dublin Core: Type | Text |
| `spatial` | Dublin Core: Spatial | Text |
| `subject` | Dublin Core: Subject | Text |
| `source` | Dublin Core: Source | Text |
| `identifier` | Dublin Core: Identifier | Text |
| `file` | Files | File URL |

### Set Collection Assignment

1. In the CSV Import configuration, look for "Collection" mapping
2. For the `collection` column:
   - If value = "NYS Teachers' Association" → assign to Collection 1
   - If value = "District Consolidation Records" → assign to Collection 2

(This might be automatic if the plugin recognizes collection titles, or manual if you need to map values)

### Configure Item Type Mapping

1. Most items will import as generic "Items"
2. The CSV includes a `type` column with Dublin Core types (Text, Dataset, Image)
3. You can optionally create corresponding OMEKA item types if desired
4. For now, leaving them as generic "Items" is fine

### Set File Handling

1. For the `file` column:
   - Select **File URLs** (not upload)
   - URLs from GitHub CDN will be used as external file references
   - OMEKA will fetch and display images from GitHub

2. Click **Map Column to Files**

### Review & Import

1. Review the preview showing how items will be imported
2. Click **Import**
3. Wait for completion (249 items will take 2-5 minutes depending on server)
4. You should see a success message with item count

---

## Step 4: Verify Import

### Check Items Created

1. Go to **Items** in the admin panel
2. Should show **249 items** total
3. Filter or search to confirm:
   - ~115 items with "District Consolidation Records" in the collection field
   - ~134 items with "NYS Teachers' Association" in the collection field

### Check Image Display

1. Click on any item in the list
2. Scroll to view the attached file from GitHub
3. The image should display from the GitHub CDN URL
4. If image doesn't load, check:
   - Is GitHub repository public?
   - Are URLs correct in CSV?

### Check Collection Assignment

1. Go to **Collections** > click on **Teachers' Association**
2. Browse > Items should show ~134 items
3. Go to **Collections** > click on **District Consolidation**
4. Browse > Items should show ~115 items

---

## Step 5: Configure Homepage

### Set Homepage Text

1. Go to **Settings** > **Theme**
2. Look for "Homepage Text" field
3. Copy the content from `output/omeka/homepage_intro.md` into this field
4. Save

### Verify Collections Grid

1. Visit your OMEKA homepage: `http://localhost`
2. You should see:
   - Site introduction text at top
   - **Featured Collections** grid with two cards:
     - "NYS Teachers' Association Materials"
     - "District Consolidation Records"
   - Each card shows collection description and "Explore Collection" link
3. Click each link to verify it navigates to the correct collection browse page

---

## Step 6: Add Context Pages (Optional)

You can create additional pages to provide historical context:

1. Go to **Plugins** > **Simple Pages** (if installed)
2. Create new page: "About"
3. Paste content from `output/omeka/about_page.md`
4. Add to main navigation
5. Repeat with `output/omeka/collection_1_teachers.md` and `output/omeka/collection_2_consolidation.md` if desired

---

## Troubleshooting

### Items don't appear in collections

**Problem**: Items imported but don't show in collection browse

**Solution**:
1. Check CSV mapping: `collection` column should map to the collection
2. Verify collection IDs match (1 and 2)
3. Reimport with correct mappings

### Images don't display

**Problem**: File URLs show in OMEKA but images don't load

**Cause**: GitHub URLs might be blocked or incorrect

**Solution**:
1. Verify GitHub repo is public
2. Test URL in browser: `https://raw.githubusercontent.com/zmuhls/csa/main/raw/scans/img/IMG_0625.jpeg`
3. If working, check OMEKA file settings
4. Consider uploading images locally instead of using GitHub CDN

### Collections grid doesn't display

**Problem**: Homepage shows text but no collection cards

**Cause**: Theme modification not applied

**Solution**:
1. Verify `dev/omeka/index.php` was modified
2. Check that collection IDs in links are correct
3. Clear OMEKA cache (if applicable)
4. Restart OMEKA

### Wrong collection IDs

**Problem**: Collections grid links to wrong collections

**Solution**:
1. Check actual collection IDs in OMEKA admin
2. Update `dev/omeka/index.php` lines 16 and 22 with correct IDs
3. Reload homepage

---

## Next Steps

Once import is complete and verified:

1. **Customize**: Adjust colors, fonts, and layouts in theme settings
2. **Enhance**: Add exhibit pages, guides, or additional context
3. **Publish**: Deploy to production web server
4. **Promote**: Share collections with educators, historians, and researchers

---

## Support Resources

- **OMEKA Documentation**: https://omeka.org/classic/docs/
- **CSV Import Plugin Docs**: https://omeka.org/classic/plugins/CsvImport/
- **Thanks, Roy Theme**: `dev/omeka/README.md`

---

## Files Reference

All preparation files are in `output/omeka/`:

| File | Purpose |
|---|---|
| `items_import.csv` | Main import file (249 rows) |
| `homepage_intro.md` | Homepage introduction text |
| `collection_1_teachers.md` | Teachers' Association description |
| `collection_2_consolidation.md` | District Consolidation description |
| `about_page.md` | Full historical narrative (optional) |
| `THEME_MODIFICATIONS.md` | Summary of theme changes |
| `OMEKA_SETUP_GUIDE.md` | This file |

---

**Ready to import? Start with Step 1!**
