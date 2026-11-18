"""Verify quiet default map/sidebar, optional context, and controls."""
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

atlas = Path(__file__).resolve().parents[1]
baseline = os.environ.get('ATLAS_SIDEBAR_BASELINE')

with sync_playwright() as p:
    kwargs = {'executable_path': os.environ['CHROMIUM_BIN']} if os.environ.get('CHROMIUM_BIN') else {}
    browser = p.chromium.launch(**kwargs)
    for width in [320, 390, 1440]:
        page = browser.new_page(viewport={'width': width, 'height': 900},
                                is_mobile=width < 500, has_touch=width < 500)
        measure = """() => {
          const top = s => document.querySelector(s).getBoundingClientRect().top;
          return Math.round(top('#record-list article') - top('#records'));
        }"""
        if baseline:
            page.goto(Path(baseline).resolve().as_uri())
            previous = page.evaluate(measure)
            assert page.locator('#period-detail').is_visible()
        page.goto((atlas / 'index.html').as_uri())
        assert not page.locator('#period-detail').is_visible()
        assert not page.locator('.map-legend').is_visible()
        assert not page.get_by_role('button', name='Clear filters').is_visible()
        assert re.fullmatch(r'\d+ records', page.locator('#results-count').inner_text())
        assert page.locator('#record-list article .record-source a').first.is_visible()
        assert page.locator('#record-list article .record-source a').first.get_attribute('href').startswith('https:')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        if baseline:
            current = page.evaluate(measure)
            assert current < previous - 60, (width, previous, current)
            print(f'{width}px: first record moved {previous-current}px closer, {previous}px → {current}px from sidebar top.')
        key = page.get_by_text('Map key & scope', exact=True)
        key.focus()
        page.keyboard.press('Enter')
        assert page.locator('.map-legend').is_visible()
        assert page.locator('#period-detail').is_visible()
        assert '2024 county boundaries' in page.locator('#map-caption').inner_text()
        page.keyboard.press('Enter')
        assert not page.locator('.map-legend').is_visible()
        page.select_option('#county','Cayuga')
        assert page.locator('#county-scope').count() == 0
        assert page.locator('#record-list article .record-source a').first.is_visible()
        page.get_by_role('button',name='Clear filters').click()
        assert not page.get_by_role('button',name='Clear filters').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.close()
    print('PASS: compact sidebar, source link, persistent county controls, disclosure keyboard, and reflow.')
