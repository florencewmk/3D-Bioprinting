"""Render the catalog's IEEE literature and video citations in the web deck."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_NUMBERS = {
    'Scientific references · 1': 24,
    'Scientific references · 2': 25,
    'Data and online sources · 1': 26,
    'Data and online sources · 2': 27,
    'Image references': 28,
}


def reference_groups(title, original_text, catalog):
    main = catalog['presentation_references']
    if title == 'Scientific references · 1':
        return [(None, [(r['number'], r['citation']) for r in main[:5]])]
    if title == 'Scientific references · 2':
        supporting = sorted(
            (d for d in catalog['documents'] + catalog.get('bibliography_only', [])
             if d.get('bibliography_number', 0) >= 25),
            key=lambda d: d['bibliography_number'],
        )
        return [
            (None, [(r['number'], r['citation']) for r in main[5:]]),
            ('Supporting literature', [
                (d['bibliography_number'], d['ieee_citation']) for d in supporting
            ]),
        ]

    source_text = re.split(r'\n\n(?:Web sources|YouTube videos)\n', original_text)[0]
    existing = [
        (int(number), citation.strip())
        for number, citation in re.findall(
            r'\[(\d+)\]\s*(.*?)(?=\[\d+\]|\Z)', source_text, re.S
        )
    ]
    if title != 'Data and online sources · 2':
        return [(None, existing)]

    # On a refresh, the transcript already includes the separately catalogued videos.
    existing = [(number, citation) for number, citation in existing if 16 <= number <= 19]
    videos = [
        (s['bibliography_number'], s['ieee_citation'])
        for s in catalog['source_links']
        if s.get('source_type') == 'online_video' and 'bibliography_number' in s
    ]
    web = sorted(
        (s['bibliography_number'], s['ieee_citation'])
        for s in catalog['source_links']
        if s.get('source_type') != 'online_video' and 'bibliography_number' in s
    )
    groups = [(None, existing)]
    if web:
        groups.append(('Web sources', web))
    return groups + [('YouTube videos', videos)]


def citation_html(citation):
    """Escape citation text, then render journal italics, DOI and URL links."""
    pattern = r'\*([^*]+)\*|doi: (10\.\S+?)\.(?=\s|$)|(https?://\S+)'
    result = []
    end = 0
    for match in re.finditer(pattern, citation):
        result.append(html.escape(citation[end:match.start()]))
        if match[1]:
            result.append(f'<em>{html.escape(match[1])}</em>')
        else:
            value = match[2] or match[3].rstrip('.,')
            url = f'https://doi.org/{value}' if match[2] else value
            label = f'doi: {value}' if match[2] else value
            suffix = '.' if match[2] else match[3][len(value):]
            result.append(
                f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">'
                f'{html.escape(label)}</a>{suffix}'
            )
        end = match.end()
    result.append(html.escape(citation[end:]))
    return ''.join(result)


def render_references(title, original_text, catalog):
    """Return slide HTML and a matching plain-text transcript."""
    source_number = SOURCE_NUMBERS[title]
    heading = original_text.splitlines()[0]
    groups = reference_groups(title, original_text, catalog)
    scrolls = len(groups) > 1
    wrapper = ('class="reference-list reference-scroll" tabindex="0" '
               'role="region" aria-label="Scrollable references"') if scrolls else 'class="reference-list"'
    hint = ''
    markup = [
        '<div class="references">',
        f'<p class="eyebrow">SOURCES · {source_number-23:02d} / 05{hint}</p>',
        f'<h1>{heading}</h1><div {wrapper}>',
    ]
    transcript = [heading, '']
    index = 0
    for label, citations in groups:
        if label:
            markup.append(f'<h2>{label}</h2>')
            transcript.extend(['', label, ''])
        for number, citation in citations:
            markup.append(
                f'<p class="editable" data-edit="ref-{source_number}-{index}">'
                f'[{number}] {citation_html(citation)}</p>'
            )
            transcript.append(f'[{number}] {citation.replace("*", "")}')
            index += 1
    return ''.join(markup) + '</div></div>', '\n'.join(transcript)


def update():
    """Refresh the reference slides without rebuilding the source deck."""
    catalog = json.loads((ROOT / 'papers/catalog.json').read_text())
    deck_path = ROOT / 'presentation/offline.html'
    transcript_path = ROOT / 'presentation/transcript.md'
    document = deck_path.read_text()
    transcript = transcript_path.read_text()
    pattern = r'(<script id="sourceData" type="application/json">)(.*?)(</script>)'
    data = json.loads(re.search(pattern, document, re.S)[2])
    changes = 0
    for row in data:
        if row['title'] not in SOURCE_NUMBERS:
            continue
        number = row['number']
        markup, text = render_references(row['title'], row['text'], catalog)
        row['text'] = text
        section = re.compile(rf'<section\b[^>]*\bid="slide-{number}".*?</section>', re.S)
        match = section.search(document)
        assert match, number
        body, count = re.subn(r'<div class="references">.*?</div></div>', lambda _: markup, match[0], count=1, flags=re.S)
        assert count == 1, number
        body, count = re.subn(r'<div class="sr-only">.*?</div>', lambda _: f'<div class="sr-only">{html.escape(text)}</div>', body, count=1, flags=re.S)
        assert count == 1, number
        document = document[:match.start()] + body + document[match.end():]
        block = rf'(^## {number:02d}\. [^\n]+\n\n).*?(?=^## |\Z)'
        transcript, count = re.subn(block, lambda m: m[1] + text + '\n\n', transcript, count=1, flags=re.M | re.S)
        assert count == 1, number
        changes += 1
    assert changes == len(SOURCE_NUMBERS)
    document = re.sub(pattern, lambda m: m[1] + json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + m[3], document, count=1, flags=re.S)
    deck_path.write_text(document)
    transcript_path.write_text(transcript)
    print(f'Refreshed {changes} reference slides and their transcripts.')


if __name__ == '__main__':
    update()
