/* Selection, disclosure and country name lists deliberately use separate state. */
'use strict';
(async () => {
  const $ = id => document.getElementById(id);
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = n => n.toLocaleString('en-US');
  const englishOrder = new Intl.Collator('en', {sensitivity:'base',numeric:true});
  const arrow = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="m7 4 6 6-6 6"/></svg>';
  const mobile = matchMedia('(max-width:760px)').matches;
  if (mobile) $('app').classList.add('sidebar-closed');
  const setMenu = () => { const open = !$('app').classList.contains('sidebar-closed'); $('menu').setAttribute('aria-expanded', String(open)); $('menu').setAttribute('aria-label', open ? 'Hide filters' : 'Show filters'); };
  setMenu();
  const showAbout = () => $('about').showModal();
  $('about-open').onclick = showAbout; $('data-notes').onclick = showAbout;
  $('about-close').onclick = () => $('about').close();
  $('about').addEventListener('click', e => { if (e.target === $('about') && (e.offsetX < 0 || e.offsetY < 0 || e.offsetX > $('about').clientWidth || e.offsetY > $('about').clientHeight)) $('about').close(); });
  let data;
  try { const response = await fetch('data.json'); if (!response.ok) throw new Error('Dataset unavailable'); data = await response.json(); }
  catch (error) { $('tree').innerHTML = '<p class="no-matches">The dataset could not load. <button onclick="location.reload()">Try again</button></p>'; $('header-count').textContent = 'Data unavailable'; return; }
  const categories = data.categories;
  const rankedPoints = data.points.filter(p=>p.category==='countries');
  const countryStats = new Map(rankedPoints.map(p=>[p.country, {
    rank:Number(p.name.match(/^(\d+)\./)[1]),
    works:Number(p.description.match(/Works 2000–2025: (\d+)/)[1])
  }]));
  const byId = new Map(data.points.map(p => [p.id, p]));
  const selected = new Set(data.points.filter(p => categories.find(c => c.id === p.category).defaultVisible).map(p => p.id));
  const expandedCategories = new Set(), expandedCountries = new Set(), listLimits = new Map();
  let query = $('search').value.trim().toLocaleLowerCase(), debounce, renderTicket, countrySort = 'most';
  const models = categories.map(cat => {
    const points = data.points.filter(p => p.category === cat.id);
    const countryMap = new Map();
    for (const point of points) {
      point.search = (point.name + ' ' + point.country).toLocaleLowerCase();
      if (!countryMap.has(point.country)) countryMap.set(point.country, []);
      countryMap.get(point.country).push(point);
    }
    return {...cat, points, countries: [...countryMap].sort((a,b) => englishOrder.compare(a[0],b[0])).map(([name, points], index) => ({name, points: points.sort((a,b) => englishOrder.compare(a.name,b.name)), key: `${cat.id}-${index}`}))};
  });
  const reducedMotion = matchMedia('(prefers-reduced-motion:reduce)');
  const map = L.map('map', {zoomControl:false, minZoom:2, maxZoom:19, zoomSnap:0, scrollWheelZoom:false, worldCopyJump:true, zoomAnimation:!reducedMotion.matches}).setView([22,7],2);
  // One animation loop per gesture. Leaflet 1.9.4's _move lifecycle keeps
  // markers and the vector background in sync without restarting flyTo.
  let wheelFrame=0, wheelTarget, wheelAnchor, wheelPosition, lastWheel=0, lastFrame=0, wheelActive=false;
  function finishWheel() {
    cancelAnimationFrame(wheelFrame);wheelFrame=0;
    if(wheelActive){wheelActive=false;map._moveEnd(true);}
  }
  function wheelStep(now) {
    const elapsed=Math.min(64,Math.max(1,now-lastFrame));lastFrame=now;
    const current=map.getZoom(), remaining=wheelTarget-current;
    const zoom=Math.abs(remaining)<.002?wheelTarget:current+remaining*(reducedMotion.matches?1:1-Math.exp(-elapsed/45));
    const offset=wheelPosition.subtract(map.getSize().divideBy(2));
    const center=map.unproject(map.project(wheelAnchor,zoom).subtract(offset),zoom);
    if(zoom!==current) map._move(center,zoom,{pinch:true});
    if(zoom!==wheelTarget || now-lastWheel<100) wheelFrame=requestAnimationFrame(wheelStep);
    else finishWheel();
  }
  $('map').addEventListener('wheel', event => {
    if(event.target.closest('.leaflet-control, .leaflet-popup')) return;
    event.preventDefault();
    const pixels=event.deltaY*(event.deltaMode===1?16:event.deltaMode===2?map.getSize().y:1);
    if(!pixels) return;
    const position=map.mouseEventToContainerPoint(event);
    const startingZoom=wheelActive?wheelTarget:map.getZoom();
    const target=Math.max(map.getMinZoom(),Math.min(map.getMaxZoom(),startingZoom-Math.max(-240,Math.min(240,pixels))/200));
    if(!wheelActive && target===startingZoom) return;
    if(!wheelActive) map.stop();
    lastWheel=performance.now();
    wheelTarget=target;
    if(!wheelActive || !position.equals(wheelPosition)){
      wheelAnchor=map.containerPointToLatLng(position);wheelPosition=position;
    }
    if(!wheelActive){lastFrame=lastWheel;wheelActive=true;map._moveStart(true);}
    if(!wheelFrame) wheelFrame=requestAnimationFrame(wheelStep);
  },{passive:false});
  $('map').addEventListener('pointerdown',finishWheel,{capture:true});
  $('map').addEventListener('keydown',finishWheel,{capture:true});
  window.addEventListener('blur',finishWheel);
  L.control.zoom({position:'bottomright'}).addTo(map);
  L.control.scale({position:'bottomleft', imperial:false}).addTo(map);
  const tileLayer = L.maplibreGL({style:'basemap-english.json?v=20261103-readability',interactive:false,updateInterval:16,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a>'}).addTo(map);
  const background = tileLayer.getMaplibreMap();
  background.on('load', () => {$('map').dataset.labelLanguage='en';});
  background.on('error', () => {if(!background.isStyleLoaded()){$('map-notice').textContent='The background map could not load. Points and filters still work.';$('map-notice').hidden=false;}});
  const cluster = L.markerClusterGroup({maxClusterRadius:44, showCoverageOnHover:false, spiderfyOnMaxZoom:true, removeOutsideVisibleBounds:true, animate:false, iconCreateFunction:c => L.divIcon({html:`<span class="cluster-bubble">${fmt(c.getChildCount())}</span>`, className:'cluster-icon',iconSize:[38,38]})}).addTo(map);
  // Ranking badges have a separate layer: a rank is never a cluster count.
  map.createPane('rankPane').style.zIndex=650;
  const ranks=L.layerGroup().addTo(map), rankLines=new Map(), markers = new Map();
  function layoutRanks() {
    const occupied=[], size=map.getSize();
    const points=rankedPoints.filter(p=>ranks.hasLayer(markers.get(p.id)));
    for(const point of points){
      const origin=map.latLngToContainerPoint(point.position);
      let placed=origin;
      if(origin.x>=0&&origin.y>=0&&origin.x<=size.x&&origin.y<=size.y){
        for(let attempt=0;attempt<180;attempt++){
          const radius=attempt?Math.sqrt(attempt)*12:0, angle=attempt*2.399963;
          const candidate=L.point(Math.max(20,Math.min(size.x-20,origin.x+Math.cos(angle)*radius)),Math.max(20,Math.min(size.y-20,origin.y+Math.sin(angle)*radius)));
          if(occupied.every(p=>p.distanceTo(candidate)>=39)){placed=candidate;break;}
        }
        occupied.push(placed);
      }
      const position=map.containerPointToLatLng(placed);
      markers.get(point.id).setLatLng(position);
      rankLines.get(point.id).setLatLngs(origin.distanceTo(placed)>4?[point.position,position]:[]);
    }
  }
  map.on('moveend resize',layoutRanks);
  function popup(point) {
    const category = models.find(c => c.id === point.category);
    const description = esc(point.description).replace(/https?:\/\/[^\s<>]+/g, url => `<a href="${url}" target="_blank" rel="noopener">${url}</a>`);
    return `<div class="popup-kicker">${esc(category.name)}</div><h2 class="popup-name">${esc(point.name)}</h2><p class="popup-country">${esc(point.country)}</p><div class="popup-description">${description}</div>`;
  }
  for (const point of data.points) {
    const color = models.find(c => c.id === point.category).color;
    const stat=point.category==='countries'?countryStats.get(point.country):null;
    const icon = stat ? L.divIcon({className:'rank-pin',html:`<span>#${stat.rank}</span>`,iconSize:[32,32],iconAnchor:[16,16]}) : L.divIcon({className:'map-pin',html:'',iconSize:[13,13]});
    const marker = L.marker(point.position, {icon, title:point.name, alt:point.name, keyboard:true,...(stat?{pane:'rankPane'}:{})}).bindPopup(() => popup(point), {maxWidth:350});
    marker.on('add', () => marker.getElement()?.style.setProperty('--pin-color', color));
    markers.set(point.id, marker);
    if(stat) rankLines.set(point.id,L.polyline([],{color:'#285b48',weight:1.5,opacity:.82,interactive:false}));
  }
  const match = point => !query || point.search.includes(query);
  function orderedCountries(countries, category) {
    return countries.filter(c => c.points.some(match)).sort((a,b) => {
      const name = englishOrder.compare(a.name,b.name);
      if(countrySort==='za') return -name;
      if(countrySort==='most'||countrySort==='fewest'){
        const difference=category==='countries'?countryStats.get(a.name).works-countryStats.get(b.name).works:a.points.filter(match).length-b.points.filter(match).length;
        return (countrySort==='most'?-difference:difference)||name;
      }
      return name;
    });
  }
  let visibleIds = new Set();
  function renderMap() {
    cancelAnimationFrame(renderTicket);
    renderTicket = requestAnimationFrame(() => {
      const visible = data.points.filter(p => selected.has(p.id) && match(p));
      const nextIds = new Set(visible.map(p => p.id));
      const removedIds=[...visibleIds].filter(id=>!nextIds.has(id));
      const addedPoints=visible.filter(p=>!visibleIds.has(p.id));
      for(const id of removedIds) if(byId.get(id).category==='countries'){ranks.removeLayer(markers.get(id));ranks.removeLayer(rankLines.get(id));}
      for(const p of addedPoints) if(p.category==='countries'){ranks.addLayer(rankLines.get(p.id));ranks.addLayer(markers.get(p.id));}
      const removed=removedIds.filter(id=>byId.get(id).category!=='countries').map(id=>markers.get(id));
      const added=addedPoints.filter(p=>p.category!=='countries').map(p=>markers.get(p.id));
      if (removed.length) cluster.removeLayers(removed);
      if (added.length) cluster.addLayers(added);
      visibleIds=nextIds;
      layoutRanks();
      $('selection-status').textContent = `${fmt(visible.length)} shown`;
      $('header-count').textContent = `${fmt(visible.length)} / ${fmt(data.points.length)} points`;
      $('header-count').dataset.visiblePoints = visible.length;
      $('empty-map').hidden = visible.length !== 0;
      $('empty-map').querySelector('strong').textContent = query ? 'No matching selected points' : 'No points selected';
      $('fit').disabled = visible.length === 0;
    });
  }
  function checkboxState(points) { const count = points.filter(p => selected.has(p.id)).length; return {checked:count === points.length, mixed:count > 0 && count < points.length, count}; }
  function checkbox(id, label, state, attrs='') { return `<input type="checkbox" id="${id}" aria-label="${esc(label)}" ${state.checked?'checked':''} data-mixed="${state.mixed?'true':'false'}" ${attrs}>`; }
  function renderTree(focusId) {
    const previousPanels=new Set([...$('tree').querySelectorAll('.category-body,.point-list')].map(el=>el.id));
    const html = models.map(cat => {
      const state = checkboxState(cat.points), open = expandedCategories.has(cat.id);
      const matching = cat.points.filter(match);
      const countryRows = open ? orderedCountries(cat.countries,cat.id).map(country => {
        const countryState = checkboxState(country.points), listed = expandedCountries.has(country.key), matches = country.points.filter(match), limit = listLimits.get(country.key) || 50;
        const stat=cat.id==='countries'?countryStats.get(country.name):null;
        const entries=query?matches.length:country.points.length;
        const countryLabel=stat?`<span class="sidebar-rank">#${stat.rank}</span> ${esc(country.name)}<span class="publication-total">${fmt(stat.works)} publications</span>`:`${esc(country.name)}<span class="country-total">${fmt(entries)} ${entries===1?'entry':'entries'}</span>`;
        return `<div class="country" data-country="${esc(country.name)}"><div class="country-row">${checkbox(`country-${country.key}`,`Select ${country.name} in ${cat.name}`,countryState,`data-action="country" data-category="${cat.id}" data-key="${country.key}"`)}<label class="country-name" for="country-${country.key}">${countryLabel}</label><label class="list-toggle">${checkbox(`list-${country.key}`,`Show list for ${country.name} in ${cat.name}`,{checked:listed},`data-action="list" data-key="${country.key}" aria-controls="names-${country.key}"`)}List</label></div>${listed?`<div class="point-list" id="names-${country.key}" aria-label="${esc(country.name)} names in ${cat.name}">${matches.slice(0,limit).map(p=>`<div class="point-row">${checkbox(`point-${p.id}`,`Show ${p.name}`,{checked:selected.has(p.id)},`data-action="point" data-id="${p.id}"`)}<button class="point-name" data-focus="${p.id}">${esc(p.name)}</button></div>`).join('')}${matches.length>limit?`<button class="more-button" data-more="${country.key}">Show ${Math.min(50,matches.length-limit)} more · ${fmt(matches.length-limit)} remaining</button>`:''}</div>`:''}</div>`;
      }).join('') : '';
      return `<section class="category" style="--category-color:${cat.color}" data-category="${cat.id}"><div class="category-head">${checkbox(`category-${cat.id}`,`Select all ${cat.name}`,state,`data-action="category" data-category="${cat.id}"`)}<label class="category-label" for="category-${cat.id}"><span class="category-name"><span class="color-dot"></span>${esc(cat.name)}</span><span class="category-count">${query?`${fmt(matching.length)} matches · `:''}${fmt(state.count)} of ${fmt(cat.count)} selected</span></label><button class="disclosure" id="expand-${cat.id}" data-expand="${cat.id}" aria-expanded="${open}" aria-label="${open?'Collapse':'Expand'} ${cat.name}" aria-controls="countries-${cat.id}">${arrow}</button></div>${open?`<div class="category-body" id="countries-${cat.id}"><p class="category-note">${esc(cat.note)}<br>${cat.countryCount} countries / regions. Check “List” to see names.</p>${countryRows||'<p class="no-matches">No matching names or countries.</p>'}</div>`:''}</section>`;
    }).join('');
    $('tree').innerHTML = html;
    $('tree').querySelectorAll('.category-body,.point-list').forEach(el=>{if(!previousPanels.has(el.id))el.classList.add('newly-open');});
    $('tree').querySelectorAll('[data-mixed="true"]').forEach(el => {el.indeterminate = true;});
    if (focusId) document.getElementById(focusId)?.focus({preventScroll:true});
  }
  function setSelection(points, value) { for (const p of points) value ? selected.add(p.id) : selected.delete(p.id); }
  $('tree').addEventListener('change', event => {
    const el = event.target, action = el.dataset.action;
    if (action === 'list') el.checked ? expandedCountries.add(el.dataset.key) : expandedCountries.delete(el.dataset.key);
    if (action === 'category') setSelection(models.find(c => c.id === el.dataset.category).points, el.checked);
    if (action === 'country') setSelection(models.find(c => c.id === el.dataset.category).countries.find(c => c.key === el.dataset.key).points, el.checked);
    if (action === 'point') el.checked ? selected.add(el.dataset.id) : selected.delete(el.dataset.id);
    renderTree(el.id); if (action !== 'list') renderMap();
  });
  $('tree').addEventListener('click', event => {
    const expand = event.target.closest('[data-expand]'), focus = event.target.closest('[data-focus]'), more = event.target.closest('[data-more]');
    if (expand) {const id=expand.dataset.expand;expandedCategories.has(id)?expandedCategories.delete(id):expandedCategories.add(id);renderTree(expand.id);}
    if (more) {const key=more.dataset.more;listLimits.set(key,(listLimits.get(key)||50)+50);renderTree();}
    if (focus) {
      finishWheel();
      const point = byId.get(focus.dataset.focus); selected.add(point.id); renderTree();
      renderMap();
      requestAnimationFrame(() => {map.setView(point.position, Math.max(map.getZoom(), 8), {animate:false});if(point.category==='countries') markers.get(point.id).openPopup();else cluster.zoomToShowLayer(markers.get(point.id),()=>markers.get(point.id).openPopup());});
      if (mobile) {$('app').classList.add('sidebar-closed');setMenu();map.invalidateSize();}
    }
  });
  $('search').addEventListener('input', event => {clearTimeout(debounce);debounce=setTimeout(()=>{query=event.target.value.trim().toLocaleLowerCase();renderTree();renderMap();},140);});
  $('country-sort').addEventListener('change', event => {countrySort=event.target.value;renderTree();});
  $('collapse').onclick = () => {expandedCategories.clear();expandedCountries.clear();renderTree();};
  $('show-all').onclick = () => {setSelection(data.points,true);renderTree();renderMap();};
  $('clear-all').onclick = () => {selected.clear();renderTree();renderMap();};
  $('menu').onclick = () => {finishWheel();$('app').classList.toggle('sidebar-closed');setMenu();map.invalidateSize();};
  $('fit').onclick = () => {finishWheel();const points=data.points.filter(p=>selected.has(p.id)&&match(p));if(points.length)map.fitBounds(L.latLngBounds(points.map(p=>p.position)),{padding:[32,32],maxZoom:9});};
  renderTree(); renderMap();
})();
