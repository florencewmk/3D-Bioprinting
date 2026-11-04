"""Render the "printing with light" slides 10–16 from tools/light-slides.html.

First run (52-slide deck): inserts the seven animated slides after the globe
(slide 9), moves the former slides 10–15 to the start of the technical backup
(after the "Technical backup" divider) and renumbers footers, menu links,
Contents, speaker notes, transcript and paper catalog. Later runs only re-render
the seven slides in place, so edit the template and rerun.

Reveals use the deck controller: each slide carries hidden `.ls-step` markers
with `data-reveal-step`; Up/Down/click reveal one marker per step and the slide
script mirrors that count into its animations.
"""
import html
import json
import re
from pathlib import Path

from deck_structure import write_transcript

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
TEMPLATE = ROOT / "tools/light-slides.html"
HULL_PNG = "materials/images/fb6bdf9f863889360d812cb9e338dba8ed28228d5a436b96f57f3c1a27db28b9.png"
HULL_MP4 = "materials/videos/02b7fdceac6d5959439932ab69a7fc3f00ca722f5345d877c86e04797df750f9.mp4"
SECTION = re.compile(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>.*?</section>', re.S)
DATA = re.compile(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', re.S)
FIRST = 10
REPLAY = {10, 12, 14, 16}
ORDER = [10, 14, 11, 12, 13, 15, 16]  # template ids in slide order (bioink & curing follows Hull)  # template slides with timed animations get the toolbar Replay button
MOVED = ["Bioprinting technologies", "A structure forms one layer at a time", "SLA · DLP · multiphoton lithography",
         "Four light-based curing routes", "UV / violet and NIR", "Thermal activation"]
NOTES = json.loads((ROOT / "tools/light-slides-notes.json").read_text())


def b64(path, mime):
    import base64
    return f"data:{mime};base64," + base64.b64encode((ROOT / path).read_bytes()).decode()


def parse_template():
    text = TEMPLATE.read_text()
    style = re.search(r'<style id="light-slides-style">.*?</style>', text, re.S)[0]
    script = re.search(r'<!--LS-SCRIPT-->\s*(<script>.*?</script>)', text, re.S)[1]
    chunks = re.findall(r'<!--LS (\d+) (\d+) ([^>]*?)-->\n(.*?)(?=\n<!--LS)', text, re.S)
    assert len(chunks) == 7, len(chunks)
    return style, script, [(int(n), int(steps), title, body) for n, steps, title, body in chunks]


def visible_text(body):
    body = re.sub(r'<(script|style)\b.*?</\1>', '', body, flags=re.S)
    body = re.sub(r'<(br|/p|/div|/h\d|/li|/tr|/text|/figcaption|/span)\b[^>]*>', '\n', body)
    lines = [html.unescape(re.sub(r'<[^>]+>', '', line)).strip() for line in body.splitlines()]
    out = []
    for line in lines:
        line = re.sub(r'\s+', ' ', line)
        if line and (not out or out[-1] != line):
            out.append(line)
    return "\n".join(out)


def nav(conclusion, printing=FIRST):
    return ('<nav class="section-nav" aria-label="Talk sections"><button data-goto="3" class="">Introduction</button>'
            f'<button data-goto="{printing}" class="current">Printing methods</button><button data-goto="{conclusion}" class="">'
            'Conclusion</button><span></span></nav>')


def render(total, conclusion, date, presenter, first=FIRST, printing=FIRST):
    style, script, chunks = parse_template()
    png, mp4 = b64(HULL_PNG, "image/png"), b64(HULL_MP4, "video/mp4")
    sections, records = [], []
    by_id = {c[0]: c for c in chunks}
    assert sorted(by_id) == sorted(ORDER)
    chunks = [by_id[n] for n in ORDER]
    for i, (n, steps, title, body) in enumerate(chunks):
        number = first + i  # template ids stay fixed; slide numbers follow ORDER and `first`
        body = body.replace("{{HULL_PNG}}", png).replace("{{HULL_MP4}}", mp4)
        markers = "".join(f'<i class="ls-step" data-reveal-step="{k}" aria-hidden="true" inert></i>' for k in range(1, steps + 1))
        text = visible_text(body)
        notes = NOTES[str(n)]
        sections.append(
            f'<section class="slide light-slide"{" data-replay" if n in REPLAY else ""} id="slide-{number}" aria-label="{number}. {html.escape(title, quote=True)}" aria-hidden="true">'
            + nav(conclusion, printing) + (style if i == 0 else "") + body + markers
            + f'<div class="sr-only">{html.escape(text)}</div><!-- Speaker notes: {html.escape(notes)} -->'
            + f'<footer><span>{date}</span><span>{presenter}</span><span>{number:02d} / {total}</span></footer>'
            + (script if i == len(chunks) - 1 else "") + '</section>')
        records.append({"number": number, "title": title, "text": text, "notes": notes})
    return sections, records


def restructure(document, data, settings):
    matches = list(SECTION.finditer(document))
    sections = [m[0] for m in matches]
    assert len(sections) == len(data) == 52, len(sections)
    assert [d["title"] for d in data[9:15]] == MOVED, [d["title"] for d in data[9:15]]
    assert data[28]["title"] == "Technical backup"
    order = [*range(1, 10), *[None] * 7, *range(16, 30), *range(10, 16), *range(30, 53)]
    total = len(order)
    renumber = {old: new for new, old in enumerate(order, 1) if old is not None}
    goto = lambda old: FIRST if old == FIRST else renumber[old]  # "Printing methods" now starts with the new slides
    conclusion = goto(next(s["slide"] for s in settings["sections"] if s["label"] == "Conclusion"))
    date, presenter = settings["event"]["date"], settings["presenter"]
    new_sections, new_records = render(total, conclusion, date, presenter)
    out_sections, out_data = [], []
    for number, old in enumerate(order, 1):
        if old is None:
            out_sections.append(new_sections[number - FIRST]); out_data.append(new_records[number - FIRST]); continue
        section, row = sections[old - 1], dict(data[old - 1])
        section = re.sub(r'id="slide-\d+"', f'id="slide-{number}"', section, count=1)
        section = re.sub(r'aria-label="\d+\. ', f'aria-label="{number}. ', section, count=1)
        section = re.sub(r'(data-goto=")(\d+)', lambda m: m[1] + str(goto(int(m[2]))), section)
        section = re.sub(r'<small>(\d+) →</small>', lambda m: f'<small>{goto(int(m[1])):02d} →</small>', section)
        section = re.sub(r'Page (\d+)', lambda m: f'Page {goto(int(m[1])):02d}', section)
        section = re.sub(r'<span>\d{2} / 52</span></footer>', f'<span>{number:02d} / {total}</span></footer>', section)
        row["number"] = number
        row["text"] = re.sub(r'Page (\d+)', lambda m: f'Page {goto(int(m[1])):02d}', row["text"])
        out_sections.append(section); out_data.append(row)
    document = document[:matches[0].start()] + "\n".join(out_sections) + document[matches[-1].end():]
    document = document.replace("52 slides", f"{total} slides").replace(
        "talk 1–23, references 24–28, technical backup 29–52",
        f"talk 1–{renumber[23]}, references {renumber[24]}–{renumber[28]}, technical backup {renumber[29]}–{total}")
    return document, out_data, renumber, goto, total


def rerender(document, data, settings):
    matches = list(SECTION.finditer(document))
    total = len(matches)
    first = next(i for i, m in enumerate(matches) if 'light-slide' in m[0].split('>', 1)[0])
    assert first == FIRST - 1
    conclusion = next(s["slide"] for s in settings["sections"] if s["label"] == "Conclusion")
    new_sections, new_records = render(total, conclusion, settings["event"]["date"], settings["presenter"])
    start, end = matches[first].start(), matches[first + 6].end()
    document = document[:start] + "\n".join(new_sections) + document[end:]
    data[first:first + 7] = new_records
    return document


def main():
    settings_path = ROOT / "presentation/settings.json"
    settings = json.loads(settings_path.read_text())
    document = DECK.read_text()
    data = json.loads(DATA.search(document)[2])
    if 'class="slide light-slide"' in document:
        document = rerender(document, data, settings)
    else:
        document, data, renumber, goto, total = restructure(document, data, settings)
        for item in settings["sections"]:
            item["slide"] = goto(item["slide"])
        settings["slide_count"] = total
        settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
        catalog_path = ROOT / "papers/catalog.json"
        catalog = json.loads(catalog_path.read_text())
        for ref in catalog.get("presentation_references", []):
            if isinstance(ref.get("reference_slide"), int):
                ref["reference_slide"] = renumber[ref["reference_slide"]]
        catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    document = DATA.sub(lambda m: m[1] + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + m[3], document, count=1)
    DECK.write_text(document)
    write_transcript(ROOT / "presentation/transcript.md", data)
    print(f"Rendered printing-with-light slides {FIRST}–{FIRST + 6}; deck has {len(data)} slides.")


if __name__ == "__main__":
    main()
