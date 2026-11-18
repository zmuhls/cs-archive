"""Regression for county details reached from a real map tap or keyboard list."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
uri = (root / 'index.html').as_uri()
baseline = os.environ.get('ATLAS_COUNTY_BASELINE')
test_uri = Path(baseline).resolve().as_uri() if baseline else uri

# SVG bounding-box centers may fall outside a county or under the map legend.
# Choose an actual rendered point that the browser hit-tests to the polygon.
hit_test = """el => {
  const r = el.getBoundingClientRect();
  for (let i = 3; i < 17; i++) {
    for (let j = 3; j < 17; j++) {
      const x = r.left + i * r.width / 20, y = r.top + j * r.height / 20;
      if (document.elementFromPoint(x, y) === el) return [x, y];
    }
  }
  return null;
}"""

with sync_playwright() as p:
    args = {'executable_path': os.environ['CHROMIUM_BIN']} if os.environ.get('CHROMIUM_BIN') else {}
    browser = p.chromium.launch(**args)
    for width, height in [(320, 720), (390, 844), (1440, 900)]:
        mobile = width < 500
        page = browser.new_page(viewport={'width': width, 'height': height},
                                has_touch=mobile, is_mobile=mobile, reduced_motion='reduce')
        errors, requests = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: requests.append(request.url)
                if request.url.startswith(('https://', 'http://')) else None)
        page.goto(test_uri)
        county = page.locator('path[aria-label="Cayuga County"]')
        county.scroll_into_view_if_needed()
        hit = county.evaluate(hit_test)
        assert hit, 'No tappable Cayuga polygon'
        if mobile:
            page.touchscreen.tap(*hit)
        else:
            page.mouse.click(*hit)
        assert page.locator('#county').input_value() == 'Cayuga'
        title = page.locator('#record-title')
        if baseline:
            assert title.inner_text() == 'Records'
            assert not title.evaluate('el => el === document.activeElement')
            if mobile:
                top = title.evaluate('el => el.getBoundingClientRect().top')
                assert top >= height, (width, top)
            print(f'REPRODUCED at {width}: county filter changed, with no named/focused county account.')
            page.close()
            continue
        assert title.inner_text() == 'Cayuga County'
        assert title.evaluate('el => el === document.activeElement')
        assert title.evaluate('el => el.getBoundingClientRect().top >= 0 && el.getBoundingClientRect().bottom <= innerHeight')
        assert page.locator('#county-scope').count() == 0
        assert 'Moravia' in page.locator('#record-list article').first.inner_text()
        assert page.locator('#record-list .record-source strong').first.inner_text().strip() == 'Source:'
        assert page.locator('#record-list article').first.evaluate(
            "el => parseFloat(getComputedStyle(el.querySelector('p:not(.record-meta):not(.record-date)')).fontSize) >= 16")
        assert 'Review status' not in page.locator('#record-list').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.reload()
        assert title.inner_text() == 'Cayuga County'
        page.get_by_role('link', name='Read Cayuga County records').click()
        assert page.evaluate("location.hash.includes('county=Cayuga')")
        assert title.evaluate('el => el === document.activeElement')
        page.get_by_role('link', name='Back to map').click()
        assert page.locator('#map').evaluate('el => el === document.activeElement')
        page.locator('#county').focus()
        page.keyboard.press('Home')
        page.keyboard.press('ArrowDown')
        page.keyboard.press('Enter')
        assert 'Statewide' in title.inner_text()
        page.select_option('#county', 'Albany')
        assert 'County account forthcoming.' in page.locator('#record-list').inner_text()
        page.get_by_role('button', name='Show all counties').click()
        assert title.inner_text() == 'Records'
        assert title.evaluate('el => el === document.activeElement')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert requests == [] and errors == [], (requests, errors)
        print(f'PASS at {width}: actual county map tap/click, focus, reflow, provenance, persistent URL, keyboard filter and map return.')
        page.close()
