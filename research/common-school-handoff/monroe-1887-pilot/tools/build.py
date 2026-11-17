"""Rebuild a one-polygon pilot via a small planar affine model."""
import csv,json,math
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]/'data'
trace=json.loads((root/'native-trace.json').read_text())
towns=json.loads((root/'modern-reference-towns.geojson').read_text())
with (root/'control-points.csv').open() as f: rows=list(csv.DictReader(f))
x=np.array([[float(r['x']),float(r['y']),1] for r in rows])
ll=np.array([[float(r['lon']),float(r['lat'])] for r in rows])
center=np.array([-77.9,43.25]); scale=np.array([81152,111110])
y=(ll-center)*scale
fit=np.array([r['mode']=='fit' for r in rows]); assert sum(fit)==5 and sum(~fit)==3
coef=np.linalg.lstsq(x[fit],y[fit],rcond=None)[0]
res=np.linalg.norm(x@coef-y,axis=1)
err=dict(fit_rmse_m=math.sqrt(np.mean(res[fit]**2)),holdout_rmse_m=math.sqrt(np.mean(res[~fit]**2)),holdout_max_m=float(max(res[~fit])))
for r,z in zip(rows,res):r['residual_m']=round(float(z),1)
crop=np.array(trace['trace_native_crop_px'])
a=np.column_stack(((crop+trace['source_crop_origin_full_px'])/4-np.array(trace['gcp_frame_origin_quarter_px']),np.ones(len(crop))))
out=(a@coef/scale+center).round(6)
assert np.array_equal(out[0],out[-1]) and out.shape==(5,2)
# For a single polygon exterior, enforce the GeoJSON right-hand rule.
signed_area=np.sum(out[:-1,0]*out[1:,1]-out[1:,0]*out[:-1,1])/2
if signed_area<0:out=out[::-1]
geo={'type':'Feature','properties':{**{k:trace[k] for k in ('label_as_printed','source_date','county','town','source_item','source_raster','interpretation')},'model':'local affine in scaled degrees','registration_error_m':{k:round(v,1) for k,v in err.items()},'confidence':'visual trace on historical sheet; approximate registration; not a legal boundary'},'geometry':{'type':'Polygon','coordinates':[out.tolist()]}}
(root/'district4-1887.geojson').write_text(json.dumps(geo,indent=2,ensure_ascii=False)+'\n')
data={'district':geo,'trace':trace,'towns':towns,'controls':rows,'metrics':err}
(root/'bundle.js').write_text('window.MONROE1887 = '+json.dumps(data,separators=(',',':'))+';\n')
print({k:round(v,1) for k,v in err.items()})
