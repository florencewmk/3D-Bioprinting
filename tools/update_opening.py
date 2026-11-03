"""Apply settings/opening layouts while preserving scientific slide artwork.

Run from any directory: python3 tools/update_opening.py
"""
import html
import json
import re
from pathlib import Path
from cover_slide import render_cover
from opening_slides import settings, footer, navigation, render_introduction, render_contents, render_question
from deck_structure import write_transcript

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'presentation/index.html'
document = path.read_text()
pattern = r'(?:<!-- SLIDE[^>]*-->\s*)?<section\b[^>]*\bid="slide-(\d+)".*?</section>'
matches = list(re.finditer(pattern, document, re.S))
data_match = re.search(r'<script id="sourceData" type="application/json">(.*?)</script>', document, re.S)
data = json.loads(data_match[1])
c = settings()

if len(matches) == 50:
    # Restore the source's introduction at position 2 exactly once.
    sections = []
    for match in matches:
        n = int(match[1])
        section = match[0][match[0].index('<section'):]
        if n >= 2:
            section = section.replace(f'id="slide-{n}"', f'id="slide-{n + 1}"', 1)
            section = section.replace(f'aria-label="{n}. ', f'aria-label="{n + 1}. ', 1)
        sections.append(section)
    sections.insert(1, '<section class="slide profile-slide" id="slide-2" aria-label="2. Florence Mei Kuan Wong" aria-hidden="true"></section>')
    for row in data:
        if row['number'] >= 2:
            row['number'] += 1
    data.insert(1, {'number': 2, 'title': c['presenter'], 'text': '', 'notes': c['introduction']['notes']})
else:
    assert len(matches) == 51, 'Expected the current 50- or 51-slide deck'
    sections = [m[0][m[0].index('<section'):] for m in matches]

data[0]['text'] = f'{c["event"]["name"]} · {c["event"]["city"]} · {c["event"]["date"]}\n\nStereolithographic\n\nBioprinting\n\n{c["cover_tagline"]}\n\n{c["presenter"]}'
data[1].update(title=c['presenter'], text=c['presenter'] + '\n\n' + '\n\n'.join(c['introduction']['points']), notes=c['introduction']['notes'])
data[2]['text'] = 'Contents\n\n' + '\n\n'.join(f'{s["label"]} · Page {s["slide"]:02d}' for s in c['sections'])
data[3]['text'] = '\n'.join(c['opening_question']) + '\n\nBackground source: ' + c['opening_background']['source_url']

for i, section in enumerate(sections):
    number = i + 1
    section = re.sub(r'<nav class="section-nav".*?</nav>', '', section, flags=re.S)
    section = re.sub(r'<footer>.*?</footer>', '', section, flags=re.S)
    if number <= 4:
        opening = section.split('>', 1)[0] + '>'
        artwork = [render_cover, render_introduction, render_contents, render_question][i]()
        section = opening + artwork + '<div class="sr-only">' + html.escape(data[i]['text']) + '</div></section>'
    # References to event day change; historical source retrieval dates stay intact.
    section = section.replace('15 October 2026', c['event']['date'])
    if number > 2:
        at = section.index('>') + 1
        section = section[:at] + navigation(number) + section[at:]
    if number > 1:
        section = section.replace('</section>', footer(number) + '</section>')
    sections[i] = f'<!-- SLIDE {number:02d}: {html.escape(data[i]["title"])} -->\n' + section

start, end = matches[0].start(), matches[-1].end()
document = document[:start] + '\n'.join(sections) + document[end:]
data_match = re.search(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', document, re.S)
document = document[:data_match.start(2)] + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + document[data_match.end(2):]
document = document.replace('15 October 2026', c['event']['date']).replace('SOfE Berlin', 'SOfE Düsseldorf')
document = document.replace('50-slide presentation', '51-slide presentation').replace('50 slides', '51 slides')
description = f'Stereolithographic Bioprinting — {c["cover_tagline"]}. {c["event"]["name"]} · {c["event"]["city"]} · {c["event"]["date"]}. A 51-slide presentation by {c["presenter"]}.'
document = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + html.escape(description, quote=True) + '">', document, count=1)
document = document.replace('talk 1–22, references 23–27, technical backup 28–50', 'talk 1–23, references 24–28, technical backup 29–51')
css = (ROOT / 'tools/deck.css').read_text().rstrip()
a = document.index('/* === C: LIGHT-DEFINED LAYERS')
b = document.index('@media print', a)
b = document.index('\n', b)
document = document[:a] + css + document[b:]
start = document.index('/* === SOURCE DATA AND LOCAL TEXT EDITING === */')
end = document.index('</script>', start)
document = document[:start] + '\n'.join((ROOT / 'tools' / name).read_text() for name in ['deck.js', 'publication-chart.js', 'organ-chart.js']) + document[end:]
path.write_text(document)
write_transcript(ROOT / 'presentation/transcript.md', data)
print('Applied event settings, restored introduction, three-section navigation, and centered opening question; 51 slides.')
