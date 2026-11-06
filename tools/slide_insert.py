"""Shared helpers for generator scripts that add one slide to the talk.

insert_or_rerender(cls, after_title, render, title, text, notes):
  * first run: inserts the section returned by render(number, conclusion, printing)
    right after the slide titled `after_title`, then renumbers every later slide
    (ids, aria labels, footers, menu links, settings sections and slide_count,
    talk/reference ranges, catalog reference slides, speaker-notes.json keys,
    transcript);
  * later runs: re-renders the existing `<section class="slide {cls} …">` in place.
Also makes sure `.canvas-step-slide` is one of the deck controller's reveal selectors,
so hidden `[data-reveal-step]` markers on such slides step with Left/Right/click.
Same logic as tools/vessel_slide.py, which predates this module.
"""
import json
import re
from pathlib import Path

from deck_structure import write_transcript

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
SECTION = re.compile(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>.*?</section>', re.S)
DATA = re.compile(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', re.S)
SELECTOR_ANCHOR = ".publication-slide,.vessel-slide'"
SELECTOR_NEW = ".publication-slide,.vessel-slide,.canvas-step-slide'"


def nav(conclusion, printing, current):
    cls = lambda name: ' class="current"' if name == current else ' class=""'
    return ('<nav class="section-nav" aria-label="Talk sections">'
            f'<button data-goto="2"{cls("Introduction")}>Introduction</button>'
            f'<button data-goto="{printing}"{cls("Printing methods")}>Printing methods</button>'
            f'<button data-goto="{conclusion}"{cls("Conclusion")}>Conclusion</button><span></span></nav>')


def _section_slide(settings, label):
    return next(s["slide"] for s in settings["sections"] if s["label"] == label)


def _insert(document, data, settings, after_title, render, row):
    titles = [r["title"] for r in data]
    at = titles.index(after_title) + 2
    matches = list(SECTION.finditer(document))
    shift = lambda n: n + 1 if n >= at else n
    conclusion, printing = shift(_section_slide(settings, "Conclusion")), shift(_section_slide(settings, "Printing methods"))
    sections, rows = [], []
    for i, m in enumerate(matches):
        old, sec = i + 1, m[0]
        new = shift(old)
        sec = re.sub(r'id="slide-\d+"', f'id="slide-{new}"', sec, count=1)
        sec = re.sub(r'aria-label="\d+\. ', f'aria-label="{new}. ', sec, count=1)
        sec = re.sub(r'(data-goto=")(\d+)', lambda g: g[1] + str(shift(int(g[2]))), sec)
        sec = re.sub(r'<span>\d+</span></footer>', f'<span>{new}</span></footer>', sec)
        r = dict(data[i]); r["number"] = new
        if old == at:
            sections.append(render(at, conclusion, printing)); rows.append({"number": at, **row})
        sections.append(sec); rows.append(r)
    if at == len(matches) + 1:
        sections.append(render(at, conclusion, printing)); rows.append({"number": at, **row})
    document = document[:matches[0].start()] + "\n".join(sections) + document[matches[-1].end():]
    total = len(rows)
    ref = [r["title"] for r in rows].index("Scientific references · 1") + 1
    document = re.sub(r'talk 1–\d+, references \d+–\d+', f'talk 1–{ref - 1}, references {ref}–{total}', document)
    labels = re.compile(r"\$\{i<\d+\?'TALK':i<\d+\?'REFERENCES':'BACKUP'\}")
    new_labels = f"${{i<{ref - 1}?'TALK':i<{total}?'REFERENCES':'BACKUP'}}"
    document = labels.sub(lambda _: new_labels, document)
    js = ROOT / "tools/deck.js"
    js.write_text(labels.sub(lambda _: new_labels, js.read_text()))
    for item in settings["sections"]:
        item["slide"] = shift(item["slide"])
    settings["slide_count"] = total
    catalog_path = ROOT / "papers/catalog.json"
    catalog = json.loads(catalog_path.read_text())
    for r in catalog.get("presentation_references", []):
        if isinstance(r.get("reference_slide"), int):
            r["reference_slide"] = shift(r["reference_slide"])
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    notes_path = ROOT / "presentation/speaker-notes.json"
    notes = json.loads(notes_path.read_text())
    out = {(str(shift(int(k))) if k.isdigit() else k): v for k, v in notes.items()}
    out[str(at)] = row["notes"]
    ordered = {k: out[k] for k in sorted(out, key=lambda k: (k.isdigit(), int(k) if k.isdigit() else 0))}
    notes_path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n")
    return document, rows


def _add_selector(path):
    text = path.read_text()
    if SELECTOR_NEW not in text:
        assert SELECTOR_ANCHOR in text, path
        path.write_text(text.replace(SELECTOR_ANCHOR, SELECTOR_NEW))


def insert_or_rerender(cls, after_title, render, title, text, notes):
    settings_path = ROOT / "presentation/settings.json"
    settings = json.loads(settings_path.read_text())
    document = DECK.read_text()
    data = json.loads(DATA.search(document)[2])
    row = {"title": title, "text": text, "notes": notes}
    m = re.search(rf'<section class="slide [^"]*\b{re.escape(cls)}\b[^"]*" id="slide-(\d+)".*?</section>', document, re.S)
    if m:
        number = int(m[1])
        document = document[:m.start()] + render(number, _section_slide(settings, "Conclusion"),
                                                 _section_slide(settings, "Printing methods")) + document[m.end():]
        for r in data:
            if r["number"] == number:
                r.update(row)
    else:
        document, data = _insert(document, data, settings, after_title, render, row)
        settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
    document = DATA.sub(lambda g: g[1] + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + g[3], document, count=1)
    DECK.write_text(document)
    _add_selector(DECK)
    _add_selector(ROOT / "tools/deck.js")
    write_transcript(ROOT / "presentation/transcript.md", data)
    return len(data)
