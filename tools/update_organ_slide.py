"""Replace slide8 only, retaining all other sections and the publication controller."""
from pathlib import Path
import re,json
from organ_chart import render_organ_slide
ROOT=Path(__file__).resolve().parents[1];TOOLS=Path(__file__).parent;p=ROOT/'presentation/index.html';old=p.read_text();pattern=r'<section\b[^>]*\bid="slide-(\d+)".*?</section>'
m=re.search(r'<section\b[^>]*\bid="slide-8".*?</section>',old,re.S);assert m
s=m.group();opening=s.split('>',1)[0]+'>';nav=re.search(r'<nav class="section-nav".*?</nav>',s,re.S).group();footer=re.search(r'<footer>.*?</footer>',s,re.S).group()
new=old[:m.start()]+opening+nav+render_organ_slide()+footer+'</section>'+old[m.end():]
new=re.sub(r'/\* === ORGAN_CHART_STYLE_BEGIN === \*/.*?/\* === ORGAN_CHART_STYLE_END === \*/\s*','',new,flags=re.S)
new=new.replace('</style>',(TOOLS/'organ-chart.css').read_text()+'\n</style>',1)
start=new.index('/* === SOURCE DATA AND LOCAL TEXT EDITING === */');end=new.index('</script>',start)
new=new[:start]+(TOOLS/'deck.js').read_text()+'\n'+(TOOLS/'publication-chart.js').read_text()+'\n'+(TOOLS/'organ-chart.js').read_text()+new[end:]
# Update notes and transcript, which the presentation reads from embedded sourceData.
match=re.search(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)',new,re.S);data=json.loads(match.group(2));data[7]['text']='The organ shortage persists\nReported international activity · 2015–2025\nOrgan transplant procedures and actual deceased donors\n2025: >183,800 procedures; 49,169 deceased donors (homepage highlights; full report not verified)\nKidney waiting lists, 2024: 377,902 waiting at year-end; 19,936 deaths.'
data[7]['notes']='Reported international activity, 2015–2024 annual report snapshots plus 2025 GODT homepage highlights. The 2025 transplant exact count is not verified: the homepage reports MORE THAN 183,800, shown as an open lower-bound marker and dashed connection. 49,169 actual deceased donors are listed for 2025. Homepage fields are internally inconsistent and a complete annual report has not been verified. Kidney waiting figures remain 2024 only (377,902 waiting, 19,936 deaths). Country/indicator coverage varies; transplants count organ procedures, not unique patients. Sources and definitions: data/organ-transplants/README.md and annual_counts.json. https://data.transplant-observatory.org/ ; https://www.transplant-observatory.org/wp-content/uploads/2025/12/2024-data-global-report.pdf (PDF p65).'
new=new[:match.start(2)]+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+new[match.end(2):]
a={m.group(1):m.group() for m in re.finditer(pattern,old,re.S)};b={m.group(1):m.group() for m in re.finditer(pattern,new,re.S)};assert len(b)==50;assert all(a[k]==b[k] for k in a if k!='8');p.write_text(new);print('Slide8 updated; other49slide sections byte-identical')
