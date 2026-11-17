import os
from pathlib import Path
from playwright.sync_api import sync_playwright
url=(Path(__file__).resolve().parents[1]/'index.html').as_uri()
with sync_playwright() as p:
 options={'headless':True}
 if os.environ.get('CHROMIUM_BIN'):options['executable_path']=os.environ['CHROMIUM_BIN']
 b=p.chromium.launch(**options)
 for width in (1440,390):
  w=b.new_page(viewport={'width':width,'height':885})
  external=[];errors=[]
  w.on('request',lambda r:external.append(r.url) if r.url.startswith(('https:','http:')) else None)
  w.on('pageerror',lambda e:errors.append(e))
  w.goto(url)
  assert w.locator('.leaflet-overlay-pane path').count()==3
  assert w.locator('.leaflet-marker-icon').count()==8 and w.locator('.marker.check').count()==3
  assert w.locator('#controls-table tr').count()==8
  assert '164.4 m' in w.locator('#metrics').inner_text()
  assert w.locator('.crop img').evaluate('i=>i.complete && i.naturalWidth===1400')
  assert w.evaluate('document.documentElement.scrollWidth===window.innerWidth')
  m=w.locator('.marker.check').first
  m.focus();w.keyboard.press('Enter')
  assert 'residual' in w.locator('.leaflet-popup-content').inner_text()
  w.uncheck('#show-controls'); assert w.locator('.leaflet-marker-icon').count()==0
  w.uncheck('#show-trace'); assert not w.locator('.crop svg').is_visible()
  assert not external and not errors,(external,errors)
  if width==1440 and os.environ.get('PILOT_SCREENSHOT'):w.screenshot(path=os.environ['PILOT_SCREENSHOT'])
  print('PASS',width,'source crop, one district and two modern references, five fit/three check points, keyboard, toggles, metrics, no external startup')
