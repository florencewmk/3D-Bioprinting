"""Data-driven slide 7. Missing annual counts remain null, never observed zeros."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1]
def render_publication_slide():
 data=json.loads((ROOT/'data/publication-trends/annual_counts.json').read_text())
 return '''<div class="publication-chart" id="publicationChart">
<div class="pub-heading"><h1 class="editable" data-edit="pub-title">Bioprinting publications</h1><p>Annual keyword matches · Web of Science Core Collection</p></div>
<svg id="publicationPlot" viewBox="0 0 1450 620" role="img" aria-label="Annual publication category matches, 2000–2026. Values after 2023 are not verified."></svg>
<aside class="pub-year-panel" aria-label="Selected year counts"><p class="pub-small">SELECTED YEAR</p><output id="publicationYear">2000</output><p class="pub-year-status" id="publicationStatus">Historical snapshot</p><div id="publicationCounts"></div><div class="pub-total"><span>Category matches</span><strong id="publicationTotal">0</strong></div></aside>
<div class="pub-legend" id="publicationLegend"></div>
<div class="pub-timeline" aria-label="Publication animation controls"><button id="publicationPlay" aria-label="Play yearly animation">Pause</button><button id="publicationReplay">Replay</button><label class="sr-only" for="publicationSlider">Select year from 2000 to 2026</label><input id="publicationSlider" type="range" min="2000" max="2026" value="2000" step="1"><output id="publicationSliderYear">2000</output></div>
<p class="pub-source">Retrieved 14 October 2026 · Frozen institutional snapshot; recent years may be incomplete.<br>Categories overlap. Shaded 2024–2026: not verified. 2026 requires a dated year-to-date count.</p>
<script id="publicationData" type="application/json">'''+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+'''</script></div>'''
