from pathlib import Path
import json,re,csv,hashlib
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data/organ-transplants';d=json.loads((D/'annual_counts.json').read_text());r=d['rows'];assert [x['year'] for x in r]==list(range(2015,2026));assert r[-1]['solid_organ_transplant_procedures']==sum(r[-1]['transplants_by_organ'].values())==183879;assert r[-1]['deceased_donors']==49169;assert r[-1]['transplants_relation']=='exact'
w=d['waiting_list_totals'];assert w['year']==2025;assert sum(x['waiting_year_end'] for x in w['by_organ'].values())==w['waiting_year_end']==532905;assert sum(x['deaths_during_year'] for x in w['by_organ'].values())==w['deaths_during_year']==40019
cells=list(csv.DictReader((D/'waiting_lists_2025_cells.csv').open()));assert len(cells)==1128
for metric in ['waiting_year_end','deaths_during_year']:assert sum(int(x['value']) for x in cells if x['metric']==metric and x['value']!='')==w[metric]
s=(ROOT/'presentation/offline.html').read_text();assert json.loads(re.search(r'<script id="organData" type="application/json">(.*?)</script>',s,re.S).group(1))==d
section=next(m.group() for m in re.finditer(r'<section\b.*?</section>',s,re.S) if 'id="organChart"' in m.group());assert '532,905' in section and '40,019' in section and 'Organ-list entries' in section;assert 'Coverage varies.' not in section and 'All six solid-organ categories' not in section and 'Kidney only' not in section
count=len(re.findall(r'<section\b[^>]*\bid="slide-\d+"',s));assert count==json.loads((ROOT/'presentation/settings.json').read_text()).get('slide_count',51);assert s.count('class OrganTimeline')==1
print(f'PASS:2025 source arithmetic,1128cells,missing blanks,HTML/data identity,{count}slides')
