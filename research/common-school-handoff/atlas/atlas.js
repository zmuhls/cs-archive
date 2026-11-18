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
  const archiveKinds = new Set(['Archive guide','Archival collection','Ledger section']);
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
      if(archiveKinds.has(r.kind)&&r.kind!==filters.kind)return false;
      if (!ignoreCounty && filters.county && (filters.county==='~statewide' ? r.county : r.county!==filters.county)) return false;
      if (filters.kind && r.kind!==filters.kind) return false;
      const known=r.event_start!=null||r.event_end!=null;
      if (filters.period==='unknown'&&known) return false;
      if (start!=null && (!known || (r.event_start??-Infinity)>end || (r.event_end??Infinity)<start)) return false;
      const hits=[r.title,r.county,r.kind,r.summary,r.event_label,r.record_label,r.source_locator,r.place_note].join(' ').toLowerCase();
      return q.every(term=>hits.includes(term));
    });
  }

  // The vetted site CSV retains full compound locators. Render its references
  // separately so long map-service queries stay in href, not in the text.
  function sources(r) {
    const parts=(r.source_locator||'').split(/;\s*/);
    const compound=parts.some(part=>/https?:\/\//i.test(part));
    const supplemental=new Map();
    const add=(url,label)=>{
      if(url&&url!==r.source_url)supplemental.set(url,label);
    };
    if(compound){
      for(const part of parts.slice(1)){
        const match=part.match(/^(.*?)\s*(https:\/\/\S+)$/i);
        if(match) {
          const url=match[2];
          if(url!==r.geometry_source_url && url!==r.related_source_url)
            add(url,match[1].replace(/[ ,]+$/,'')||'Supplementary reference');
        } else {
          const folio=part.match(/^B0494(?: PDF)? p\.\s*(\d+)/i);
          if(folio) {
            const archive=data.records.find(record=>record.id==='b0494-guide');
            if(archive?.source_url)add(archive.source_url.split('#')[0]+'#page='+folio[1],part);
          }
        }
      }
    }
    add(r.geometry_source_url,r.geometry_source_locator||'Coordinate reference');
    add(r.related_source_url,r.related_source_locator||'Corroborating source');
    return {label:compound?parts[0]:r.source_locator,supplemental};
  }
  function sourceList(evidence){
    const list=e('ul',null,'source-notes');
    for(const [url,label] of evidence.supplemental){
      const item=e('li');
      item.append(link(url,label));
      list.append(item);
    }
    return list;
  }
  function publicSummary(r){
    // Preserve the source bundle. Omit scan-production/editorial aside text
    // rather than substituting an account where none has been written.
    const omit={
      'onondaga-1954':' It is a consolidation continuation despite the generated OCR category.',
      'che-01':'; p22 repeat exposure of p21',
      'b0494-038-a':'; additional letter annotation not fully legible',
      'b0494-101-a':' Same physical register page is imaged again at PDF p. 104; not a distinct event.',
      'b0494-116-a':' Keep both constituent references under one candidate administrative action.'
    };
    return omit[r.id]?r.summary.replace(omit[r.id],''):r.summary;
  }
  function card(r) {
    const article=e('article',null,'record');article.id='record-'+r.id;
    article.append(e('h3',r.title));
    article.append(e('p',[(r.county?r.county+' County':'Statewide'),r.kind].join(' · '),'record-meta'));
    if(r.event_start!=null||r.event_end!=null)article.append(e('p',r.event_label,'record-date'));
    if(!archiveKinds.has(r.kind))article.append(e('p',publicSummary(r)));
    const citations=sources(r);
    const caption=e('p',null,'record-source');caption.append(e('strong','Source: '),link(r.source_url,citations.label));article.append(caption);
    if(citations.supplemental.size){
      const disclosure=e('details');
      disclosure.append(e('summary','Additional sources'),sourceList(citations));
      article.append(disclosure);
    }
    if(r.pages && (r.pages.length>1||r.pages.some(page=>page.duplicate_of))){
      const disclosure=e('details');
      const pages=e('ul');
      disclosure.append(e('summary','Scan pages'),pages);
      for(const page of r.pages){
        const item=e('li');
        item.append(link(page.url,'PDF p. '+page.number));
        if(page.duplicate_of)item.append(e('span',' · Retake of p. '+page.duplicate_of,'retake'));
        pages.append(item);
      }
      article.append(disclosure);
    }
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
          const citations=sources(r);
          entry.append(e('strong',r.title),e('p',(r.precision==='approximate'?'Approximate location':'Verified site')+' · '+r.kind),e('p',r.event_label),e('p',publicSummary(r)),link(r.source_url,citations.label));
          if(citations.supplemental.size){
            const extra=e('details');
            extra.append(e('summary','Additional sources'),sourceList(citations));
            entry.append(extra);
          }
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
    const jump=$('selected-county-link');
    $('record-title').textContent=name==='~statewide'?'Statewide records':name?name+' County':'Records';
    jump.hidden=!name;
    if(name)jump.textContent='Read '+(name==='~statewide'?'statewide':name+' County')+' records';
    $('county-actions').hidden=!name;
  }
  let accountCounty = null;
  function renderCountyAccount() {
    const county = filters.county;
    if (county === accountCounty) return;
    accountCounty = county;
    const panel = $('county-account');
    const body = $('county-account-body');
    const accounts = window.COUNTY_ACCOUNTS;
    const account = accounts && Object.hasOwn(accounts, county) ? accounts[county] : null;
    panel.open = false;
    panel.hidden = !account;
    body.replaceChildren();
    if (!account) return;
    panel.querySelector('summary').setAttribute('aria-label', county + ' County account');
    for (const paragraph of account.paragraphs) {
      const p = e('p');
      for (const chunk of paragraph.split(/(\[\d+\])/)) {
        const citation = /^\[(\d+)\]$/.exec(chunk);
        const source = citation && account.sources[Number(citation[1]) - 1];
        if (source) {
          const a = link(source.url, chunk);
          a.setAttribute('aria-label', 'Source ' + citation[1] + ': ' + source.title);
          p.append(a);
        } else p.append(document.createTextNode(chunk));
      }
      body.append(p);
    }
    const list = e('ol', null, 'county-account-sources');
    list.setAttribute('aria-label', 'Sources for ' + county + ' County account');
    for (const source of account.sources) {
      const item = e('li');
      item.append(link(source.url, source.title));
      if (source.locator) item.append(e('span', ' · ' + source.locator));
      list.append(item);
    }
    body.append(list);
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
    renderCountyAccount();
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
    if(!matches.length){
      const hasHistory=data.records.some(r=>r.county===filters.county&&!archiveKinds.has(r.kind));
      const placeholder=filters.county&&filters.county!=='~statewide'&&!filters.kind&&!hasHistory;
      frag.append(e('p',placeholder?'County account forthcoming.':'No records match the selected filters.','no-results'));
    }
    if(matches.length>pageSize){
      const b=e('button','Show '+Math.min(18,matches.length-pageSize)+' more records','more-button');b.type='button';
      b.addEventListener('click',()=>{pageSize+=18;render(true);});frag.append(b);
    }
    current.replaceChildren(frag);
    if(focusNew)current.querySelector('[tabindex="-1"]')?.focus();
    $('results-count').hidden=!matches.length;
    $('results-count').textContent=matches.length?matches.length+' '+(matches.length===1?'record':'records'):'';
    $('clear').hidden=!(filters.period!=='all'||filters.county||filters.kind||filters.search||!filters.points);
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
  $('points').addEventListener('change',ev=>{filters.points=ev.target.checked;render();});
  $('clear').addEventListener('click',()=>{
    Object.assign(filters,{period:'all',county:'',search:'',kind:'',points:true});pageSize=18;render();$('search').focus({preventScroll:true});
  });
  readState();mapInit();render();
})();
