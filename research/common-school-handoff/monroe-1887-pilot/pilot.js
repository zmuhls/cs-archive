'use strict';
(() => {
  const m=window.MONROE1887;
  const $=id=>document.getElementById(id);
  const elem=(tag,txt)=>{const el=document.createElement(tag);el.textContent=txt;return el;};
  if(!m) return;
  $('show-trace').addEventListener('change',e=>{document.querySelector('.crop svg').style.visibility=e.target.checked?'visible':'hidden';});
  $('metrics').textContent='Fit RMS: '+m.metrics.fit_rmse_m.toFixed(1)+' m. Withheld check RMS: '+m.metrics.holdout_rmse_m.toFixed(1)+' m; largest check: '+m.metrics.holdout_max_m.toFixed(1)+' m.';
  for(const r of m.controls){
    let tr=document.createElement('tr');
    tr.append(elem('td',r.feature),elem('td',r.mode==='fit'?'Fit':'Check'),elem('td',r.residual_m+' m'));
    $('controls-table').append(tr);
  }
  if(!window.L){$('map-off').hidden=false;return;}
  try{
    const map=L.map('map',{scrollWheelZoom:false,zoomSnap:.1});
    map.attributionControl.setPrefix(false).addAttribution('1887: Library of Congress · 2024 town reference: U.S. Census Bureau');
    L.geoJSON(m.towns,{style:{color:'#727f70',weight:1,dashArray:'3 6',fillOpacity:0}}).addTo(map);
    const trace=L.geoJSON(m.district,{style:{color:'#854911',weight:3,dashArray:'8 5',fillColor:'#e4b54c',fillOpacity:.45}}).addTo(map);
    trace.bindTooltip(elem('span',m.district.properties.label_as_printed+' · 1887'),{permanent:true,direction:'center'});
    const controls=L.layerGroup().addTo(map);
    for(const r of m.controls){
      const lbl=r.mode==='fit'?'F':'C';
      const icon=L.divIcon({className:'marker '+(r.mode==='fit'?'fit':'check'),html:elem('span',lbl),iconSize:[22,22],iconAnchor:[11,11]});
      const mark=L.marker([Number(r.lat),Number(r.lon)],{icon,title:r.feature,keyboard:true}).addTo(controls);
      mark.getElement()?.setAttribute('aria-label',r.feature+'; '+(r.mode==='fit'?'fit':'independent check')+'; residual '+r.residual_m+' meters');
      mark.bindPopup(elem('span',r.feature+' · '+r.residual_m+' m residual'));
    }
    map.fitBounds(L.featureGroup([...trace.getLayers(),...controls.getLayers()]).getBounds(),{padding:[18,24],animate:false});
    $('show-controls').addEventListener('change',e=>e.target.checked?controls.addTo(map):controls.remove());
  }catch(error){$('map-off').hidden=false;console.warn('Map unavailable',error);}
})();
