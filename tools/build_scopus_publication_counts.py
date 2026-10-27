"""Rebuild annual counts and provenance from original Scopus filter-count CSVs."""
from pathlib import Path
import csv,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/publication-trends/scopus'
DATE='2026-10-27'
SPECS={'Laser-assisted':('laser_assisted',334),'Inkjet':('inkjet',595),'Stereolithography':('stereolithography',1497),'Extrusion':('extrusion',2515)}
counts={};queries={};sources={}
for label,(slug,expected) in SPECS.items():
 path=OUT/'raw'/f'{slug}_filter_counts_{DATE}.csv'
 rows=list(csv.reader(path.open(encoding='utf-8-sig')))
 q=next(r[0] for r in rows if r and r[0].startswith('Your query : '))[len('Your query : '):]
 assert 'PUBYEAR' in q and '2027' in q and '1999' in q and 'SRCTYPE' in q and 'LANGUAGE' in q
 assert all(x not in q.lower() for x in ['sessionid','apikey','access_token'])
 h=next(i for i,r in enumerate(rows) if 'YEAR' in r and 'DOCUMENT TYPE' in r)
 cols=rows[h];yi=cols.index('YEAR');di=cols.index('DOCUMENT TYPE')
 yr={};types={}
 for r in rows[h+1:]:
  if len(r)>yi+1 and re.fullmatch(r'\d{4}',r[yi] or ''):
   y=int(r[yi]);assert y not in yr and 2000<=y<=2026
   yr[y]=int(r[yi+1].replace(',',''))
  if len(r)>di+1 and r[di]:types[r[di]]=int(r[di+1].replace(',',''))
 assert sum(yr.values())==expected,(label,sum(yr.values()),expected)
 assert set(types)<={'Article','Review'} and sum(types.values())==expected
 counts[label]={y:yr.get(y,0) for y in range(2000,2027)}
 queries[label]=q
 sources[label]={'raw_file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'search_total':expected,'year_sum':sum(yr.values()),'document_types':types}
with (OUT/'annual_counts_2000_2026.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Year',*SPECS,'Coverage','Retrieved','Database'])
 for y in range(2000,2027):w.writerow([y,*[counts[k][y] for k in SPECS],'Year-to-date' if y==2026 else 'Calendar-year snapshot',DATE,'Scopus'])
(OUT/'queries.json').write_text(json.dumps(queries,indent=2)+'\n')
(OUT/'provenance.json').write_text(json.dumps({'database':'Scopus (Elsevier)','retrieved':DATE,'year_convention':'Scopus YEAR facet / PUBYEAR as exported','partial_year':2026,'sources':sources},indent=2)+'\n')
print('Verified all four annual sums and document-type totals:',{k:v['search_total'] for k,v in sources.items()})
for y in [2023,2024,2025,2026]:print(y,{k:counts[k][y] for k in SPECS})
