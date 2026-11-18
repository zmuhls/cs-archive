# Verification

Local Chromium tests: 62 map polygons; county, date, type, and text controls; keyboard skip links and approximate schoolhouse markers; source disclosures; browsing retake labels; persistent filter state; desktop and 390 px mobile; independent results when Leaflet is unavailable; no external runtime requests. Test commands are in the README.

This publication subset does not include Newberry geometries or unpublished research leads. External source links and historical map interpretation are not guaranteed by browser tests.

## County account navigation

Run `python3 tests/county_details_browser.py` with Playwright Chromium (optionally set `CHROMIUM_BIN`). It hit-tests real SVG county polygons, then taps them at 320 px and 390 px or clicks them at 1440 px. It checks named account group, viewport and keyboard focus, reflow and readable record text, scope and source details, stable county links after reload, keyboard county choice, map return, uncovered-county caveats, and zero external runtime requests. Set `ATLAS_COUNTY_BASELINE` to the prior checkout's `index.html` to reproduce the original offscreen results at phone widths. The checks are not a physical iPhone or screen-reader test.
