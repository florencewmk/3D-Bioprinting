"""Data-driven slide 7. Missing annual counts remain null, never observed zeros."""
from pathlib import Path
import json,html,csv
ROOT=Path(__file__).resolve().parents[1]
def render_publication_slide():
 data=json.loads((ROOT/'data/publication-trends/annual_counts.json').read_text())
 data['last_verified_year']=2026
 data['as_of']='2026-10-27'
 data['source']={'database':'Scopus (Elsevier)','retrieved':'2026-10-27','counting_unit':'Overlapping technique keyword matches','csv':'data/publication-trends/scopus/annual_counts_2000_2026.csv'}
 rows=list(csv.DictReader((ROOT/'data/publication-trends/scopus/annual_counts_2000_2026.csv').open()))
 data['rows']=[{'year':int(row['Year']),'status':'year_to_date' if row['Year']=='2026' else 'verified_snapshot','counts':{t['key']:int(row[t['key']]) for t in data['techniques']}} for row in rows]
 for t in data['techniques']:t['verified_snapshot_total']=sum(row['counts'][t['key']] for row in data['rows'])
 return '''<div class="publication-chart" id="publicationChart">
<div class="pub-heading"><h1 class="editable" data-edit="pub-title">Bioprinting publications</h1><p>Annual keyword matches · Scopus (Elsevier) · 2000–2026*</p></div>
<svg id="publicationPlot" viewBox="0 0 1450 620" role="img" aria-label="Annual publication category matches, 2000–2026. 2026 is partial, indexed as of 27 October 2026."></svg>
<aside class="pub-year-panel" aria-label="Selected year counts"><p class="pub-small">SELECTED YEAR</p><output id="publicationYear">2000</output><p class="pub-year-status" id="publicationStatus">Historical snapshot</p><div id="publicationCounts"></div><div class="pub-total"><span>Category matches</span><strong id="publicationTotal">0</strong></div></aside>
<div class="pub-legend" id="publicationLegend"></div>
<div class="pub-timeline" aria-label="Publication animation controls"><button id="publicationPlay" aria-label="Play yearly animation">Pause</button><button id="publicationReplay">Replay</button><label class="sr-only" for="publicationSlider">Select year from 2000 to 2026</label><input id="publicationSlider" type="range" min="2000" max="2026" value="2000" step="1"><output id="publicationSliderYear">2000</output></div>
<p class="pub-source">Source: Scopus (Elsevier) · Retrieved 27 October 2026 · English journal articles and reviews.<br>Categories overlap. *2026 is partial / indexed as of retrieval; includes assigned publication years.</p>
<script id="publicationData" type="application/json">'''+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+'''</script></div>'''
