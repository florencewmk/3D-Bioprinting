"""Build the custom map from archived My Maps inputs and an actual map export."""
import csv
import hashlib
import json
import re
import unicodedata
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/geography-2025'
MAP = ROOT / 'map'
NS = {'k': 'http://www.opengis.net/kml/2.2'}
EXPORT = DATA / 'custom-map/google-export-2026-11-03.kml'


def text(node, path):
    found = node.find(path, NS)
    return found.text or '' if found is not None else ''


def fields(node):
    return {el.attrib['name']: text(el, 'k:value') for el in node.findall('k:ExtendedData/k:Data', NS)}


def point(node):
    lon, lat, *_ = map(float, text(node, 'k:Point/k:coordinates').strip().split(','))
    assert -90 <= lat <= 90 and -180 <= lon <= 180
    return [lat, lon]


def place_key(name):
    return re.sub('[^a-z0-9]', '', unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower())


def gazetteer_locations(companies):
    source = DATA / 'custom-map/geonames-cities500.zip'
    research = {r['company_name']: r for r in json.loads((DATA / 'company_research.json').read_text())}
    wanted = {(place_key(r['Location'].rsplit(', ', 1)[0]), research[r['Name']]['country_code']) for r in companies}
    aliases = {'villazstpierre': 'villazsaintpierre'}
    wanted = {(aliases.get(name, name), code) for name, code in wanted}
    candidates = {key: [] for key in wanted}
    with zipfile.ZipFile(source) as z:
        for raw in z.read('cities500.txt').decode().splitlines():
            row = raw.split('\t')
            if row[8] not in {code for _, code in wanted}: continue
            names = {place_key(name) for name in [row[1], row[2], *row[3].split(',')]}
            for name, code in wanted:
                if code == row[8] and name in names:
                    candidates[(name, code)].append(row)
    found = {}
    for company in companies:
        key = place_key(company['Location'].rsplit(', ', 1)[0]); key = aliases.get(key, key)
        matches = candidates[(key, research[company['Name']]['country_code'])]
        assert matches, f'No city match: {company["Location"]}'
        row = max(matches, key=lambda r: int(r[14] or 0))
        found[company['Name']] = {'position': [float(row[4]), float(row[5])], 'geonames_id': row[0],
            'matched_name': row[1], 'country_code': row[8], 'admin1': row[10], 'population': int(row[14] or 0)}
    (DATA / 'custom-map/company-city-matches.json').write_text(json.dumps(found, ensure_ascii=False, indent=2) + '\n')
    return found


def main():
    export = ET.parse(EXPORT)
    folders = {text(f, 'k:name'): f.findall('k:Placemark', NS) for f in export.findall('.//k:Folder', NS)}
    assert sum(map(len, folders.values())) == 5572
    categories = [
        {'id': 'companies', 'name': 'Companies', 'color': '#a55391', 'defaultVisible': True,
         'note': '38 company lineages; city-level locations.'},
        {'id': 'affiliations', 'name': 'Affiliations', 'color': '#427ba0', 'defaultVisible': True,
         'note': 'Top 100 institutions by publications in 2021–2025.'},
        {'id': 'other', 'name': 'Other affiliations', 'color': '#83919c', 'defaultVisible': False,
         'note': 'All 5,242 remaining geolocated institutions, combined in one category.'},
        {'id': 'authors', 'name': 'Authors', 'color': '#b87e38', 'defaultVisible': False,
         'note': '100 authors at 172 last-observed institutional locations.'},
        {'id': 'countries', 'name': 'Top 20 countries', 'color': '#4f8871', 'defaultVisible': False,
         'note': 'Country totals for publications in 2000–2025.'},
    ]
    records = []
    for file, category in [
        ('03-affiliations-top100.kml', 'affiliations'),
        ('04-affiliations-other-1.kml', 'other'),
        ('05-affiliations-other-2.kml', 'other'),
        ('06-affiliations-other-3.kml', 'other'),
        ('07-authors-top100.kml', 'authors'),
    ]:
        for pm in ET.parse(DATA / 'google-map' / file).findall('.//k:Placemark', NS):
            records.append({'id': f'p{len(records)}', 'category': category, 'name': text(pm, 'k:name'),
                            'country': fields(pm)['Country'], 'position': point(pm),
                            'description': text(pm, 'k:description')})
    with (DATA / 'google-map/01-companies.csv').open(newline='') as f:
        companies = list(csv.DictReader(f))
    company_points = {text(p, 'k:name'): p for p in folders['Companies']}
    assert set(company_points) == {r['Name'] for r in companies}
    city_matches = gazetteer_locations(companies)
    for row in companies:
        records.append({'id': f'p{len(records)}', 'category': 'companies', 'name': row['Name'],
                        'country': row['Country'], 'position': city_matches[row['Name']]['position'],
                        'description': '\n'.join(f'{k}: {v}' for k, v in row.items() if k not in ('Name', 'Country'))})
    with (DATA / 'google-map/08-top20-countries.csv').open(newline='') as f:
        countries = list(csv.DictReader(f))
    country_points = {text(p, 'k:name'): p for p in folders['Top 20 countries — publications 2000–2025']}
    assert set(country_points) == {r['Name'] for r in countries}
    natural = json.loads((DATA / 'custom-map/ne_50m_admin_0_countries.geojson').read_text())
    anchors = {f['properties']['ISO_A2_EH']: [f['properties']['LABEL_Y'], f['properties']['LABEL_X']] for f in natural['features']}
    with (DATA / 'countries.csv').open(newline='') as f:
        country_codes = {r['country']: r['country_code'] for r in csv.DictReader(f)}
    for row in countries:
        records.append({'id': f'p{len(records)}', 'category': 'countries', 'name': row['Name'],
                        'country': row['Location'], 'position': anchors[country_codes[row['Location']]],
                        'description': '\n'.join(f'{k}: {v}' for k, v in row.items() if k != 'Name') + '\nCountry summary at a Natural Earth label anchor, not an institution location.'})
    expected = {'companies': 38, 'affiliations': 100, 'other': 5242, 'authors': 172, 'countries': 20}
    assert len(records) == 5572 and len({r['id'] for r in records}) == 5572
    for cat in categories:
        selected = [r for r in records if r['category'] == cat['id']]
        assert len(selected) == expected[cat['id']]
        cat['count'] = len(selected)
        cat['countryCount'] = len({r['country'] for r in selected})
    result = {'title': 'Bioprinting World Map', 'researchYears': '2000–2025',
              'retrieved': '2026-10-27', 'interfaceUpdated': '2026-11-03',
              'source': 'https://github.com/florencewmk/3D-Bioprinting/tree/main/data/geography-2025',
              'categories': categories, 'points': records}
    MAP.mkdir(exist_ok=True)
    (MAP / 'data.json').write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')) + '\n')
    provenance = {'built': '2026-11-03', 'source_map_id': '1xMICGif7YhqVEFiDnPdq-cAFGzoo6v0',
                  'export_file': str(EXPORT.relative_to(ROOT)),
                  'export_sha256': hashlib.sha256(EXPORT.read_bytes()).hexdigest(),
                  'company_geometry': 'City-level GeoNames matches; names and countries unchanged. The My Maps export contains addresses without coordinates for these points.',
                  'country_geometry': 'Natural Earth country label anchors; publication values unchanged',
                  'geometry_sources': ['https://download.geonames.org/export/dump/cities500.zip', 'https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_admin_0_countries.geojson'],
                  'geometry_source_sha256': {name: hashlib.sha256((DATA/'custom-map'/name).read_bytes()).hexdigest() for name in ['geonames-cities500.zip','ne_50m_admin_0_countries.geojson']},
                  'institution_geometry': 'Unchanged archived OpenAlex institution coordinates',
                  'categories': categories, 'total_points': len(records),
                  'data_sha256': hashlib.sha256((MAP / 'data.json').read_bytes()).hexdigest()}
    (DATA / 'custom-map/provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'points': len(records), 'counts': expected, 'bytes': (MAP / 'data.json').stat().st_size}))


if __name__ == '__main__':
    main()
