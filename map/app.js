/* Selection, disclosure and country name lists deliberately use separate state. */
'use strict';
(async () => {
  const $ = id => document.getElementById(id);
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = n => n.toLocaleString('en-US');
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
  const byId = new Map(data.points.map(p => [p.id, p]));
  const selected = new Set(data.points.filter(p => categories.find(c => c.id === p.category).defaultVisible).map(p => p.id));
  const expandedCategories = new Set(), expandedCountries = new Set(), listLimits = new Map();
  let query = $('search').value.trim().toLocaleLowerCase(), debounce, renderTicket;
  const models = categories.map(cat => {
    const points = data.points.filter(p => p.category === cat.id);
    const countryMap = new Map();
    for (const point of points) {
      point.search = (point.name + ' ' + point.country).toLocaleLowerCase();
      if (!countryMap.has(point.country)) countryMap.set(point.country, []);
      countryMap.get(point.country).push(point);
    }
    return {...cat, points, countries: [...countryMap].sort((a,b) => a[0].localeCompare(b[0])).map(([name, points], index) => ({name, points: points.sort((a,b) => a.name.localeCompare(b.name, undefined, {numeric:true})), key: `${cat.id}-${index}`}))};
  });
  const map = L.map('map', {zoomControl:false, minZoom:2, maxZoom:19, zoomSnap:.25, worldCopyJump:true}).setView([22,7],2);
  L.control.zoom({position:'bottomright'}).addTo(map);
  L.control.scale({position:'bottomleft', imperial:false}).addTo(map);
  const tileLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom:19, attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'}).addTo(map);
  let tileErrors = 0;
  tileLayer.on('tileerror', () => { if (++tileErrors > 4) { $('map-notice').textContent = 'Base map tiles are unavailable. Points and filters still work.'; $('map-notice').hidden = false; } });
  const cluster = L.markerClusterGroup({maxClusterRadius:44, showCoverageOnHover:false, spiderfyOnMaxZoom:true, removeOutsideVisibleBounds:true, animate:false, iconCreateFunction:c => L.divIcon({html:`<span class="cluster-bubble">${fmt(c.getChildCount())}</span>`, className:'cluster-icon',iconSize:[38,38]})}).addTo(map);
  const markers = new Map();
  function popup(point) {
    const category = models.find(c => c.id === point.category);
    const description = esc(point.description).replace(/https?:\/\/[^\s<>]+/g, url => `<a href="${url}" target="_blank" rel="noopener">${url}</a>`);
    return `<div class="popup-kicker">${esc(category.name)}</div><h2 class="popup-name">${esc(point.name)}</h2><p class="popup-country">${esc(point.country)}</p><div class="popup-description">${description}</div>`;
  }
  for (const point of data.points) {
    const color = models.find(c => c.id === point.category).color;
    const icon = L.divIcon({className:'map-pin',html:'',iconSize:[13,13]});
    const marker = L.marker(point.position, {icon, title:point.name, alt:point.name, keyboard:true}).bindPopup(() => popup(point), {maxWidth:350});
    marker.on('add', () => marker.getElement()?.style.setProperty('--pin-color', color));
    markers.set(point.id, marker);
  }
  const match = point => !query || point.search.includes(query);
  function renderMap() {
    cancelAnimationFrame(renderTicket);
    renderTicket = requestAnimationFrame(() => {
      const visible = data.points.filter(p => selected.has(p.id) && match(p));
      cluster.clearLayers(); cluster.addLayers(visible.map(p => markers.get(p.id)));
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
    const html = models.map(cat => {
      const state = checkboxState(cat.points), open = expandedCategories.has(cat.id);
      const matching = cat.points.filter(match);
      const countryRows = open ? cat.countries.filter(c => c.points.some(match)).map(country => {
        const countryState = checkboxState(country.points), listed = expandedCountries.has(country.key), matches = country.points.filter(match), limit = listLimits.get(country.key) || 50;
        return `<div class="country" data-country="${esc(country.name)}"><div class="country-row">${checkbox(`country-${country.key}`,`Select ${country.name} in ${cat.name}`,countryState,`data-action="country" data-category="${cat.id}" data-key="${country.key}"`)}<label class="country-name" for="country-${country.key}">${esc(country.name)}<span class="country-total">${fmt(query?matches.length:country.points.length)}</span></label><label class="list-toggle">${checkbox(`list-${country.key}`,`Show list for ${country.name} in ${cat.name}`,{checked:listed},`data-action="list" data-key="${country.key}" aria-controls="names-${country.key}"`)}List</label></div>${listed?`<div class="point-list" id="names-${country.key}" aria-label="${esc(country.name)} names in ${cat.name}">${matches.slice(0,limit).map(p=>`<div class="point-row">${checkbox(`point-${p.id}`,`Show ${p.name}`,{checked:selected.has(p.id)},`data-action="point" data-id="${p.id}"`)}<button class="point-name" data-focus="${p.id}">${esc(p.name)}</button></div>`).join('')}${matches.length>limit?`<button class="more-button" data-more="${country.key}">Show ${Math.min(50,matches.length-limit)} more · ${fmt(matches.length-limit)} remaining</button>`:''}</div>`:''}</div>`;
      }).join('') : '';
      return `<section class="category" style="--category-color:${cat.color}" data-category="${cat.id}"><div class="category-head">${checkbox(`category-${cat.id}`,`Select all ${cat.name}`,state,`data-action="category" data-category="${cat.id}"`)}<label class="category-label" for="category-${cat.id}"><span class="category-name"><span class="color-dot"></span>${esc(cat.name)}</span><span class="category-count">${query?`${fmt(matching.length)} matches · `:''}${fmt(state.count)} of ${fmt(cat.count)} selected</span></label><button class="disclosure" id="expand-${cat.id}" data-expand="${cat.id}" aria-expanded="${open}" aria-label="${open?'Collapse':'Expand'} ${cat.name}" aria-controls="countries-${cat.id}">${arrow}</button></div>${open?`<div class="category-body" id="countries-${cat.id}"><p class="category-note">${esc(cat.note)}<br>${cat.countryCount} countries / regions. Check “List” to see names.</p>${countryRows||'<p class="no-matches">No matching names or countries.</p>'}</div>`:''}</section>`;
    }).join('');
    $('tree').innerHTML = html;
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
      const point = byId.get(focus.dataset.focus); selected.add(point.id); renderTree();
      renderMap();
      requestAnimationFrame(() => {map.setView(point.position, Math.max(map.getZoom(), 8), {animate:false});cluster.zoomToShowLayer(markers.get(point.id),()=>markers.get(point.id).openPopup());});
      if (mobile) {$('app').classList.add('sidebar-closed');setMenu();map.invalidateSize();}
    }
  });
  $('search').addEventListener('input', event => {clearTimeout(debounce);debounce=setTimeout(()=>{query=event.target.value.trim().toLocaleLowerCase();renderTree();renderMap();},140);});
  $('collapse').onclick = () => {expandedCategories.clear();expandedCountries.clear();renderTree();};
  $('show-all').onclick = () => {setSelection(data.points,true);renderTree();renderMap();};
  $('clear-all').onclick = () => {selected.clear();renderTree();renderMap();};
  $('menu').onclick = () => {$('app').classList.toggle('sidebar-closed');setMenu();map.invalidateSize();};
  $('fit').onclick = () => {const points=data.points.filter(p=>selected.has(p.id)&&match(p));if(points.length)map.fitBounds(L.latLngBounds(points.map(p=>p.position)),{padding:[32,32],maxZoom:9});};
  renderTree(); renderMap();
})();
