"""Check the slide 7 data contract and source snapshot totals."""
from pathlib import Path
import json,csv,hashlib
ROOT=Path(__file__).resolve().parents[1];directory=ROOT/'data/publication-trends'
data=json.loads((directory/'annual_counts.json').read_text());keys=[t['key'] for t in data['techniques']]
source=list(csv.DictReader((directory/'annual_counts_2000_2023.csv').open()))
assert hashlib.sha256((directory/'annual_counts_2000_2023.csv').read_bytes()).hexdigest()==data['source']['source_csv_sha256']
assert [r['year'] for r in data['rows']]==list(range(2000,2027))
for i,r in enumerate(source):
 assert data['rows'][i]['year']==int(r['Year'])
 assert data['rows'][i]['counts']=={k:int(r[k]) for k in keys}
for k,total in {'Laser-assisted':152,'Inkjet':309,'Stereolithography':769,'Extrusion':1385}.items():
 assert sum(int(r[k]) for r in source)==total
for r in data['rows']:
 if r['year']<=2023:assert all(isinstance(v,int) and v>=0 for v in r['counts'].values())
 else:assert all(v is None for v in r['counts'].values()) and r['status']=='awaiting_comparable_source'
print('PASS: 96 source values, 4 totals, continuous years, and 12 explicitly unknown extension values')
# Current slide uses the independent complete Scopus series; retain WoS checks above.
import re
slide=(ROOT/'presentation/index.html').read_text()
embedded=json.loads(re.search(r'<script id="publicationData" type="application/json">(.*?)</script>',slide,re.S)[1])
scopus=list(csv.DictReader((directory/'scopus/annual_counts_2000_2026.csv').open()))
assert embedded['source']['database']=='Scopus (Elsevier)'
assert embedded['last_verified_year']==2026
assert [r['year'] for r in embedded['rows']]==list(range(2000,2027))
for actual,expected in zip(embedded['rows'],scopus):
 assert actual['counts']=={k:int(expected[k]) for k in keys}
assert embedded['rows'][-1]['status']=='year_to_date'
print('PASS: slide 7 matches all 108 Scopus counts; 2026 explicitly partial')
