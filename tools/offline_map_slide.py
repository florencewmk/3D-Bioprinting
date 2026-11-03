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
            'The initial view shows the top 20 countries by publication count, 2000–2025.',
    'notes': 'Start with the numbered country markers. The United States ranks first '
             'with 2,555 publications, China second with 2,106, and Germany fifth with 637. '
             'International papers may count for several countries. Use the filters to show '
             'companies, institutions or authors. Click outside the map to resume slide '
             'keyboard controls. Sources: OpenAlex and the archived geography dataset. '
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


def render_slide():
    embedded = html.escape(map_document(), quote=True)
    return (
        f'<section class="slide" id="slide-{NUMBER}" aria-label="{NUMBER}. {TITLE}" aria-hidden="true">'
        f'<iframe class="offline-map-frame" title="Interactive Bioprinting World Map" '
        f'style="position:absolute;inset:0 0 58px;width:100%;height:calc(100% - 58px);border:0" '
        f'srcdoc="{embedded}"></iframe>{footer(NUMBER)}</section>'
    )


def update_presentation():
    target = ROOT / 'presentation/index.html'
    original = target.read_text()
    slide = re.compile(r'<section\b[^>]*\bid="slide-7"[^>]*>.*?</section>', re.S)
    updated, count = slide.subn(lambda _: render_slide(), original, count=1)
    if count != 1:
        raise ValueError('Could not locate slide 7')

    def source_data(match):
        records = json.loads(match[2])
        records[NUMBER - 1] = RECORD
        return match[1] + json_script(records) + match[3]

    updated = re.sub(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)',
                     source_data, updated, count=1, flags=re.S)
    transcript = ROOT / 'presentation/transcript.md'
    replacement = f'## 07. {TITLE}\n\n{RECORD["text"]}\n\n### Speaker notes\n\n{RECORD["notes"]}\n\n'
    notes, count = re.subn(r'^## 07\..*?(?=^## 08\.)', lambda _: replacement,
                           transcript.read_text(), count=1, flags=re.S | re.M)
    if count != 1:
        raise ValueError('Could not locate slide 7 in the transcript')
    target.write_text(updated)
    transcript.write_text(notes)


if __name__ == '__main__':
    update_presentation()
