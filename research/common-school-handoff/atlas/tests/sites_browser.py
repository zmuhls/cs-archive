"""Verify that three approximate markers expose provenance offline."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
  kwargs={'executable_path':os.environ['CHROMIUM_BIN']} if os.environ.get('CHROMIUM_BIN') else {}
  browser=p.chromium.launch(**kwargs)
  for size in [{'width':1440,'height':900},{'width':390,'height':844}]:
    page=browser.new_page(viewport=size, has_touch=size['width']<500, is_mobile=size['width']<500)
    requests=[];errors=[]
    page.on('request',lambda req:requests.append(req.url) if req.url.startswith(('http:', 'https:')) else None)
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto((root/'index.html').as_uri())
    assert page.locator('.site-marker').all_inner_texts()==['S','S','S']
    page.select_option('#county','Columbia')
    marker=page.locator('.site-marker')
    assert marker.count()==1 and marker.get_attribute('tabindex')=='0'
    assert 'Approximate location' in marker.get_attribute('aria-label')
    marker.focus(); page.keyboard.press('Enter')
    popup=page.locator('.leaflet-popup-content')
    assert popup.is_visible() and 'not the building footprint' in popup.inner_text().lower()
    assert popup.get_by_role('link',name='NYS ITS Streets',exact=False).get_attribute('href').startswith('https://nysgeohub.ny.gov/')
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), page.evaluate('[document.documentElement.scrollWidth, window.innerWidth]')
    assert requests==[] and errors==[]
  print('PASS: three approximate markers; keyboard-accessible source popup; offline desktop and mobile.')
