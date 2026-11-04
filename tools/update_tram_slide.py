"""Insert or refresh the offline tram story after the presenter introduction."""
import html
import json
import re
from pathlib import Path

from deck_structure import write_transcript

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'materials/interactive/munich-tram-story.html'
DECK = ROOT / 'presentation/offline.html'
FRAME_CSS = '''
<style>
:root{background:transparent}body{padding:0;min-height:100vh}main{width:100%}
svg{border-radius:0}nav{display:none}
@media print{.scene{display:none!important}.scene[data-scenes="7"]{display:block!important;animation:none!important}#florence{display:none}}
</style>
'''
title = 'The tram encounter'
notes = ('Advance through eight cues. Introduce the crowded Saturday tram during Oktoberfest, '
         'let the jacket and holiday exchange play out, then pause on the courier’s age and the trip '
         'from Poland to the USA. End with the question about manufacturing living tissues and organs.')
story = SOURCE.read_text().replace('</head>', FRAME_CSS + '</head>', 1).replace(
    'show(0);\n</script>', '''window.tramStory = {
  reset: () => document.querySelector('#replay').click(),
  step(direction) {
    const index = beat + direction;
    if (index < 0 || index >= labels.length) return false;
    show(index);
    return true;
  }
};
show(0);
</script>''', 1)
section = (
    f'<!-- SLIDE 02: {title} -->\n'
    f'<section class="slide tram-story-slide" id="slide-2" aria-label="2. {title}" aria-hidden="true">'
    '<iframe class="tram-story-frame" title="Animated tram encounter" tabindex="-1" '
    'style="position:absolute;width:1728px;height:972px;left:96px;top:54px;border:0;pointer-events:none" '
    f'srcdoc="{html.escape(story, quote=True)}"></iframe></section>'
)
document = DECK.read_text()
if 'class="slide tram-story-slide"' in document:
    document = re.sub(r'<!-- SLIDE 02: The tram encounter -->\n<section\b.*?</section>',
                      lambda _: section, document, count=1, flags=re.S)
else:
    pattern = r'(<!-- SLIDE )(\d+)(:.*?-->\s*<section\b.*?</section>)'

    total = len(re.findall(pattern, document, flags=re.S))

    def renumber(match):
        number = int(match[2])
        new = number + (number >= 2)
        body = match[3].replace(f'id="slide-{number}"', f'id="slide-{new}"', 1)
        body = body.replace(f'aria-label="{number}. ', f'aria-label="{new}. ', 1)
        body = re.sub(r'data-goto="(\d+)"', lambda m: f'data-goto="{int(m[1])+1}"', body)
        body = re.sub(r'<small>(\d+) →</small>', lambda m: f'<small>{int(m[1])+1:02} →</small>', body)
        body = re.sub(r' · Page (\d+)', lambda m: f' · Page {int(m[1])+1:02}', body)
        body = body.replace(f'{number:02} / {total}</span>', f'{new:02} / {total+1}</span>')
        return f'{match[1]}{new:02}{body}'

    document, count = re.subn(pattern, renumber, document, flags=re.S)
    assert count in (51, 53), count
    document = document.replace('<!-- SLIDE 03: 3D-Bioprinting -->',
                                section + '\n<!-- SLIDE 03: 3D-Bioprinting -->', 1)
    assert 'class="slide tram-story-slide"' in document
    match = re.search(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', document, re.S)
    rows = json.loads(match[2])
    rows.insert(1, dict(number=2, title=title, text='Munich tram encounter · Poland to USA', notes=notes))
    for number, row in enumerate(rows, 1):
        row['number'] = number
        if row['title'] == 'Contents':
            row['text'] = re.sub(r' · Page (\d+)', lambda m: f' · Page {int(m[1])+1:02}', row['text'])
    document = document[:match.start(2)] + json.dumps(rows, ensure_ascii=False).replace('</', '<\\/') + document[match.end(2):]
    write_transcript(ROOT / 'presentation/transcript.md', rows)
DECK.write_text(document)
