"""Check source/HTML consistency and the non-exact 2025 data contract."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/organ-transplants/annual_counts.json').read_text());rows=d['rows'];assert [r['year'] for r in rows]==list(range(2015,2026))
assert all(r['deceased_donors']>0 for r in rows)
assert all(r['solid_organ_transplant_procedures']>0 and r['status']=='annual_report_snapshot' for r in rows[:-1])
assert rows[-1]['solid_organ_transplant_procedures'] is None
assert rows[-1]['transplants_lower_bound_exclusive']==183800
assert rows[-1]['transplants_relation']=='greater_than'
assert rows[-1]['deceased_donors']==49169
assert d['kidney_waiting_list']['year']==2024 and d['kidney_waiting_list']['waiting_year_end']==377902 and d['kidney_waiting_list']['deaths_during_year']==19936
s=(ROOT/'presentation/index.html').read_text();embedded=json.loads(re.search(r'<script id="organData" type="application/json">(.*?)</script>',s,re.S).group(1));assert embedded==d
assert len(re.findall(r'<section\b[^>]*\bid="slide-\d+"',s))==50
assert s.count('class OrganTimeline')==1 and s.count('class PublicationTimeline')==1
assert "window.organTimeline?.activate(this.slides[next].contains(document.getElementById('organChart')))" in s
assert '2025 waiting-list data not verified' in s
print('PASS: 11 years, 2025 exclusive bound, 2024 kidney-only figures, HTML/data identity, 50 slides and both controllers')
