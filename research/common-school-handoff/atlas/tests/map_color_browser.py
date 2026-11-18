"""County appearance encodes selection only; sites keep a redundant shape cue."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

def lum(h):
    rgb = [int(h[i:i+2], 16)/255 for i in (1,3,5)]
    vals = [x/12.92 if x <= .04045 else ((x+.055)/1.055)**2.4 for x in rgb]
    return sum(x*y for x,y in zip(vals,(.2126,.7152,.0722)))

for a,b in [('#66645b','#efeee9'),('#66645b','#d9e6eb'),('#17447d','#cfdef2'),
            ('#17447d','#efeee9'),('#423719','#ffecb5'),('#29271e','#ffecb5')]:
    l = sorted([lum(a),lum(b)])
    ratio=(l[1]+.05)/(l[0]+.05)
    assert ratio>=(4.5 if a=='#29271e' else 3)
    print(f'Contrast {a} against {b}: {ratio:.2f}:1')

with sync_playwright() as p:
    opts={'executable_path': os.environ['CHROMIUM_BIN']} if os.environ.get('CHROMIUM_BIN') else {}
    b=p.chromium.launch(**opts)
    for w in (320,390,1440):
        page=b.new_page(viewport={'width':w,'height':850},is_mobile=w<500,has_touch=w<500)
        page.goto((Path(__file__).resolve().parents[1]/'index.html').as_uri())
        layers=page.locator('.leaflet-overlay-pane path')
        assert layers.count()==62
        assert set(layers.evaluate_all('els=>els.map(e=>e.getAttribute("fill"))'))=={'#efeee9'}
        marker=page.locator('.site-approximate').first
        assert marker.evaluate('e=>[getComputedStyle(e).borderRadius,getComputedStyle(e).borderStyle]')==['4px','dashed']
        assert 'Approximate' in marker.get_attribute('aria-label')
        page.select_option('#county','Delaware')
        sel=page.locator('path[aria-label="Delaware County"]')
        assert sel.get_attribute('stroke')=='#17447d' and sel.get_attribute('stroke-width')=='3.5'
        assert page.locator('path[fill="#cfdef2"]').count()==1
        page.locator('[data-key="aid"]').click()
        assert page.locator('path[fill="#cfdef2"]').count()==1
        page.get_by_text('Map key & scope',exact=True).click()
        assert page.locator('.map-legend').inner_text().splitlines()==['County','Selected county']
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        print(f'PASS {w}px: neutral counties; selection retained through period filter; dashed approximate marker and legend.')
        page.close()
