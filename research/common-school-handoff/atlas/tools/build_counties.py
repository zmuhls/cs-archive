"""Regenerate modern, reference-only NY counties from Census 2024 1:20m."""
import io,json,sys,zipfile
from pathlib import Path
import shapefile
root=Path(__file__).resolve().parent.parent
with zipfile.ZipFile(sys.argv[1]) as z:
  def open_ext(ext): return io.BytesIO(z.read(f'cb_2024_us_county_20m.{ext}'))
  source=shapefile.Reader(shp=open_ext('shp'), shx=open_ext('shx'),dbf=open_ext('dbf'),encoding='utf-8')
  output=[]
  for row in source.iterShapeRecords():
    p=row.record.as_dict()
    if p['STATEFP']!='36': continue
    output.append({'type':'Feature','id':p['GEOID'],'properties':{'name':p['NAME'],'fips':p['GEOID']},'geometry':row.shape.__geo_interface__})
  assert len(output)==62
  output.sort(key=lambda f:f['properties']['name'])
  (root/'data/counties.geojson').write_text(json.dumps({'type':'FeatureCollection','features':output},separators=(',',':'))+'\n')
