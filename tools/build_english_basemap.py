"""Make English the preferred label language in the archived CARTO style."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/geography-2025/custom-map/carto-positron-2026-11-03.json'
TARGET = ROOT / 'map/basemap-english.json'


def main():
    style = json.loads(SOURCE.read_text())
    count = 0
    for layer in style['layers']:
        if layer['id'] in ('place_country_1', 'place_country_2'):
            layer.setdefault('paint', {})['text-color'] = '#000000'
        layout = layer.get('layout', {})
        field = layout.get('text-field')
        if field is not None and 'name' in json.dumps(field):
            layout['text-field'] = ['coalesce', ['get', 'name:en'], ['get', 'name_en'],
                                    ['get', 'name:latin'], ['get', 'name']]
            count += 1
    style.setdefault('metadata', {})['bioprinting:language'] = 'en'
    TARGET.write_text(json.dumps(style, separators=(',', ':')) + '\n')
    print(f'English-default labels configured in {count} layers')


if __name__ == '__main__':
    main()
