'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const data = window.ATLAS_DATA;
  const details = {
    all: [null,null,'Browse source records and scan sections by county. Date filters use dates of events, not the register’s catalog span.'],
    common: [1812,1852,'Local reports and minutes document how common-school districts recorded teaching, money and attendance.'],
    union: [1853,1910,'The Union Free School Act authorized a different district form. Explore dated evidence before the Capitol fire.'],
    fire: [1911,1924,'The 1911 fire and reconstruction are a documented recordkeeping break, distinct from the centralization laws that followed.'],
    aid: [1925,1946,'New state aid expanded centralization. The surviving record still distinguishes state orders from local organization and consent.'],
    plan: [1947,1954,'The 1947 Master Plan and late entries in the accessible register extract.'],
    unknown: [null,null,'Browse materials without indexed event-year bounds. An undated section is not assigned the register’s full catalog span.']
  };
  const filters = {period:'all', county:'', search:'', kind:'', points:true};
  let pageSize = 18, map, counties, pointLayer;
  const mapStatus = () => { $('map-failure').hidden = false; $('reset-map').hidden = true; };
  const e = (type, text, cls) => {
    const node = document.createElement(type);
    if (text != null) node.textContent = text;
    if (cls) node.className = cls;
    return node;
  };
  const link = (s,text) => {
    const anchor = e('a',text);
    try {
      const u = new URL(s);
      if (u.protocol === 'https:' && !u.username && !u.password) {
        anchor.href = u.href; anchor.target = '_blank'; anchor.rel = 'noopener noreferrer';
      }
    } catch { /* invalid input remains plain text */ }
    return anchor;
  };
  if (!data || !Array.isArray(data.records)) {
    mapStatus();
    $('results-count').textContent='Record data unavailable. Download the page index below.';
    return;
  }
  const names = new Set(data.counties.features.map(f=>f.properties.name));
  const types = new Set(data.records.map(r=>r.kind).sort());
  const hasSites = data.records.some(r=>r.site);
  const pageCoverage = Object.groupBy ? Object.groupBy(data.records.filter(r=>r.kind==='Ledger section'),r=>r.county) : data.records.filter(r=>r.kind==='Ledger section').reduce((a,r)=>((a[r.county]??=[]).push(r),a),{});
  function option(select,value,label=value) {
    const o=e('option',label);o.value=value;select.append(o);
  }
  option($('county'),'~statewide','Statewide only');
  Array.from(names).sort((a,b)=>a.localeCompare(b)).forEach(name=>option($('county'),name,name+' County'));
  types.forEach(name=>option($('kind'),name));
  $('points-control').hidden=!hasSites;

  function recordsInView({ignoreCounty=false}={}) {
    const q=filters.search.toLowerCase().trim().split(/\s+/).filter(Boolean);
    const [start,end]=details[filters.period];
    return data.records.filter(r=>{
      if (!ignoreCounty && filters.county && (filters.county==='~statewide' ? r.county : r.county!==filters.county)) return false;
      if (filters.kind && r.kind!==filters.kind) return false;
      const known=r.event_start!=null||r.event_end!=null;
      if (filters.period==='unknown'&&known) return false;
      if (start!=null && (!known || (r.event_start??-Infinity)>end || (r.event_end??Infinity)<start)) return false;
      const hits=[r.title,r.county,r.kind,r.summary,r.event_label,r.record_label,r.source_locator,r.place_note].join(' ').toLowerCase();
      return q.every(term=>hits.includes(term));
    });
  }

  function card(r) {
    const article=e('article',null,'record');article.id='record-'+r.id;
    article.append(e('h3',r.title));
    article.append(e('p',[(r.county?r.county+' County':'Statewide'),r.kind].join(' · '),'record-meta'));
    if(r.event_start!=null||r.event_end!=null)article.append(e('p',r.event_label,'record-date'));
    article.append(e('p',r.summary));
    const caption=e('p',null,'record-source');caption.append(e('strong','Source: '),link(r.source_url,r.source_locator));article.append(caption);
    const disclosure = e('details');
    disclosure.append(e('summary',r.pages?'Scan pages and provenance':'Dates, place and provenance'));
    const list=e('dl');
    for (const [label,value] of [['Event date',r.event_label],['Record date or scope',r.record_label],['Place evidence',r.place_note],['Review status',r.review],...(r.precision?[['Location precision',r.precision+(r.uncertainty_note?' · '+r.uncertainty_note:'')]]:[])]) {
      list.append(e('dt',label),e('dd',value||'Not established'));
    }
    disclosure.append(list);
    if(r.geometry_source_url){
      const evidence=e('p');evidence.append(link(r.geometry_source_url,r.geometry_source_locator||'Coordinate reference'));disclosure.append(evidence);
    }
    if(r.related_source_url){
      const corroboration=e('p');corroboration.append(link(r.related_source_url,r.related_source_locator||'Corroborating source'));disclosure.append(corroboration);
    }
    if(r.pages) {
      const ul=e('ul');
      for(const p of r.pages){
        const li=e('li');li.append(link(p.url,'PDF p. '+p.number));
        if(p.duplicate_of)li.append(e('span',' · Retake of p. '+p.duplicate_of,'retake'));
        if(p.note)li.append(e('span',' · '+p.note));
        li.append(e('span',' · '+p.review));
        ul.append(li);
      }
      disclosure.append(ul);
    }
    article.append(disclosure);
    return article;
  }

  function updateMap() {
    if(!map)return;
    const active=recordsInView({ignoreCounty:true});
    const counts=new Map();
    for (const r of active) if(r.county)counts.set(r.county,(counts.get(r.county)||0)+1);
    counties.eachLayer(layer=>{
      const name=layer.feature.properties.name;
      const selected=filters.county===name;
      const color=counts.get(name)?'#557044':pageCoverage[name]?'#c3ac72':'#dce0ce';
      layer.setStyle({color:selected?'#652e13':'#fff9df',weight:selected?2.5:1.2,fillColor:color,fillOpacity:selected?1:.8});
      if(selected)layer.bringToFront();
    });
    pointLayer.clearLayers();
    $('site-key').hidden=!filters.points || !recordsInView().some(r=>r.site);
    if(filters.points){
      const clusters=new Map();
      for(const r of recordsInView().filter(x=>x.site)){
        const key=r.site.join(',');
        if(!clusters.has(key))clusters.set(key,[]);
        clusters.get(key).push(r);
      }
      for(const group of clusters.values()){
        group.sort((a,b)=>(a.event_start??Infinity)-(b.event_start??Infinity)||a.title.localeCompare(b.title));
        const first=group[0];
        const approx=group.some(r=>r.precision==='approximate');
        const roles=new Set(group.map(r=>r.kind));
        const role=roles.size>1?'mixed':first.kind==='Meeting site'?'meeting':'school';
        const code={mixed:'X',meeting:'M',school:'S'}[role]+(group.length>1?group.length:'');
        const badge=e('span',code,'site-symbol');
        badge.setAttribute('aria-hidden','true');
        const icon=L.divIcon({className:'site-marker site-'+role+' '+(approx?'site-approximate':'site-exact'),html:badge,iconSize:[31,31],iconAnchor:[15,15],popupAnchor:[0,-14]});
        const label=(approx?'Approximate location: ':'Verified site: ')+(group.length>1?group.length+' records at the same proxy; ':'')+group.map(r=>r.title).join('; ');
        const marker=L.marker([first.site[1],first.site[0]],{icon,keyboard:true,title:label,alt:label});
        const popup=e('div',null,'site-popup');
        if(group.length>1)popup.append(e('p',group.length+' events share this proxy. Each is recorded separately.','site-group-note'));
        for(const r of group){
          const entry=e('section');
          entry.append(e('strong',r.title),e('p',(r.precision==='approximate'?'Approximate location':'Verified site')+' · '+r.kind),e('p',r.event_label),e('p',r.summary),e('p',r.uncertainty_note||r.place_note),link(r.source_url,r.source_locator));
          if(r.geometry_source_url){const p=e('p');p.append(link(r.geometry_source_url,r.geometry_source_locator||'Coordinate reference'));entry.append(p);}
          if(r.related_source_url){const p=e('p');p.append(link(r.related_source_url,r.related_source_locator||'Corroborating source'));entry.append(p);}
          popup.append(entry);
        }
        marker.bindPopup(popup,{maxHeight:300,maxWidth:330}).addTo(pointLayer);
        marker.getElement()?.setAttribute('aria-label',label);
      }
    }
  }

  function focusRecords(){
    const title=$('record-title');
    title.focus({preventScroll:true});
    title.scrollIntoView({block:'start',behavior:'instant'});
  }
  function setCounty(name,{focus=false}={}){
    filters.county=name;
    pageSize=18;
    render();
    if(focus)focusRecords();
  }
  function renderCountyHeading(){
    const name=filters.county;
    const scope=$('county-scope');
    const jump=$('selected-county-link');
    $('record-title').textContent=name==='~statewide'?'Statewide records':name?name+' County':'Records';
    jump.hidden=!name;
    if(name)jump.textContent='Read '+(name==='~statewide'?'statewide':name+' County')+' records';
    scope.hidden=!name;
    $('county-actions').hidden=!name;
    if(!name)return;
    if(name==='~statewide'){
      scope.textContent='Statewide context is not evidence for any individual county or district.';
      return;
    }
    const indexed=(pageCoverage[name]||[]).length;
    const parts=indexed
      ? [indexed+' grouped B0494 scan '+(indexed===1?'entry':'entries')+' indexed for this county.']
      : ['No B0494 section is indexed for this county in the available scan. That does not mean no records survive.'];
    parts.push('Dated records are ordered by event date. Undated items, including scan sections without event dates, follow.');
    scope.textContent=parts.join(' ');
  }
  function mapInit(){
    if(!window.L){mapStatus();return;}
    try {
      map=L.map('map',{scrollWheelZoom:false,zoomSnap:.1,minZoom:4,maxZoom:13,attributionControl:true});
      map.attributionControl.setPrefix(false).addAttribution('2024 <a href="https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html">U.S. Census Bureau</a> reference boundaries');
      counties=L.geoJSON(data.counties,{style:{color:'#fff9df',weight:1.2,fillColor:'#dce0ce',fillOpacity:.8},
        onEachFeature:(feature,layer)=>{
          const name=feature.properties.name;
          const tooltip=e('span',name+' County');
          layer.bindTooltip(tooltip,{sticky:true,className:'atlas-tooltip'});
          layer.on('click',()=>setCounty(name,{focus:true}));
          layer.on('add',()=>{
            const path=layer.getElement();
            if(!path)return;
            path.setAttribute('tabindex','-1');
            path.setAttribute('aria-label',name+' County');
          });
        }
      }).addTo(map);
      pointLayer=L.layerGroup().addTo(map);
      const fit=()=>map.fitBounds(counties.getBounds(),{paddingTopLeft:[20,20],paddingBottomRight:[20,40],animate:false,maxZoom:8});
      fit();
      $('reset-map').addEventListener('click',fit);
    } catch(err){
      if(map)map.remove();
      map=null;mapStatus();
      console.warn('Map initialization failed; source list remains available',err);
    }
  }

  function readState(){
    const params=new URLSearchParams(location.hash.slice(1));
    const p=params.get('period'), c=params.get('county'), k=params.get('kind');
    if(p&&Object.hasOwn(details,p))filters.period=p;
    if(c&&(names.has(c)||c==='~statewide'))filters.county=c;
    if(k&&types.has(k))filters.kind=k;
    filters.search=(params.get('q')||'').slice(0,150);
    filters.points=params.get('sites')!=='0';
  }
  function writeState(){
    const p=new URLSearchParams();
    if(filters.period!=='all')p.set('period',filters.period);
    if(filters.county)p.set('county',filters.county);
    if(filters.kind)p.set('kind',filters.kind);
    if(filters.search)p.set('q',filters.search);
    if(!filters.points)p.set('sites','0');
    try{
      const hash=p.size?'#'+p:'';
      history.replaceState(null,'',location.pathname+location.search+hash);
    }catch{ /* file origins can restrict history; nothing depends on it */ }
  }
  function render(focusNew=false){
    renderCountyHeading();
    const matches=recordsInView();
    if(filters.county)matches.sort((a,b)=>(a.event_start??a.event_end??Infinity)-(b.event_start??b.event_end??Infinity)
      ||Number(b.kind==='Ledger section')-Number(a.kind==='Ledger section')
      ||(a.kind==='Ledger section'&&b.kind==='Ledger section'?((a.pages?.[0]?.number??Infinity)-(b.pages?.[0]?.number??Infinity)):0)
      ||a.title.localeCompare(b.title));
    const current=$('record-list');
    const frag=document.createDocumentFragment();
    const oldLimit=pageSize-18;
    matches.slice(0,pageSize).forEach((r,index)=>{
      const entry=card(r);
      if(focusNew&&index===oldLimit)entry.tabIndex=-1;
      frag.append(entry);
    });
    if(!matches.length)frag.append(e('p','No indexed records match. Try clearing filters or browsing undated sections. This is not evidence of absence.','no-results'));
    if(matches.length>pageSize){
      const b=e('button','Show '+Math.min(18,matches.length-pageSize)+' more records','more-button');b.type='button';
      b.addEventListener('click',()=>{pageSize+=18;render(true);});frag.append(b);
    }
    current.replaceChildren(frag);
    if(focusNew)current.querySelector('[tabindex="-1"]')?.focus();
    const mapped=matches.filter(r=>r.county).length;
    $('results-count').textContent=matches.length+' '+(matches.length===1?'record':'records')+' · '+mapped+' county-linked · '+(matches.length-mapped)+' statewide';
    $('period-detail').textContent=details[filters.period][2];
    if($('search')!==document.activeElement)$('search').value=filters.search;
    $('county').value=filters.county;
    $('kind').value=filters.kind;
    $('points').checked=filters.points;
    for(const b of $('periods').querySelectorAll('button'))b.setAttribute('aria-pressed',String(b.dataset.key===filters.period));
    updateMap();writeState();
  }
  $('periods').addEventListener('click',ev=>{
    const button=ev.target.closest('button');
    if(!button)return;
    filters.period=button.dataset.key;pageSize=18;render();
  });
  for(const nav of [$('selected-county-link'),document.querySelector('.skip')]){
    nav.addEventListener('click',ev=>{ev.preventDefault();focusRecords();});
  }
  $('county').addEventListener('change',ev=>setCounty(ev.target.value));
  $('show-all-counties').addEventListener('click',()=>setCounty('',{focus:true}));
  $('back-to-map').addEventListener('click',ev=>{
    ev.preventDefault();
    if(!map){$('county').focus();return;}
    const frame=$('map');
    frame.focus({preventScroll:true});
    frame.scrollIntoView({block:'start',behavior:'instant'});
  });
  $('kind').addEventListener('change',ev=>{filters.kind=ev.target.value;pageSize=18;render();});
  $('search').addEventListener('input',ev=>{filters.search=ev.target.value.slice(0,150);pageSize=18;render();});
  $('points').addEventListener('change',ev=>{filters.points=ev.target.checked;updateMap();writeState();});
  $('clear').addEventListener('click',()=>{
    Object.assign(filters,{period:'all',county:'',search:'',kind:'',points:true});pageSize=18;render();
  });
  readState();mapInit();render();
})();
