"""Check the slide 8 data contract and source snapshot totals."""
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
