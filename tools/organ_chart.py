"""Data-driven organ-donation slide; bounds remain bounds, missing data remain null."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def render_organ_slide():
 data=json.loads((ROOT/'data/organ-transplants/annual_counts.json').read_text())
 return '''<div id="organChart">
<div class="organ-heading"><h1 class="editable" data-edit="organ-title">The organ shortage persists</h1><p>All six solid-organ categories · 2015–2025</p></div>
<svg id="organPlot" viewBox="0 0 1330 615" role="img" aria-label="Annual organ transplant procedures and deceased donors, 2015 to 2025. The 2025 transplant figure is a lower bound from homepage highlights."></svg>
<aside class="organ-waiting" id="organWaiting"><h2>Kidney only <span>Waiting lists · 2024</span></h2><strong>377,902</strong><p>still waiting at year-end</p><strong class="organ-deaths">19,936</strong><p>died while on the waiting list</p><small>Reporting countries · kidney only<br>2025 waiting-list data not verified</small></aside>
<div class="organ-legend"><span><i style="background:#e8c77b"></i>Organ transplants</span><span><i style="background:#e394ad"></i>Deceased donors</span><small>Kidney, liver, heart, lung, pancreas &amp; small bowel · Includes living donation</small></div>
<div class="organ-controls"><button id="organPlay" aria-label="Pause organ chart animation">Pause</button><button id="organReplay">Replay</button><label class="sr-only" for="organYearSlider">Select organ chart year</label><input id="organYearSlider" type="range" min="2015" max="2025" value="2015" step="1"><output id="organYearLabel" for="organYearSlider" aria-live="off">2015</output></div>
<p class="organ-status" id="organStatus" aria-live="polite">Annual report snapshot</p>
<p class="organ-source">Source: WHO–ONT GODT · Annual reports 2015–2024; 2025 homepage highlights, full report not verified.<br>Coverage varies. Transplants are procedures, not unique recipients. Dashed 2025 point marks a reported lower bound.</p>
<script id="organData" type="application/json">'''+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+'''</script></div>'''
