"""Bundle records and geometry as local JS for file:// and static HTTP use."""
import csv,json,re
from urllib.parse import urlparse
from pathlib import Path
from itertools import groupby
p=Path(__file__).resolve().parent.parent
d=p/'data'
geo=json.loads((d/'counties.geojson').read_text())
counties={f['properties']['name'] for f in geo['features']}
assert len(counties)==62 and all(f['properties']['fips'].startswith('36') for f in geo['features'])
with (d/'B0494_county_page_index.csv').open(newline='') as f:
    rows=list(csv.DictReader(f))
assert [int(x['pdf_page']) for x in rows]==list(range(1,117))
assert len([x for x in rows if x['duplicate_of_pdf_page']])==6
assert len({x['filed_county'] for x in rows if x['filed_county']})==29
assert all(r['filed_county'] in counties or not r['filed_county'] for r in rows)
records=json.loads((d/'context.json').read_text())
for (county,kind), group in groupby(rows[2:],lambda r:(r['filed_county'],r['scan_review_type'])):
    pages=list(group)
    start,end=pages[0]['pdf_page'],pages[-1]['pdf_page']
    locator=f'B0494, PDF p. {start}' if start==end else f'B0494, PDF pp. {start}–{end}'
    records.append({'id':'b0494-section-'+start,'title':kind,'kind':'Ledger section','county':county,
      'event_start':None,'event_end':None,'event_label':'Individual entry dates not yet indexed',
      'record_start':1860,'record_end':1954,'record_label':'ca. 1860–1954 (register catalog span, not page date)',
      'place_note':'State register filed under this county. Some districts cross county boundaries.',
      'summary':'Scan coverage only. The section heading is not an event count.',
      'source_url':pages[0]['scan_url'],'source_locator':locator,'review':'County indexed; entries not fully transcribed',
      'pages':[{'number':int(r['pdf_page']),'url':r['scan_url'],'duplicate_of':int(r['duplicate_of_pdf_page']) if r['duplicate_of_pdf_page'] else None,'note':r['notes'],'review':r['confidence']} for r in pages]})
with (d/'B0494_SELECTED_SCAN_VERIFIED_CASES.csv').open(newline='') as f:
  for r in csv.DictReader(f):
    stage=[(r[f'stage_date_{i}'],r[f'stage_type_{i}']) for i in range(1,4) if r[f'stage_date_{i}']]
    years=[int(date[:4]) for date,_ in stage if re.match(r'^(18|19)\d\d',date)]
    label='; '.join(f'{date} ({kind or "stage unverified"})' for date,kind in stage) or 'Event dates not established'
    locator=f"B0494, PDF p. {r['pdf_page']}"+(f", folio {r['printed_page']}" if r['printed_page'] else '')
    records.append({'id':r['event_id'].lower(),'title':f"{r['location']}: {r['action_type']}",'kind':'Ledger example','county':r['filed_county'],
      'event_start':min(years) if years else None,'event_end':max(years) if years else None,'event_label':label,
      'record_start':None,'record_end':None,'record_label':'Ledger entry; date of recording unverified',
      'place_note':'Filing county, not territory or venue.'+(' Also names: '+r['also_counties_as_explicit'] if r['also_counties_as_explicit'] else ''),
      'summary':r['scan_observation'],'source_url':r['scan_url'],'source_locator':locator,'review':r['confidence_scope'],
      'related_source_url':r.get('corroborating_source',''),'related_source_locator':r.get('corroboration_scope','')})
if (d/'sites.csv').exists():
  with (d/'sites.csv').open(newline='') as f:
    for x in csv.DictReader(f):
      for k in ('event_start','event_end','record_start','record_end'): x[k]=int(x[k]) if x[k] else None
      lon,lat=x.pop('longitude'),x.pop('latitude')
      x['site']=[float(lon),float(lat)] if lon and lat else None
      assert bool(lon)==bool(lat)
      assert x['precision'] in ('exact','approximate','unknown')
      assert bool(x['site'])==(x['precision']!='unknown')
      if x['site']: assert -80<=x['site'][0]<=-71 and 40<=x['site'][1]<=46
      x['event_label']=x['event_label'] or 'Event date not established'
      x['record_label']=x['record_label'] or 'Record date not established'
      x['place_note']={'exact':'Verified site coordinates','approximate':'Approximate site location; not an asserted building footprint or meeting venue','unknown':'Venue or exact site not established; county is archival context, not an asserted venue'}[x['precision']]
      if x.get('geometry_source_url'):
        u=urlparse(x['geometry_source_url'])
        assert u.scheme=='https' and u.netloc and not u.username
      if x['precision']=='approximate':
        assert x.get('uncertainty_note') and x.get('geometry_source_url')
      records.append(x)
ids=set()
for r in records:
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]*',r['id']) and r['id'] not in ids
    ids.add(r['id'])
    for key in ('source_url','related_source_url','geometry_source_url'):
        if not r.get(key): continue
        u=urlparse(r[key]); assert u.scheme=='https' and u.netloc and not u.username
    assert all(r.get(k) for k in ('title','source_locator','review','event_label'))
    assert r['county'] in counties or not r['county']
    for prefix in ('event','record'):
        a,b=(r[prefix+k] for k in ('_start','_end'))
        assert a is None or b is None or a<=b
    for page in r.get('pages',[]):
        assert page['url'].startswith('https://media.githubusercontent.com/')
bundle={'counties':geo,'records':records,'coverage':{'pdf_positions':116,'filed_counties':29,'front_matter':2,'retake_pairs':6,'first_county':'Broome','last_county':'Onondaga','last_folio':215}}
(d/'bundle.js').write_text('window.ATLAS_DATA = '+json.dumps(bundle,separators=(',',':'),ensure_ascii=True)+';\n')
print(len(records),'source entries;',sum(r['kind']=='Ledger section' for r in records),'ledger sections;',len(counties),'boundary features')
