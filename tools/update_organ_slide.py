"""Update organ slide only; preserve other sections, global motion and pending edits."""
from pathlib import Path
import re,json
from organ_chart import render_organ_slide,organ_metadata
ROOT=Path(__file__).resolve().parents[1];TOOLS=Path(__file__).parent;p=ROOT/'presentation/index.html';old=p.read_text();pattern=r'<section\b[^>]*\bid="slide-(\d+)".*?</section>'
m=next(m for m in re.finditer(pattern,old,re.S) if 'id="organChart"' in m.group());number=int(m[1]);section=m.group();opening=section.split('>',1)[0]+'>';nav=re.search(r'<nav class="section-nav".*?</nav>',section,re.S).group();footer=re.search(r'<footer>.*?</footer>',section,re.S).group()
new=old[:m.start()]+opening+nav+render_organ_slide()+footer+'</section>'+old[m.end():]
start=new.index('/* === ORGAN_CHART_SCRIPT_BEGIN === */');end=new.index('/* === ORGAN_CHART_SCRIPT_END === */',start)+len('/* === ORGAN_CHART_SCRIPT_END === */');new=new[:start]+(TOOLS/'organ-chart.js').read_text().rstrip()+new[end:]
match=re.search(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)',new,re.S);data=json.loads(match.group(2));text,notes=organ_metadata();data[number-1]['text']=text;data[number-1]['notes']=notes;new=new[:match.start(2)]+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+new[match.end(2):]
a={m.group(1):m.group() for m in re.finditer(pattern,old,re.S)};b={m.group(1):m.group() for m in re.finditer(pattern,new,re.S)};assert len(b)==len(a);assert all(a[k]==b[k] for k in a if k!=str(number));p.write_text(new)
t=ROOT/'presentation/transcript.md'
if t.exists():
 s=t.read_text();pat=r'## '+f'{number:02d}'+r'\. The organ shortage persists\n.*?(?=\n## \d|\Z)';s,n=re.subn(pat,lambda m:f'## {number:02d}. The organ shortage persists\n\n{text}\n\n### Speaker notes\n\n{notes}\n',s,flags=re.S);assert n==1;t.write_text(s)
print(f'Organ slide{number} updated; other{len(a)-1}slide sections unchanged')
