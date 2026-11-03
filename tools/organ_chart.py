"""Data-driven organ-donation slide; bounds remain bounds, missing data remain null."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def render_organ_slide():
 data=json.loads((ROOT/'data/organ-transplants/annual_counts.json').read_text())
 return '''<div id="organChart">
<div class="organ-heading"><h1 class="editable" data-edit="organ-title">The organ shortage persists</h1><p>2015–2025</p></div>
<svg id="organPlot" viewBox="0 0 1330 615" role="img" aria-label="Annual organ transplant procedures and deceased donors, 2015 to 2025. 2025 figures are from Newsletter Transplant2026."></svg>
<aside class="organ-waiting" id="organWaiting"><h2>Organ-list entries <span>2025</span></h2><strong>532,905</strong><p>waiting at year-end</p><strong class="organ-deaths">40,019</strong><p>deaths on waiting lists</p></aside>
<div class="organ-legend"><span><i style="background:#e8c77b"></i>Organ transplants</span><span><i style="background:#e394ad"></i>Deceased donors</span></div>
<div class="organ-controls"><button id="organPlay" aria-label="Pause organ chart animation">Pause</button><button id="organReplay">Replay</button><label class="sr-only" for="organYearSlider">Select organ chart year</label><input id="organYearSlider" type="range" min="2015" max="2025" value="2015" step="1"><output id="organYearLabel" for="organYearSlider" aria-live="off">2015</output></div>
<p class="organ-status" id="organStatus" aria-live="polite">Annual report snapshot</p>
<p class="organ-source">Sources: WHO–ONT GODT annual reports (2015–2024); EDQM–ONT Newsletter Transplant 2026 (2025 data).</p>
<script id="organData" type="application/json">'''+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+'''</script></div>'''

def organ_metadata():
 text='The organ shortage persists\n2015–2025\nOrgan transplants and deceased donors\n2025:183,879 transplant procedures and49,169 deceased donors.\n2025 reported organ-list entries:532,905 waiting at year-end;40,019 deaths on waiting lists.'
 notes='Source: EDQM–ONT Newsletter Transplant2026, international figures2025, linked from WHO–ONT GODT. PDFp37(printed35): kidney116775, liver45556, heart10748, lung8472, pancreas2148, smallbowel180; sum183879. Actual deceased donors49169. PDFpp66–74(printed64–72): sum reported organ-list entries=532905 waiting at31December2025 and40019 deaths during2025. These are calculated sums across six organ lists and94country columns, not deduplicated patient counts. Missing cells remain missing; a multi-organ candidate may appear in several lists. Country coverage and report versions vary. No2026forecast. https://www.transplant-observatory.org/wp-content/uploads/2026/10/NEWSLETTER-2026_alta.pdf'
 return text,notes
