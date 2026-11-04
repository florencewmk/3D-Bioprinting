"""Build slide 7 from the existing map, with all resources embedded."""
import html
import json
import re
from pathlib import Path

from opening_slides import footer

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'map'
NUMBER = 7
TITLE = 'Bioprinting around the world'
RECORD = {
    'number': NUMBER,
    'title': TITLE,
    'text': 'Interactive world map of bioprinting research and companies. '
            'The globe tours the five leading publication countries, 2000–2025. Press Down Arrow to open the map.',
    'notes': 'Start with the numbered country markers. The United States ranks first '
             'with 2,555 publications, China second with 2,106, and Germany fifth with 637. '
             'International papers may count for several countries. Press Down Arrow to open the interactive map. Use the filters to show '
             'companies, institutions or authors. Use Back to globe, Escape or Next slide to leave the map. Sources: OpenAlex and the archived geography dataset. '
             'World boundaries: Natural Earth.',
}


def json_script(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', r'\u003c')


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'Offline map template changed near {old[:70]!r}')
    return text.replace(old, new, 1)


def world_geometry():
    source = ROOT / 'data/geography-2025/custom-map/ne_50m_admin_0_countries.geojson'
    features = json.loads(source.read_text())['features']

    def round_coordinates(value):
        if isinstance(value, list):
            return [round_coordinates(item) for item in value]
        return round(value, 3)

    return [
        {'type': 'Feature', 'properties': {'name': feature['properties']['NAME_EN'],
                                           'label': [feature['properties'][key] for key in ('LABEL_Y', 'LABEL_X')]},
         'geometry': {'type': feature['geometry']['type'],
                      'coordinates': round_coordinates(feature['geometry']['coordinates'])}}
        for feature in features
    ]


def map_document():
    data = json.loads((MAP / 'data.json').read_text())
    for category in data['categories']:
        category['defaultVisible'] = category['id'] == 'countries'
    data['categories'].sort(key=lambda category: category['id'] != 'countries')
    app = (MAP / 'app.js').read_text()
    app = replace_once(app, "const response = await fetch('data.json'); if (!response.ok) throw new Error('Dataset unavailable'); data = await response.json();",
                       "data = JSON.parse($('offline-records').textContent);")
    app = replace_once(app, 'expandedCategories = new Set()', "expandedCategories = new Set(['countries'])")
    start = app.index('  const tileLayer = L.maplibreGL')
    end = app.index('  const cluster =', start)
    app = app[:start] + """  const world = JSON.parse($('offline-boundaries').textContent);
  const boundaries = L.geoJSON(world, {
    renderer: L.canvas(),
    style: {color:'#a5afb0', weight:1, fillColor:'#f8f8f4', fillOpacity:1},
    interactive:false
  }).addTo(map);
  const countryLabels = L.layerGroup();
  for (const layer of boundaries.getLayers()) {
    const {name, label: position} = layer.feature.properties;
    if (!name || !position.every(Number.isFinite)) continue;
    const label = L.divIcon({className:'offline-country-name', html:esc(name), iconSize:[0,0]});
    countryLabels.addLayer(L.marker(position, {
      icon:label, interactive:false, keyboard:false, pane:'shadowPane'
    }));
  }
  function showCountryLabels() {
    if (map.getZoom() >= 4) countryLabels.addTo(map);
    else countryLabels.remove();
  }
  map.on('zoomend', showCountryLabels);
  map.attributionControl.addAttribution('Natural Earth');
""" + app[end:]
    css = '\n'.join((MAP / name).read_text() for name in
                    ('vendor/leaflet.css', 'vendor/MarkerCluster.css', 'style.css'))
    # All markers use div icons. Remove Leaflet's unused raster icon defaults.
    css = re.sub(r'url\(images/[^)]+\)', 'none', css)
    css += """
:root { --sidebar: 432px; --header: 78px; }
#map { background: #dce6eb; }
.brand-title { font-size: 27px; }
.category-name { font-size: 20px; }
.country-name { font-size: 18px; }
.publication-total { font-size: 15px; }
.offline-country-name { color:#000; font-size:13px; font-weight:600; white-space:nowrap; }
"""
    vendor = '\n'.join((MAP / 'vendor' / name).read_text() for name in
                       ('leaflet.js', 'leaflet.markercluster.js'))
    vendor = re.sub(r'(?m)^//[#@] sourceMappingURL=.*$', '', vendor)
    policy = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'"
    head = f'<meta http-equiv="Content-Security-Policy" content="{policy}"><style>{css}</style>'
    page = (MAP / 'index.html').read_text()
    page = re.sub(r'  <link rel="stylesheet".*?\n  <script defer.*?\n', lambda _: head + '\n', page, count=1)
    page = page.replace('RESEARCH & COMPANIES · THROUGH 2025', 'PUBLICATIONS · 2000–2025')
    page = page.replace('English-default base map © CARTO and OpenStreetMap contributors. Map tiles need an internet connection.',
                        'World boundaries: Natural Earth (public domain).')
    licenses = '\n'.join((MAP / 'vendor' / name).read_text() for name in
                         ('leaflet-LICENSE', 'markercluster-LICENSE'))
    scripts = (
        f'<script id="offline-records" type="application/json">{json_script(data)}</script>'
        f'<script id="offline-boundaries" type="application/json">{json_script(world_geometry())}</script>'
        f'<script>{vendor}</script><script>{app}</script>'
    )
    return page.replace('</body>', f'<!-- {licenses} -->{scripts}</body>', 1)


def globe_document():
    points = json.loads((MAP / 'data.json').read_text())['points']
    leaders = sorted((
        {'rank': int(point['name'].split('.')[0]),
         'works': int(re.search(r'Works 2000–2025: (\d+)', point['description'])[1]),
         'country': point['country'], 'position': point['position']}
        for point in points if point['category'] == 'countries'
    ), key=lambda point: point['rank'])[:5]
    document = Path(__file__).with_name('globe-tour.html').read_text()
    map_keys = """<script>
document.addEventListener('keydown', event => {
  if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
  if (['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp'].includes(event.key)) {
    event.preventDefault();
    event.stopPropagation();
    window.parent.postMessage(['ArrowUp', 'PageUp'].includes(event.key) ? 'bioprinting-prev-slide' : 'bioprinting-next-slide', '*');
  } else if (event.key === 'Escape' && !document.querySelector('dialog[open], .leaflet-popup')) {
    event.preventDefault();
    window.parent.postMessage('bioprinting-close-map', '*');
  }
}, true);
</script>"""
    values = {
        '__RED_LAND__': ['United States of America', "People's Republic of China", 'Germany'],
        '__WORLD__': world_geometry(),
        '__LEADERS__': leaders,
        '__ATLAS__': map_document().replace('</body>', map_keys + '</body>', 1),
    }
    for placeholder, value in values.items():
        document = replace_once(document, placeholder, json_script(value))
    return document


def render_slide(number=NUMBER, total=51):
    embedded = html.escape(globe_document(), quote=True)
    keys = """<script>
(() => {
  const slide = document.currentScript.closest('.slide');
  const frame = slide.querySelector('iframe');
  let mapOpened = false;
  window.addEventListener('message', event => {
    if (event.source !== frame.contentWindow) return;
    if (event.data === 'bioprinting-map-opened') mapOpened = true;
    if (event.data === 'bioprinting-map-closed') mapOpened = false;
    if ((event.data === 'bioprinting-next-slide' || event.data === 'bioprinting-prev-slide') && slide.classList.contains('active')) {
      if (mapOpened) frame.contentWindow.postMessage('bioprinting-close-map', '*');
      const button = document.getElementById(event.data === 'bioprinting-next-slide' ? 'next' : 'prev');
      button.focus();
      button.click();
    }
  });
  document.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey ||
        !slide.classList.contains('active') || document.body.classList.contains('editing') ||
        document.querySelector('dialog[open]') || !frame.hasAttribute('srcdoc')) return;
    // Up/Down are left to the deck (change slides); Escape closes an open map
    if (event.key !== 'Escape' || !mapOpened) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    frame.contentWindow.postMessage('bioprinting-close-map', '*');
  }, true);
})();
</script>"""
    return (
        f'<section class="slide" id="slide-{number}" aria-label="{number}. {TITLE}" aria-hidden="true">'
        f'<iframe class="offline-map-frame" title="Bioprinting globe and interactive map" '
        f'style="position:absolute;inset:0 0 58px;width:100%;height:calc(100% - 58px);border:0" '
        f'data-srcdoc="{embedded}"></iframe>{footer(number).replace(" / 51</span>", f" / {total}</span>")}{keys}</section>'
    )


def update_presentation():
    target = ROOT / 'presentation/offline.html'
    original = target.read_text()
    slides = re.findall(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>', original)
    match = re.search(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>\s*<iframe class="offline-map-frame"', original)
    if not match:
        raise ValueError('Could not locate the offline map slide')
    number = int(match[1])
    slide = re.compile(rf'<section\b[^>]*\bid="slide-{number}"[^>]*>.*?</section>', re.S)
    updated = slide.sub(lambda _: render_slide(number, len(slides)), original, count=1)

    def source_data(match):
        records = json.loads(match[2])
        records[number - 1] = dict(RECORD, number=number)
        return match[1] + json_script(records) + match[3]

    updated = re.sub(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)',
                     source_data, updated, count=1, flags=re.S)
    transcript = ROOT / 'presentation/transcript.md'
    replacement = f'## {number:02d}. {TITLE}\n\n{RECORD["text"]}\n\n### Speaker notes\n\n{RECORD["notes"]}\n\n'
    notes, count = re.subn(rf'^## {number:02d}\..*?(?=^## |\Z)', lambda _: replacement,
                           transcript.read_text(), count=1, flags=re.S | re.M)
    if count != 1:
        raise ValueError('Could not locate the offline map in the transcript')
    target.write_text(updated)
    transcript.write_text(notes)


if __name__ == '__main__':
    update_presentation()
