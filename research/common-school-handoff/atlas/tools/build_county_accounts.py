"""Validate public county accounts and compile an offline-safe JS file."""
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

root = Path(__file__).resolve().parents[1]
data = root / 'data'
geo = json.loads((data / 'counties.geojson').read_text(encoding='utf-8'))
counties = {feature['properties']['name'] for feature in geo['features']}
accounts = json.loads((data / 'county-accounts.json').read_text(encoding='utf-8'))
assert isinstance(accounts, dict) and 0 < len(accounts) <= len(counties)
assert set(accounts) <= counties

def literal(value, limit):
    assert isinstance(value, str) and value.strip() == value and 0 < len(value) <= limit
    assert not any(unicodedata.category(ch).startswith('C') for ch in value)
    assert not re.search(r'https?://|<[^>]+>', value), 'Use named source links instead of raw URLs or markup.'

for county, account in accounts.items():
    assert set(account) == {'paragraphs', 'sources'}, county
    paragraphs, sources = account['paragraphs'], account['sources']
    assert isinstance(paragraphs, list) and 1 <= len(paragraphs) <= 4, county
    assert isinstance(sources, list) and 3 <= len(sources) <= 12, county
    for paragraph in paragraphs:
        literal(paragraph, 1500)
        assert all(1 <= int(n) <= len(sources) for n in re.findall(r'\[(\d+)\]', paragraph))
    documents = set()
    for source in sources:
        assert set(source) == {'title', 'url', 'locator'}
        literal(source['title'], 180)
        if source['locator']:
            literal(source['locator'], 300)
        url = source['url']
        parsed = urlsplit(url)
        assert parsed.scheme == 'https' and parsed.hostname and not (parsed.username or parsed.password)
        assert not any(ch.isspace() for ch in url) and len(url) <= 2000
        documents.add((parsed.hostname.lower(), parsed.path.rstrip('/'), parsed.query))
    assert len(documents) == len(sources), f'{county}: sources must point to distinct documents, not just separate fragments.'

result = 'window.COUNTY_ACCOUNTS = ' + json.dumps(accounts, ensure_ascii=True, separators=(',', ':'), sort_keys=True) + ';\n'
(data / 'county-accounts.js').write_text(result, encoding='utf-8')
print(f'{len(accounts)} county accounts; {sum(len(a["sources"]) for a in accounts.values())} named documentary sources')
