"""Run with Playwright Python; CHROMIUM_BIN overrides its Chromium engine."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
url=(root/'index.html').as_uri()
with sync_playwright() as p:
    kwargs={'headless':True}
    if os.environ.get('CHROMIUM_BIN'): kwargs['executable_path']=os.environ['CHROMIUM_BIN']
    b=p.chromium.launch(**kwargs)
    desktop=b.new_page(viewport={'width':1440,'height':900})
    errors,external=[],[]
    desktop.on('pageerror', lambda e: errors.append(str(e)))
    desktop.on('request',lambda r:external.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
    desktop.goto(url)
    assert desktop.locator('.leaflet-overlay-pane path').count()==62
    assert desktop.locator('#county option').count()==64
    assert desktop.locator('#results-count').inner_text().endswith(" records")
    desktop.keyboard.press('Tab')
    assert desktop.locator('.skip').evaluate('e=>e===document.activeElement')
    total = int(desktop.locator('#results-count').inner_text().split()[0])
    desktop.get_by_role('button',name=f'Show {min(18,total-18)} more records').click()
    assert desktop.locator('#record-list article').count()==min(36,total)
    assert desktop.locator('#record-list article[tabindex="-1"]').evaluate('e=>e===document.activeElement')
    desktop.select_option('#county','Delaware')
    assert desktop.locator('path[aria-label="Delaware County"]').get_attribute('stroke')=='#652e13'
    desktop.locator('[data-key="common"]').click()
    assert desktop.locator('#record-list article').count()==1
    assert 'tax' in desktop.locator('#record-list article').inner_text()
    assert '1833' in desktop.locator('#record-list article').inner_text()
    desktop.locator('[data-key="aid"]').click()
    assert 'Stamford' in desktop.locator('#record-list').inner_text()
    desktop.get_by_role('button',name='Clear filters').click()
    desktop.locator('[data-key="union"]').click()
    desktop.select_option('#county','Cayuga')
    assert 'Moravia' in desktop.locator('#record-list').inner_text()
    assert 'Historical Sketches' in desktop.locator('#record-list').inner_text()
    assert '1868' in desktop.locator('#record-list').inner_text()
    desktop.get_by_role('button',name='Clear filters').click()
    desktop.locator('[data-key="unknown"]').click()
    desktop.select_option('#county','Essex')
    desktop.select_option('#kind','Ledger section')
    desktop.locator('#record-b0494-section-54 summary').click()
    assert 'Retake of p. 54' in desktop.locator('#record-list').inner_text()
    href=desktop.locator('#record-b0494-section-54 details a').first.get_attribute('href')
    assert href.startswith('https://') and href.endswith('#page=54')
    desktop.get_by_role('button',name='Clear filters').click()
    desktop.fill('#search','"><img src=x onerror=alert(1)>')
    assert desktop.locator('#record-list img').count()==0
    assert "No records match the selected filters." in desktop.locator('#record-list').inner_text()
    # County click is deliberately redundant with keyboard-accessible select.
    desktop.fill('#search','')
    desktop.locator('path[aria-label="Cayuga County"]').evaluate("(e)=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    assert desktop.locator('#county').input_value()=='Cayuga'
    desktop.select_option('#kind','Meeting minutes')
    assert all('Meeting minutes' in x for x in desktop.locator('.record-meta').all_inner_texts())
    desktop.goto(url+'#period=aid&county=Suffolk')
    desktop.reload()
    assert 'transportation contract' in desktop.locator('#record-list').inner_text()
    desktop.get_by_role('button',name='Clear filters').click()
    if (shots:=os.environ.get('ATLAS_SCREENSHOTS')): desktop.screenshot(path=str(Path(shots)/'atlas-desktop.png'))
    assert external==[] and errors==[],(external,errors)
    mobile=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    mobile.goto(url)
    assert mobile.locator('#record-list article').count()==18
    assert mobile.evaluate('document.documentElement.scrollWidth === window.innerWidth')
    mobile.select_option('#county','Broome')
    assert 'County account forthcoming.' in mobile.locator('#record-list').inner_text()
    mobile.select_option('#kind','Ledger section')
    assert 'Broome County' in mobile.locator('#record-list').inner_text()
    if shots: mobile.screenshot(path=str(Path(shots)/'atlas-mobile.png'))
    # Simulate failure of vendored JS by using a separate copy without its script.
    import shutil,tempfile
    with tempfile.TemporaryDirectory() as t:
        copy=Path(t)/'atlas'
        shutil.copytree(root,copy,ignore=shutil.ignore_patterns('__pycache__'))
        (copy/'vendor/leaflet/leaflet.js').unlink()
        mobile.goto((copy/'index.html').as_uri())
        assert mobile.locator('#map-failure').is_visible()
        mobile.select_option('#county','Delaware')
        assert 'Delaware County' in mobile.locator('#record-list').inner_text()
    print("PASS: local file, no external requests, 62 map paths, county/click/period/search, URL state, keyboard skip, disclosure, pagination, mobile width, map-failure fallback.")
