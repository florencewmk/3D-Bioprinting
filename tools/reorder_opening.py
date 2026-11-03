"""Place the printing examples and organ question before the title card; place Contents in backup."""
import json
import re
from pathlib import Path

from deck_structure import write_transcript

QUESTION = "What if we could print organs?"
SECTION = re.compile(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>.*?</section>', re.S)
DATA = re.compile(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', re.S)


def reorder(document):
    matches = list(SECTION.finditer(document))
    data_match = DATA.search(document)
    data = json.loads(data_match[2])
    assert len(matches) == len(data) == 51
    sections = [m[0] for m in matches]
    assert 'examples-slide' in sections[5].split('>', 1)[0]
    assert 'cover-slide' in sections[3].split('>', 1)[0]

    question = sections[2]
    question = re.sub(r'(<div class="question-center"><h1[^>]*>).*?(</h1>)',
                      lambda m: m[1].replace('opening-centered-question', 'organ-centered-question')
                      + QUESTION + m[2], question, count=1, flags=re.S)
    question = re.sub(r'<div class="sr-only">.*?</div>', '', question, flags=re.S)
    question = re.sub(r'<!-- Speaker notes:.*?-->', '', question, flags=re.S)
    question = question.replace('3. What comes to your mind?', f'5. {QUESTION}', 1)
    question = question.replace('id="slide-3"', 'id="slide-5"', 1)

    sections[5] = re.sub(r'<div class="examples-copy" data-example="3".*?</div>',
                         '', sections[5], count=1, flags=re.S)
    sections[5] = re.sub(r'\n\nSo far, we’ve been talking.*?(?= -->|-->)',
                         '', sections[5], count=1, flags=re.S)
    data[5]['text'] = data[5]['text'].split('\n\nBioprinting\n')[0]
    intro, transition = data[5]['notes'].rsplit('\n\n', 1)
    data[5]['notes'] = intro
    question_data = {'title': QUESTION, 'text': QUESTION, 'notes': transition}

    order = [1, 2, 3, 6, None, 4, 9, 8, 7, *range(10, 52), 5]
    renumber = {old: new for new, old in enumerate(order, 1) if old is not None}
    updated_sections = []
    updated_data = []
    for number, old in enumerate(order, 1):
        section = question if old is None else sections[old - 1]
        row = question_data if old is None else data[old - 1]
        section = re.sub(r'id="slide-\d+"', f'id="slide-{number}"', section, count=1)
        section = re.sub(r'aria-label="\d+\. ', f'aria-label="{number}. ', section, count=1)
        section = re.sub(r'(data-goto=")(\d+)', lambda m: m[1]+str(renumber[int(m[2])]), section)
        section = re.sub(r'<small>(\d+) →</small>',
                         lambda m: f'<small>{renumber[int(m[1])]:02d} →</small>', section)
        section = re.sub(r'<span>\d{2} / 51</span>', f'<span>{number:02d} / 52</span>', section)
        row['number'] = number
        if old == 5:
            section = re.sub(r'Page (\d+)', lambda m: f'Page {renumber[int(m[1])]:02d}', section)
            row['text'] = re.sub(r'Page (\d+)', lambda m: f'Page {renumber[int(m[1])]:02d}', row['text'])
        updated_sections.append(section)
        updated_data.append(row)
    document = document[:matches[0].start()] + '\n'.join(updated_sections) + document[matches[-1].end():]
    document = DATA.sub(lambda m: m[1] + json.dumps(updated_data, ensure_ascii=False).replace('</', '<\\/') + m[3], document, count=1)
    document = document.replace('51 slides', '52 slides').replace('talk 1–23, references 24–28, technical backup 29–51',
                                                                  'talk 1–23, references 24–28, technical backup 29–52')
    return document, updated_data


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1] / 'presentation'
    deck = root / 'index.html'
    document, records = reorder(deck.read_text())
    deck.write_text(document)
    write_transcript(root / 'transcript.md', records)
