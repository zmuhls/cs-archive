"""Verify exact Delaware locator is legible and all compound locators remain preserved."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

base = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    opts = {'executable_path': os.environ['CHROMIUM_BIN']} if os.environ.get('CHROMIUM_BIN') else {}
    browser = p.chromium.launch(**opts)
    for width in (320, 390, 1440):
        page = browser.new_page(viewport={'width':width,'height':850},
                                has_touch=width<500, is_mobile=width<500)
        page.goto((base/'index.html').as_uri()+'#county=Delaware&q=Gregorytown')
        r = page.locator('#record-delaware-gregorytown4')
        assert r.is_visible()
        assert 'https://' not in r.inner_text()
        assert r.get_by_role('link',name='District 4 historical society PDF').get_attribute('href').endswith('/7-gregorytown-school-no.-4.pdf')
        r.get_by_text('Additional sources').click()
        sources = dict(r.locator('.source-notes a').evaluate_all('links => links.map(a => [a.textContent, a.href])'))
        assert sources['1869 Beers-derived map'].endswith('/schcolchestermapbeers1.jpg')
        assert sources['1900s map'].endswith('/MapColchester1900s.jpg')
        assert sources['B0494 p.44'].endswith('#page=44')
        assert 'returnGeometry=true' in sources['NYS Streets · Fuller Hill and River Road centerline node']
        assert 'https://' not in r.inner_text()
        assert r.get_by_text('Original locator').count() == 0
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        for county, query, ids in [('Delaware','Davenport District 14','delaware-davenport14'),('Columbia','Kinderhook District 6','columbia-kinderhook6')]:
            page.goto((base/'index.html').as_uri()+f'#county={county}&q={query.replace(" ","+")}')
            page.reload()
            other=page.locator('#record-'+ids)
            assert other.is_visible()
            assert 'https://' not in other.inner_text()
            other.get_by_text('Additional sources').click()
            assert other.locator('.source-notes a').count() >= 2
            assert 'https://' not in other.inner_text()
        page.close()
        print(f'PASS {width}px: exact Gregorytown and two other compound citations; all URLs retained without a visible URL wall.')
