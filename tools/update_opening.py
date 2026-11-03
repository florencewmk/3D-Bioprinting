"""Apply introduction-first openings and shared settings, retaining later slides."""
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
assert len(matches) >= 4, 'Opening slides are missing'
sections = [m[0][m[0].index('<section'):] for m in matches]
data_match = re.search(r'<script id="sourceData" type="application/json">(.*?)</script>', document, re.S)
data = json.loads(data_match[1])
c = settings()
if 'profile-slide' in sections[1].split('>', 1)[0]:
    sections[0], sections[1] = sections[1], sections[0]
    data[0], data[1] = data[1], data[0]
assert 'profile-slide' in sections[0].split('>', 1)[0], 'Expected the presenter introduction among the first two slides'
for i, row in enumerate(data, 1):
    row['number'] = i

heading = c['introduction'].get('heading', c['presenter'])
data[0].update(title=heading, text=heading + '\n\n' + '\n\n'.join(c['introduction']['points']), notes=c['introduction']['notes'])
data[1]['text'] = f'{c["event"]["name"]} · {c["event"]["city"]} · {c["event"]["date"]}\n\nStereolithographic\n\nBioprinting\n\n{c["cover_tagline"]}\n\n{c["presenter"]}'
data[2]['text'] = 'Contents\n\n' + '\n\n'.join(f'{s["label"]} · Page {s["slide"]:02d}' for s in c['sections'])
data[3]['text'] = '\n'.join(c['opening_question']) + '\n\nBackground source: ' + c['opening_background']['source_url']
renderers = [render_introduction, render_cover, render_contents, render_question]
for i, section in enumerate(sections):
    number = i + 1
    if number <= 4:
        classes = ['slide active visible profile-slide', 'slide poster-slide cover-slide', 'slide poster-slide', 'slide poster-slide'][i]
        opening = f'<section class="{classes}" id="slide-{number}" aria-label="{number}. {html.escape(data[i]["title"])}" aria-hidden="{str(number != 1).lower()}">'
        if number > 2:
            opening = section.split('>', 1)[0] + '>'
        # Screen-reader content follows click reveals too; full transcript stays in sourceData.
        transcript = heading if number == 1 else data[i]['text']
        section = opening + renderers[i]() + '<div class="sr-only">' + html.escape(transcript) + '</div></section>'
        if number > 2:
            at = section.index('>') + 1
            section = section[:at] + navigation(number) + section[at:]
        if number != 2:
            section = section.replace('</section>', footer(number) + '</section>')
    sections[i] = f'<!-- SLIDE {number:02d}: {html.escape(data[i]["title"])} -->\n' + section

start, end = matches[0].start(), matches[-1].end()
document = document[:start] + '\n'.join(sections) + document[end:]
data_match = re.search(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', document, re.S)
document = document[:data_match.start(2)] + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + document[data_match.end(2):]
css = (ROOT / 'tools/deck.css').read_text().rstrip()
a = document.index('/* === C: LIGHT-DEFINED LAYERS')
b = document.index('@media print', a)
b = document.index('\n', b)
document = document[:a] + css + document[b:]
start = document.index('/* === SOURCE DATA AND LOCAL TEXT EDITING === */')
end = document.index('</script>', start)
# Reuse any optional runtime modules, such as the independent history work.
runtime = ['deck.js', 'publication-chart.js', 'organ-chart.js']
if (ROOT / 'tools/history.js').exists():
    runtime.append('history.js')
document = document[:start] + '\n'.join((ROOT / 'tools' / name).read_text() for name in runtime) + document[end:]
path.write_text(document)
write_transcript(ROOT / 'presentation/transcript.md', data)
print(f'Applied introduction-first opening, natural photo proportions, and click reveals; {len(data)} slides.')
