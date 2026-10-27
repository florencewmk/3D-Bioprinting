"""Archive public OpenAlex metadata. Uses curl with certificate verification.

Run from repository root. Reuses saved pages; no API key or private data needed.
"""
import gzip
import json
import subprocess
import time
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/geography-2025'
RAW = BASE / 'raw'
SEARCH = 'bioprint* OR "bio printing" OR "bio printed" OR "bio printer" OR "bio printers"'
FILTER = 'to_publication_date:2025-12-31,type:article|review,is_retracted:false'
PARAMS = {'search.title_and_abstract.exact': SEARCH, 'filter': FILTER}

def request(params, target):
    url = 'https://api.openalex.org/' + params.pop('_endpoint', 'works') + '?' + urlencode(params)
    if target.exists():
        opener = gzip.open if target.suffix == '.gz' else open
        with opener(target, 'rt') as f:
            return json.load(f)
    for attempt in range(3):
        p = subprocess.run(['curl', '--silent', '--show-error', '--fail-with-body', '--location',
                            '--max-time', '90', url], capture_output=True)
        if p.returncode == 0:
            data = json.loads(p.stdout)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.suffix == '.gz':
                with gzip.open(target, 'wt', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            else:
                target.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            with (BASE / 'requests.jsonl').open('a') as f:
                f.write(json.dumps({'retrieved_date': '2026-10-27', 'url': url,
                    'path': str(target.relative_to(BASE)), 'count': data.get('meta', {}).get('count')}) + '\n')
            return data
        if b'429' in p.stderr or b'budget' in p.stdout.lower():
            raise RuntimeError('Public API budget/rate limit reached; saved pages retained.')
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(p.stderr.decode() + p.stdout.decode()[:1000])

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    if '--institutions' in sys.argv:
        ids = set()
        for page in list(RAW.glob('historical-*.gz')) + list(RAW.glob('recent-*.gz')):
            with gzip.open(page, 'rt') as f:
                for w in json.load(f)['results']:
                    if w['publication_year'] >= 2000:
                        ids.update(i['id'].rsplit('/', 1)[-1] for a in w['authorships'] for i in a['institutions'])
        ids = sorted(ids)
        for start in range(0, len(ids), 100):
            d = request({'_endpoint': 'institutions', 'filter': 'openalex:' + '|'.join(ids[start:start+100]),
                'per_page': 200, 'select': 'id,display_name,ror,country_code,type,geo,homepage_url'},
                RAW / f'institutions-{start//100+1:03d}.json.gz')
            print('institution batch', start//100+1, len(d['results']), flush=True)
        return
    for name, group in [('countries-api', 'authorships.institutions.country_code'),
                        ('years-api', 'publication_year')]:
        data = request({**PARAMS, 'group_by': group, 'per_page': 200}, RAW / (name + '.json'))
        print(name, data['meta']['count'], flush=True)
    total = 0
    # Ordinary public page pagination supports <=10,000 records per query.
    # Disjoint publication-date windows keep each query below this documented limit.
    for window, extra in [('historical', ',to_publication_date:2020-12-31'),
                          ('recent', ',from_publication_date:2021-01-01')]:
        for page in range(1, 51):
            filt = FILTER.replace('to_publication_date:2025-12-31', 'to_publication_date:2020-12-31') if window == 'historical' else FILTER + extra
            data = request({**PARAMS, 'filter': filt, 'page': page, 'per_page': 200,
                'sort': 'publication_date:asc',
                'select': 'id,doi,title,publication_year,publication_date,type,is_retracted,authorships,is_authors_truncated'},
                RAW / f'{window}-{page:03d}.json.gz')
            total += len(data['results'])
            print(f'{window} page {page}: {total} collected; window total {data["meta"]["count"]}', flush=True)
            if page * 200 >= data['meta']['count']:
                break
    print('Complete', total, flush=True)

if __name__ == '__main__':
    main()
