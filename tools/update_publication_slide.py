"""Update only slide 7 and its CSS/controller in an existing single-file deck.
Other slide sections are checked byte-for-byte unchanged.
"""
from pathlib import Path
import re
from publication_chart import render_publication_slide
ROOT=Path(__file__).resolve().parents[1];TOOLS=Path(__file__).parent
path=ROOT/'presentation/index.html';old=path.read_text()
pattern=r'<section\b[^>]*\bid="slide-(\d+)".*?</section>'

match=re.search(r'<section\b[^>]*\bid="slide-7".*?</section>',old,re.S)
if not match:raise SystemExit('Slide 7 not found')
section=match.group();opening=section.split('>',1)[0]+'>'
nav=re.search(r'<nav class="section-nav".*?</nav>',section,re.S).group()
footer=re.search(r'<footer>.*?</footer>',section,re.S).group()
transcript=re.search(r'<div class="sr-only">.*',section,re.S).group() if '<div class="sr-only">' in section else '</section>'
new=old[:match.start()]+opening+nav+render_publication_slide()+footer+transcript+old[match.end():]
css='/* === PUBLICATION_CHART_STYLE_BEGIN === */\n'+(TOOLS/'publication-chart.css').read_text()+'\n/* === PUBLICATION_CHART_STYLE_END === */'
new=re.sub(r'/\* === PUBLICATION_CHART_STYLE_BEGIN === \*/.*?/\* === PUBLICATION_CHART_STYLE_END === \*/','',new,flags=re.S)
new=new.replace('</style>',css+'\n</style>',1)
script_start=new.index('/* === SOURCE DATA AND LOCAL TEXT EDITING === */');script_end=new.index('</script>',script_start)
new=new[:script_start]+(TOOLS/'deck.js').read_text()+'\n'+(TOOLS/'publication-chart.js').read_text()+'\n'+(TOOLS/'organ-chart.js').read_text()+new[script_end:]
updated=re.findall(pattern,new,re.S)
assert len(updated)==50
# Match complete individual sections rather than captures of section content.
a={m.group(1):m.group() for m in re.finditer(pattern,old,re.S)};b={m.group(1):m.group() for m in re.finditer(pattern,new,re.S)}
assert all(a[k]==b[k] for k in a if k!='7'),'Unexpected change to a slide other than 7'
path.write_text(new)
print('Updated slide 7; all other 49 slide sections unchanged')
