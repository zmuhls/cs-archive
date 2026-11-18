"""Check all 62 county views and a synthetic no-history fallback."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
url = (root / 'index.html').as_uri()
with sync_playwright() as playwright:
    kwargs = {'headless': True}
    if os.environ.get('CHROMIUM_BIN'):
        kwargs['executable_path'] = os.environ['CHROMIUM_BIN']
    browser = playwright.chromium.launch(**kwargs)
    for width in (320, 1440):
        page = browser.new_page(viewport={'width': width, 'height': 900},
                                is_mobile=width == 320, has_touch=width == 320)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(url)
        counties = page.evaluate('window.ATLAS_DATA.counties.features.map(row => row.properties.name)')
        assert len(counties) == len(set(counties)) == 62
        for county in counties:
            page.select_option('#county', county)
            rows = page.evaluate("""county => window.ATLAS_DATA.records.filter(record =>
              record.county === county && Number.isInteger(record.event_start) &&
              record.summary && record.source_url && record.source_locator
            ).map(record => record.id)""", county)
            visible = page.locator('#record-list article').evaluate_all(
                "cards => cards.map(card => ({id: card.id, source: !!card.querySelector('a[href^=\"https:\"]')}))")
            assert any(card['id'].removeprefix('record-') in rows and card['source'] for card in visible), county
            assert 'County account forthcoming.' not in page.locator('#record-list').inner_text(), county
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors, errors
        print(f'PASS {width}px: all 62 county views render at least one dated sourced account.')
        page.close()
    page = browser.new_page()
    page.add_init_script("""Object.defineProperty(window, 'ATLAS_DATA', {
      configurable: true, get() { return this.__fixture; },
      set(data) { this.__fixture = {...data, records: data.records.filter(row => row.county !== 'Albany')}; }
    });""")
    page.goto(url)
    page.select_option('#county', 'Albany')
    assert page.locator('#record-list').inner_text() == 'County account forthcoming.'
    assert page.locator('#record-list article').count() == 0
    print('PASS: synthetic empty county renders only its short placeholder.')
    browser.close()
