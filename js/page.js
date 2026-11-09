/* Not where it says on the ticket: airports and UK stations drawn to the place in their name, on a plain OpenFreeMap base map.
 * Dr Tristan Hotham, Independent researcher, 2026. MIT licence. */
(function () {
  'use strict';
  const qs = new URLSearchParams(location.search);
  const STYLE = 'https://tiles.openfreemap.org/styles/positron';
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const small = matchMedia('(max-width:800px)').matches;
  const fmt = n => Number(n).toLocaleString('en-GB');
  const RAMP = [0, '#F2C66D', 5, '#E9A03B', 15, '#D9702C', 40, '#B8322A', 90, '#7E1B2A'];
  let map = null, D = null, show = qs.get('show') || 'both', minKm = +(qs.get('min') || 0);
  document.getElementById('theme').addEventListener('click', () => { const r = document.documentElement, d = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; r.dataset.theme = d ? 'light' : 'dark'; });
  const ct = document.getElementById('cartouche'); const fold = f => ct.classList.toggle('folded', f);
  if (small) fold(true);
  document.getElementById('ctToggle').addEventListener('click', () => fold(!ct.classList.contains('folded')));
  document.getElementById('ctFold').addEventListener('click', () => fold(true));

  function features() {
    const F = D.fields, ix = {}; F.forEach((k, i) => ix[k] = i);
    const lines = [], pts = [], ends = [];
    D.f.forEach((r, i) => {
      const p = { i, t: r[ix.t], km: r[ix.km] };
      lines.push({ type: 'Feature', properties: p, geometry: { type: 'LineString', coordinates: [[r[ix.lon], r[ix.lat]], [r[ix.plon], r[ix.plat]]] } });
      pts.push({ type: 'Feature', properties: Object.assign({ m: r[ix.marketed] ? 1 : 0, s: r[ix.flag] }, p), geometry: { type: 'Point', coordinates: [r[ix.lon], r[ix.lat]] } });
      ends.push({ type: 'Feature', properties: p, geometry: { type: 'Point', coordinates: [r[ix.plon], r[ix.plat]] } });
    });
    return { ix, lines, pts, ends };
  }
  function rec(i) { const r = D.f[i], o = {}; D.fields.forEach((k, j) => o[k] = r[j]); return o; }
  function popup(i, ll) {
    const o = rec(i);
    let h;
    if (o.t === 'a') {
      const wd = o.id ? `<a href="https://www.wikidata.org/wiki/${esc(o.id)}" target="_blank" rel="noopener">airport on Wikidata</a>` : '';
      const pw = o.pid ? `<a href="https://www.wikidata.org/wiki/${esc(o.pid)}" target="_blank" rel="noopener">${esc(o.place)} on Wikidata</a>` : '';
      h = `<b class="t">${esc(o.name)}${o.code ? ' (' + esc(o.code) + ')' : ''}</b><div class="nt">${esc(o.country)}</div>
        <div class="big">${o.km.toFixed(0)} km</div><div>from ${esc(o.place)}${o.pop ? ' (population ' + fmt(o.pop) + ')' : ''}, the place in its name.</div>
        ${o.marketed ? `<div class="nt">Sold by airlines as <b>${esc(o.marketed)}</b>; that name is not in the Wikidata label.</div>` : ''}
        ${o.flag ? '<div class="nt">Another airport named after the same city is closer to it.</div>' : ''}
        ${o.pax ? `<table><tr><td>passengers</td><td>${fmt(o.pax)} a year (largest value in Wikidata)</td></tr></table>` : ''}
        <div class="lk">${wd}${pw}</div><div class="nt">Straight line from the airport's point to the place's point.</div>`;
    } else {
      h = `<b class="t">${esc(o.name)}</b><div class="nt">${o.code ? 'National Rail · ' + esc(o.code) : 'station or halt (heritage, metro or tram)'}</div>
        <div class="big">${o.km < 10 ? o.km.toFixed(1) : o.km.toFixed(0)} km</div><div>from ${esc(o.place)}${o.pop ? ' (population ' + fmt(o.pop) + ')' : ''}, the place in its name.</div>
        <div class="lk"><a href="https://www.openstreetmap.org/${esc(o.id)}" target="_blank" rel="noopener">station on OpenStreetMap</a>${o.pid ? `<a href="https://www.wikidata.org/wiki/${esc(o.pid)}" target="_blank" rel="noopener">${esc(o.place)} on Wikidata</a>` : ''}</div>
        <div class="nt">Straight line from the station to the place's point.</div>`;
    }
    new maplibregl.Popup({ maxWidth: '310px' }).setLngLat(ll).setHTML(h).addTo(map);
  }
  function filt() {
    const t = show === 'both' ? true : ['==', ['get', 't'], show === 'air' ? 'a' : 's'];
    const f = ['all', t, ['>=', ['get', 'km'], minKm]];
    ['ln', 'ap', 'st', 'end', 'aplbl'].forEach(l => map.getLayer(l) && map.setFilter(l, l === 'ap' ? ['all', f, ['==', ['get', 't'], 'a']] : l === 'st' ? ['all', f, ['==', ['get', 't'], 's']]
      : l === 'aplbl' ? ['all', f, ['==', ['get', 't'], 'a'], ['>=', ['get', 'km'], 40]] : f));
    document.querySelectorAll('.chip[data-s]').forEach(b => b.setAttribute('aria-pressed', b.dataset.s === show));
    document.getElementById('kmv').textContent = minKm ? 'only ' + minKm + ' km or more' : 'all distances';
  }
  function setup() {
    const before = (map.getStyle().layers.find(l => l.type === 'symbol') || {}).id;
    const G = features();
    const att = 'Airports: <a href="https://www.wikidata.org/" target="_blank">Wikidata</a> (CC0) · Stations: <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> (ODbL)';
    map.addSource('ln', { type: 'geojson', data: { type: 'FeatureCollection', features: G.lines }, attribution: att });
    map.addSource('pt', { type: 'geojson', data: { type: 'FeatureCollection', features: G.pts } });
    map.addSource('end', { type: 'geojson', data: { type: 'FeatureCollection', features: G.ends } });
    const col = ['interpolate', ['linear'], ['get', 'km'], ...RAMP];
    map.addLayer({ id: 'ln', type: 'line', source: 'ln', layout: { 'line-cap': 'round' }, paint: { 'line-color': col,
      'line-width': ['interpolate', ['linear'], ['zoom'], 3, ['interpolate', ['linear'], ['get', 'km'], 0, 0.8, 100, 3.5], 10, ['interpolate', ['linear'], ['get', 'km'], 0, 2, 100, 6]], 'line-opacity': 0.9 } }, before);
    map.addLayer({ id: 'end', type: 'circle', source: 'end', paint: { 'circle-color': '#FFFFFF', 'circle-stroke-color': '#26262B', 'circle-stroke-width': 1.2,
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 3, 2.2, 8, 3.5, 13, 5] } });
    const rad = (a, b) => ['interpolate', ['linear'], ['zoom'], 3, ['interpolate', ['linear'], ['get', 'km'], 0, a, 100, a + 3], 8, ['interpolate', ['linear'], ['get', 'km'], 0, b, 100, b + 4], 13, b + 3];
    map.addLayer({ id: 'st', type: 'circle', source: 'pt', filter: ['==', ['get', 't'], 's'], paint: { 'circle-color': col, 'circle-stroke-color': '#FFFFFF', 'circle-stroke-width': 1, 'circle-radius': rad(3, 4.5) } });
    map.addLayer({ id: 'ap', type: 'circle', source: 'pt', filter: ['==', ['get', 't'], 'a'], paint: { 'circle-color': col, 'circle-stroke-color': ['case', ['==', ['get', 'm'], 1], '#26262B', '#FFFFFF'], 'circle-stroke-width': ['case', ['==', ['get', 'm'], 1], 2, 1.2], 'circle-radius': rad(3.2, 5.5) } });
    map.addLayer({ id: 'aplbl', type: 'symbol', source: 'pt', filter: ['all', ['==', ['get', 't'], 'a'], ['>=', ['get', 'km'], 40]], minzoom: 4.5,
      layout: { 'text-field': ['concat', ['to-string', ['round', ['get', 'km']]], ' km'], 'text-font': ['Noto Sans Bold'], 'text-size': 11, 'text-offset': [0, 1.2], 'text-anchor': 'top' },
      paint: { 'text-color': '#7E1B2A', 'text-halo-color': '#fff', 'text-halo-width': 1.6 } });
    map.on('click', e => {
      const q = map.queryRenderedFeatures([[e.point.x - 5, e.point.y - 5], [e.point.x + 5, e.point.y + 5]], { layers: ['ap', 'st', 'ln'] });
      if (q.length) { const best = q.find(f => f.layer.id !== 'ln') || q[0]; popup(best.properties.i, e.lngLat); }
    });
    ['ap', 'st', 'ln'].forEach(l => { map.on('mouseenter', l, () => map.getCanvas().style.cursor = 'pointer'); map.on('mouseleave', l, () => map.getCanvas().style.cursor = ''); });
    const lp = document.getElementById('lp'), btn = document.getElementById('lyrBtn');
    btn.addEventListener('click', e => { e.stopPropagation(); const o = lp.classList.toggle('open'); btn.setAttribute('aria-expanded', o); });
    document.addEventListener('click', e => { if (!lp.contains(e.target) && e.target !== btn) { lp.classList.remove('open'); btn.setAttribute('aria-expanded', false); } });
    const vis = (id, v) => { if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', v ? 'visible' : 'none'); };
    document.getElementById('lyLn').addEventListener('change', e => vis('ln', e.target.checked));
    document.getElementById('lyAp').addEventListener('change', e => { vis('ap', e.target.checked); vis('aplbl', e.target.checked); });
    document.getElementById('lySt').addEventListener('change', e => vis('st', e.target.checked));
    document.getElementById('lyEnd').addEventListener('change', e => vis('end', e.target.checked));
    document.getElementById('lyLbl').addEventListener('change', e => map.getStyle().layers.filter(l => l.type === 'symbol' && l.id !== 'aplbl').forEach(l => vis(l.id, e.target.checked)));
    document.querySelectorAll('.chip[data-s]').forEach(b => b.addEventListener('click', () => { show = b.dataset.s; filt(); if (show === 'st') map.flyTo({ center: [-2.6, 54.4], zoom: small ? 4.6 : 5.3 }); }));
    const km = document.getElementById('km'); km.value = minKm;
    km.addEventListener('input', () => { minKm = +km.value; filt(); });
    filt();
  }
  function setupSearch() {
    const q = document.getElementById('q'), sug = document.getElementById('sug'); let items = [], k = -1;
    const idx = D.f.map((r, i) => { const o = rec(i); return { i, n: o.name + (o.code ? ' ' + o.code : ''), s: (o.t === 'a' ? 'airport · ' : 'station · ') + o.km.toFixed(o.km < 10 ? 1 : 0) + ' km from ' + o.place, k: norm(o.name + ' ' + (o.code || '') + ' ' + (o.marketed || '') + ' ' + o.place), ll: [o.lon, o.lat], km: o.km }; });
    const show_ = () => { const v = norm(q.value.trim()); sug.innerHTML = ''; k = -1; if (v.length < 2) { sug.style.display = 'none'; return; }
      items = idx.filter(x => x.k.startsWith(v)).concat(idx.filter(x => !x.k.startsWith(v) && x.k.includes(v))).sort((a, b) => (b.k.startsWith(v) - a.k.startsWith(v)) || b.km - a.km).slice(0, 12);
      items.forEach((it, j) => { const li = document.createElement('li'); li.setAttribute('role', 'option'); li.innerHTML = `${esc(it.n)} <span>${esc(it.s)}</span>`; li.addEventListener('mousedown', e => { e.preventDefault(); pick(j); }); sug.appendChild(li); });
      sug.style.display = items.length ? 'block' : 'none'; };
    const pick = j => { const it = items[j]; if (!it) return; q.value = it.n; sug.style.display = 'none'; fold(true); go(it.i); };
    q.addEventListener('input', show_);
    q.addEventListener('keydown', e => { const lis = [...sug.children];
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); k = Math.max(0, Math.min(lis.length - 1, k + (e.key === 'ArrowDown' ? 1 : -1))); lis.forEach((l, i) => l.setAttribute('aria-selected', i === k)); }
      else if (e.key === 'Enter') { e.preventDefault(); if (!items.length) show_(); pick(k < 0 ? 0 : k); } else if (e.key === 'Escape') sug.style.display = 'none'; });
    q.addEventListener('blur', () => setTimeout(() => sug.style.display = 'none', 150));
  }
  function go(i) {
    const o = rec(i); fold(true);
    if (show !== 'both' && (show === 'air') !== (o.t === 'a')) { show = 'both'; filt(); }
    if (o.km < minKm) { minKm = 0; document.getElementById('km').value = 0; filt(); }
    const b = [[Math.min(o.lon, o.plon), Math.min(o.lat, o.plat)], [Math.max(o.lon, o.plon), Math.max(o.lat, o.plat)]];
    map.fitBounds(b, { padding: small ? 60 : 140, maxZoom: o.t === 'a' ? 10 : 13, duration: 1200 });
    map.once('moveend', () => popup(i, [o.lon, o.lat]));
  }
  window.__go = n => { const i = D.f.findIndex(r => r[1] === n || r[2] === n); if (i >= 0) { document.getElementById('mapWrap').scrollIntoView({ behavior: 'smooth' }); setTimeout(() => go(i), 400); } };
  fetch('data/map.json').then(r => r.json()).then(d => {
    D = d;
    const at = (qs.get('at') || '').split(',').map(Number);
    const mo = at.length === 3 && at.every(isFinite) ? { center: [at[1], at[0]], zoom: at[2] } : { center: small ? [4, 50] : [1, 51.5], zoom: small ? 3.4 : 4.3 };
    const m0 = new maplibregl.Map(Object.assign({ container: 'map', style: STYLE, attributionControl: { compact: true }, maxZoom: 16 }, mo));
    return new Promise((res, rej) => { m0.once('load', () => res(m0)); m0.once('error', e => { if (!m0.loaded()) rej(e.error || e); }); });
  }).then(mm => {
    map = mm; window.__map = mm;
    mm.on('error', e => { const er = e && e.error; if (er && (er.name === 'AbortError' || /abort/i.test(er.message || ''))) return; console.error(er || e); });
    const n = document.getElementById('nojs'); if (n) n.remove();
    mm.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    const foldAt = () => document.querySelectorAll('.maplibregl-ctrl-attrib.maplibregl-compact').forEach(at => { at.classList.remove('maplibregl-compact-show'); at.removeAttribute('open'); });
    mm.once('idle', foldAt); setTimeout(foldAt, 1500);
    setup(); setupSearch();
    if (qs.get('open')) window.__go(qs.get('open'));
    document.getElementById('mapWrap').addEventListener('pointerdown', e => { if (e.target.closest && e.target.closest('.cartouche,.ov,.lp,.keys,.mfs-btn,.maplibregl-ctrl')) return; fold(true); }, { capture: true, passive: true, once: true });
  }).catch(e => { console.error(e); const n = document.getElementById('nojs'); if (n) n.textContent = 'The map could not load: ' + e.message; });
})();
