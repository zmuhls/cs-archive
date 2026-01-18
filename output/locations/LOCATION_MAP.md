# Location Map — Common School Archive

This document catalogs all geographic locations referenced in the archive, organized by collection. It serves as a data source for mapping visualizations and spatial analysis.

---

## Quick Reference

| Collection | Location Type | Count |
|------------|---------------|-------|
| NYS Teachers' Association | Meeting Cities | 14 unique cities |
| District Consolidation | Counties | 30 NY counties |
| District Consolidation | Towns/Districts | 200+ towns |

---

## NYS Teachers' Association Meeting Locations

Conference and proceeding locations extracted from the NYSTA collection (1845-1940s).

### Confirmed Meeting Sites (Chronological)

| Year | City | State | Notes | Source Image |
|------|------|-------|-------|--------------|
| 1881 | Saratoga | NY | Annual meeting | IMG_0694 |
| 1882 | Yonkers | NY | Annual meeting | IMG_0707 |
| 1884 | Elmira | NY | Baldwin Street location | IMG_0727 |
| 1887 | Elizabethtown | NY | Essex County courthouse | IMG_0729, IMG_0730 |
| 1888 | Watkins | NY | (Watkins Glen area) | IMG_0739 |
| 1889 | Brooklyn | NY | Annual meeting | IMG_0740, IMG_3344, IMG_3345 |
| 1890 | Saratoga Springs | NY | Annual meeting | IMG_0741 |
| 1891 | Saratoga Springs | NY | Annual meeting | IMG_0774 |
| 1894 | Saratoga Springs | NY | Annual meeting | IMG_0776, IMG_3357 |
| 1895 | Syracuse | NY | Annual meeting | IMG_0792 |
| 1896 | New York City | NY | Annual meeting | IMG_3363 |
| 1897 | Rochester | NY | Joint meeting with NYC | IMG_0795 |
| 1897 | New York City | NY | Annual meeting | IMG_3362, IMG_3374 |
| 1898 | Rochester | NY | Annual meeting | IMG_0809 |
| 1900 | Thousand Islands | NY | Summer meeting | IMG_0671 |
| 1901 | Buffalo | NY | Annual meeting | IMG_0672-IMG_0676 |
| 1902 | Saratoga | NY | Annual meeting | IMG_0677 |
| 1905 | Syracuse | NY | Annual meeting | IMG_0684 |
| 1906 | Syracuse | NY | Annual meeting | IMG_0692 |
| 1911 | New York City | NY | Annual meeting | IMG_3388 |
| 1927 | Utica | NY | Event location (Albany publisher) | IMG_0654 |

### Additional Venue References

| Location | Type | Notes | Source |
|----------|------|-------|--------|
| Fort William Henry Hotel, Fort Edward | Hotel/Venue | Conference venue | IMG_0726 |
| Cliff Haven | Town | Summer school/retreat | IMG_0680 |
| Albany | City | Publisher location, statewide admin | Multiple |

### NYSTA Location Coordinates (for mapping)

```json
{
  "type": "FeatureCollection",
  "features": [
    {"type": "Feature", "properties": {"name": "Albany", "type": "administrative", "years": ["1927"]}, "geometry": {"type": "Point", "coordinates": [-73.7562, 42.6526]}},
    {"type": "Feature", "properties": {"name": "Brooklyn", "type": "meeting", "years": ["1889"]}, "geometry": {"type": "Point", "coordinates": [-73.9442, 40.6782]}},
    {"type": "Feature", "properties": {"name": "Buffalo", "type": "meeting", "years": ["1901"]}, "geometry": {"type": "Point", "coordinates": [-78.8784, 42.8864]}},
    {"type": "Feature", "properties": {"name": "Cliff Haven", "type": "venue", "years": []}, "geometry": {"type": "Point", "coordinates": [-73.4279, 44.8789]}},
    {"type": "Feature", "properties": {"name": "Elizabethtown", "type": "meeting", "years": ["1887"]}, "geometry": {"type": "Point", "coordinates": [-73.5907, 44.2156]}},
    {"type": "Feature", "properties": {"name": "Elmira", "type": "meeting", "years": ["1884"]}, "geometry": {"type": "Point", "coordinates": [-76.8077, 42.0898]}},
    {"type": "Feature", "properties": {"name": "Fort Edward", "type": "venue", "years": []}, "geometry": {"type": "Point", "coordinates": [-73.5882, 43.2670]}},
    {"type": "Feature", "properties": {"name": "New York City", "type": "meeting", "years": ["1896", "1897", "1911"]}, "geometry": {"type": "Point", "coordinates": [-74.0060, 40.7128]}},
    {"type": "Feature", "properties": {"name": "Rochester", "type": "meeting", "years": ["1897", "1898"]}, "geometry": {"type": "Point", "coordinates": [-77.6109, 43.1566]}},
    {"type": "Feature", "properties": {"name": "Saratoga", "type": "meeting", "years": ["1881", "1902"]}, "geometry": {"type": "Point", "coordinates": [-73.7854, 43.0831]}},
    {"type": "Feature", "properties": {"name": "Saratoga Springs", "type": "meeting", "years": ["1890", "1891", "1894"]}, "geometry": {"type": "Point", "coordinates": [-73.7854, 43.0831]}},
    {"type": "Feature", "properties": {"name": "Syracuse", "type": "meeting", "years": ["1895", "1905", "1906"]}, "geometry": {"type": "Point", "coordinates": [-76.1474, 43.0481]}},
    {"type": "Feature", "properties": {"name": "Thousand Islands", "type": "meeting", "years": ["1900"]}, "geometry": {"type": "Point", "coordinates": [-75.9180, 44.3500]}},
    {"type": "Feature", "properties": {"name": "Utica", "type": "meeting", "years": ["1927"]}, "geometry": {"type": "Point", "coordinates": [-75.2327, 43.1009]}},
    {"type": "Feature", "properties": {"name": "Watkins Glen", "type": "meeting", "years": ["1888"]}, "geometry": {"type": "Point", "coordinates": [-76.8733, 42.3806]}},
    {"type": "Feature", "properties": {"name": "Yonkers", "type": "meeting", "years": ["1882"]}, "geometry": {"type": "Point", "coordinates": [-73.8987, 40.9312]}}
  ]
}
```

---

## District Consolidation Data — Counties

Data from NYS Archives Series A4456 (1845-1940s), documenting school district consolidations across New York State.

### Counties with Consolidation Records

| County | Pages | Table Types | Region |
|--------|-------|-------------|--------|
| Broome | 3 | Consolidated, Central Rural | Southern Tier |
| Cattaraugus | 5 | Union Free, Town, Consolidated, Central Rural | Western NY |
| Cayuga | 4 | Union Free, Town, Consolidated, Central Rural | Finger Lakes |
| Chautauqua | 5 | Union Free, Town, Central Rural | Western NY |
| Chemung | 3 | Union Free | Southern Tier |
| Chenango | 6 | Union Free, Town, Consolidated, Central Rural | Central NY |
| Clinton | 5 | Union Free, Town, Central Rural, Consolidated | North Country |
| Columbia | 3 | Union Free, Town, Consolidated | Hudson Valley |
| Cortland | 3 | Union Free, Consolidated | Central NY |
| Delaware | 6 | Union Free, Town, Consolidated, Central Rural | Catskills |
| Dutchess | 4 | Union Free, Town, Consolidated, Central Rural | Hudson Valley |
| Erie | 4 | Union Free, Consolidated, Central Rural | Western NY |
| Essex | 4 | Union Free, Consolidated | Adirondacks |
| Franklin | 3 | Union Free, Town, Consolidated | North Country |
| Fulton | 3 | Consolidated | Mohawk Valley |
| Genesee | 1 | Consolidated | Western NY |
| Greene | 4 | Union Free, Town, Consolidated, Central Rural | Catskills |
| Hamilton | 2 | Union Free, Consolidated | Adirondacks |
| Herkimer | 5 | Union Free, Town, Consolidated, Central Rural | Mohawk Valley |
| Jefferson | 5 | Union Free, Town, Consolidated, Central Rural | North Country |
| Lewis | 4 | Union Free, Town, Consolidated | North Country |
| Livingston | 4 | Union Free, Town, Central Rural | Finger Lakes |
| Madison | 6 | Union Free, Town, Consolidated, Central Rural | Central NY |
| Monroe | 3 | Union Free, Consolidated, Central Rural | Western NY |
| Montgomery | 3 | Union Free, Consolidated | Mohawk Valley |
| Nassau | 4 | Union Free, Consolidated | Long Island |
| Niagara | 2 | Union Free | Western NY |
| Oneida | 5 | Union Free, Town, Consolidated, Central Rural | Mohawk Valley |
| Onondaga | 5 | Union Free, Town, Consolidated, Central Rural | Central NY |

### County Coordinates (for mapping)

```json
{
  "type": "FeatureCollection",
  "features": [
    {"type": "Feature", "properties": {"name": "Broome County", "pages": 3, "region": "Southern Tier"}, "geometry": {"type": "Point", "coordinates": [-75.9180, 42.1605]}},
    {"type": "Feature", "properties": {"name": "Cattaraugus County", "pages": 5, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-78.6788, 42.2487]}},
    {"type": "Feature", "properties": {"name": "Cayuga County", "pages": 4, "region": "Finger Lakes"}, "geometry": {"type": "Point", "coordinates": [-76.5604, 42.9267]}},
    {"type": "Feature", "properties": {"name": "Chautauqua County", "pages": 5, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-79.4139, 42.2973]}},
    {"type": "Feature", "properties": {"name": "Chemung County", "pages": 3, "region": "Southern Tier"}, "geometry": {"type": "Point", "coordinates": [-76.7567, 42.1447]}},
    {"type": "Feature", "properties": {"name": "Chenango County", "pages": 6, "region": "Central NY"}, "geometry": {"type": "Point", "coordinates": [-75.6100, 42.4935]}},
    {"type": "Feature", "properties": {"name": "Clinton County", "pages": 5, "region": "North Country"}, "geometry": {"type": "Point", "coordinates": [-73.6778, 44.7489]}},
    {"type": "Feature", "properties": {"name": "Columbia County", "pages": 3, "region": "Hudson Valley"}, "geometry": {"type": "Point", "coordinates": [-73.6312, 42.2501]}},
    {"type": "Feature", "properties": {"name": "Cortland County", "pages": 3, "region": "Central NY"}, "geometry": {"type": "Point", "coordinates": [-76.0644, 42.5962]}},
    {"type": "Feature", "properties": {"name": "Delaware County", "pages": 6, "region": "Catskills"}, "geometry": {"type": "Point", "coordinates": [-74.9163, 42.1979]}},
    {"type": "Feature", "properties": {"name": "Dutchess County", "pages": 4, "region": "Hudson Valley"}, "geometry": {"type": "Point", "coordinates": [-73.7478, 41.7650]}},
    {"type": "Feature", "properties": {"name": "Erie County", "pages": 4, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-78.7998, 42.7523]}},
    {"type": "Feature", "properties": {"name": "Essex County", "pages": 4, "region": "Adirondacks"}, "geometry": {"type": "Point", "coordinates": [-73.7715, 44.1165]}},
    {"type": "Feature", "properties": {"name": "Franklin County", "pages": 3, "region": "North Country"}, "geometry": {"type": "Point", "coordinates": [-74.3046, 44.5929]}},
    {"type": "Feature", "properties": {"name": "Fulton County", "pages": 3, "region": "Mohawk Valley"}, "geometry": {"type": "Point", "coordinates": [-74.4235, 43.1142]}},
    {"type": "Feature", "properties": {"name": "Genesee County", "pages": 1, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-78.1939, 43.0009]}},
    {"type": "Feature", "properties": {"name": "Greene County", "pages": 4, "region": "Catskills"}, "geometry": {"type": "Point", "coordinates": [-74.1274, 42.2792]}},
    {"type": "Feature", "properties": {"name": "Hamilton County", "pages": 2, "region": "Adirondacks"}, "geometry": {"type": "Point", "coordinates": [-74.4971, 43.6573]}},
    {"type": "Feature", "properties": {"name": "Herkimer County", "pages": 5, "region": "Mohawk Valley"}, "geometry": {"type": "Point", "coordinates": [-74.9621, 43.4195]}},
    {"type": "Feature", "properties": {"name": "Jefferson County", "pages": 5, "region": "North Country"}, "geometry": {"type": "Point", "coordinates": [-75.9801, 44.0015]}},
    {"type": "Feature", "properties": {"name": "Lewis County", "pages": 4, "region": "North Country"}, "geometry": {"type": "Point", "coordinates": [-75.4486, 43.7846]}},
    {"type": "Feature", "properties": {"name": "Livingston County", "pages": 4, "region": "Finger Lakes"}, "geometry": {"type": "Point", "coordinates": [-77.7658, 42.7278]}},
    {"type": "Feature", "properties": {"name": "Madison County", "pages": 6, "region": "Central NY"}, "geometry": {"type": "Point", "coordinates": [-75.6697, 42.9126]}},
    {"type": "Feature", "properties": {"name": "Monroe County", "pages": 3, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-77.6109, 43.1566]}},
    {"type": "Feature", "properties": {"name": "Montgomery County", "pages": 3, "region": "Mohawk Valley"}, "geometry": {"type": "Point", "coordinates": [-74.4396, 42.9028]}},
    {"type": "Feature", "properties": {"name": "Nassau County", "pages": 4, "region": "Long Island"}, "geometry": {"type": "Point", "coordinates": [-73.5594, 40.7408]}},
    {"type": "Feature", "properties": {"name": "Niagara County", "pages": 2, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-78.8314, 43.2205]}},
    {"type": "Feature", "properties": {"name": "Oneida County", "pages": 5, "region": "Mohawk Valley"}, "geometry": {"type": "Point", "coordinates": [-75.4346, 43.2412]}},
    {"type": "Feature", "properties": {"name": "Onondaga County", "pages": 5, "region": "Central NY"}, "geometry": {"type": "Point", "coordinates": [-76.1949, 43.0063]}}
  ]
}
```

---

## District Consolidation Data — Towns

Town-level locations extracted from the consolidation tables. Sample from Broome County:

### Broome County Towns

| Town | District Types | Date Range | Notes |
|------|---------------|------------|-------|
| Barker | Consolidated, Central Rural | 1934 | Part of multi-town CRS |
| Chenango | Central Rural | 1934 | Combined with Barker, Maine |
| Colesville | Consolidated | 1914-1932 | Multiple consolidation attempts |
| Conklin | Consolidated | 1917 | Districts 1, 2, 8 merged |
| Dickinson | Consolidated | 1915-1917 | Combined with Kirkwood, Fenton |
| Fenton | Consolidated, Central Rural | 1915-1932 | Multiple consolidations |
| Kirkwood | Consolidated | 1915 | Combined with Dickinson |
| Lisle | Consolidated | 1920-1921 | Part of multi-town CRS |
| Maine | Consolidated, Central Rural | 1919-1934 | Part of multi-town CRS |
| Nanticoke | Consolidated, Central Rural | 1934 | Part of Triangle CRS |
| Newark Valley | Consolidated | 1919 | Cross-county (Tioga) |
| Richford | Consolidated | 1919-1924 | Cross-county (Tioga) |
| Sanford | Consolidated | 1914-1915 | Districts 17, 18, 19 |
| Triangle | Central Rural | 1934 | Large multi-town CRS |
| Union | Consolidated | 1923 | Village district |
| Windsor | Consolidated, Central Rural | 1931-1932 | Combined with Colesville |

---

## Next Steps for Mapping

### Jekyll Integration

1. **GeoJSON files** — Extract the JSON blocks above into standalone `.geojson` files
2. **Leaflet map** — Build on existing `dev/leaflet/` work to visualize locations
3. **Collection pages** — Link map markers to document collections

### Data Enrichment Needed

- [ ] Geocode remaining town-level locations
- [ ] Add building/venue addresses where known
- [ ] Cross-reference with NYS GIS data for historical boundaries
- [ ] Add temporal layers showing consolidation progression

### File Locations

| Resource | Path |
|----------|------|
| NYSTA Collection | `output/collections/nys-teachers-association.md` |
| County Collection | `output/collections/district-consolidation-by-county.md` |
| Table CSVs | `output/ocr/tables/csv/District-Consolidation-Data_*.csv` |
| Table Markdown | `output/ocr/tables/markdown/District-Consolidation-Data_*.md` |
| Leaflet Dev | `dev/leaflet/` |

---

## Regeneration

To refresh this location map from source data:

```bash
# Future script (not yet implemented)
python scripts/generate_location_map.py
```

---

*Generated: 2026-01-17*
*Source: Comprehensive review of archive locational data*
