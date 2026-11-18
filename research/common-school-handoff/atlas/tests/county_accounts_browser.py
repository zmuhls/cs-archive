"""Exercise the compact, progressively disclosed county account at three widths."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

url = (Path(__file__).resolve().parents[1] / 'index.html').as_uri()
with sync_playwright() as playwright:
    args = {'headless': True}
    if os.environ.get('CHROMIUM_BIN'):
        args['executable_path'] = os.environ['CHROMIUM_BIN']
    browser = playwright.chromium.launch(**args)
    for width in (320, 390, 1440):
        page = browser.new_page(viewport={'width': width, 'height': 880},
                                is_mobile=width < 640, has_touch=width < 640)
        external = []
        errors = []
        page.on('request', lambda r: external.append(r.url) if r.url.startswith('http') else None)
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(url)
        details = page.locator('#county-account')
        assert details.is_hidden()
        names = page.evaluate('Object.keys(window.COUNTY_ACCOUNTS)')
        assert len(names) >= 10
        for county in names:
            page.select_option('#county', county)
            assert details.is_visible()
            assert not details.evaluate('e => e.open')
            assert details.bounding_box()['height'] < 64
            assert page.locator('#record-list article').count() > 0
            summary = details.locator('summary')
            summary.focus()
            page.keyboard.press('Enter')
            assert details.evaluate('e => e.open')
            links = details.locator('ol a').evaluate_all("ls => ls.map(a => [a.href, a.innerText])")
            assert len(links) >= 3 and len({u.split('#')[0] for u, _ in links}) == len(links)
            assert all(u.startswith('https://') and text and 'https://' not in text for u, text in links)
            assert details.locator('p').first.inner_text().strip()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.keyboard.press('Enter')
            assert not details.evaluate('e => e.open')
        page.select_option('#county', '')
        assert details.is_hidden()
        assert not external and not errors, (external, errors)
        print(f'PASS {width}px: {len(names)} county details compact by default, keyboard disclosure, numbered named sources; dated cards preserved.')
        page.close()
    browser.close()
