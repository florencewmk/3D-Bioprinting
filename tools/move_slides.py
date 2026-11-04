"""Move slides to a new order and renumber everything that refers to slide numbers.

Usage: python3 tools/move_slides.py 1 3 4 5 2 6-60
List every current slide number once, in the new order (ranges like 6-60 allowed).
Updates slide ids, aria labels, footers, data-goto links, Contents page numbers,
speaker data, transcript, settings sections and paper catalog reference slides.
The talk / references / backup boundaries move with their divider slides.
"""
import json
import re
import sys
from pathlib import Path

from deck_structure import write_transcript

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
SECTION = re.compile(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>.*?</section>', re.S)
DATA = re.compile(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', re.S)


def parse(args):
    order = []
    for arg in args:
        a, _, b = arg.partition("-")
        order += list(range(int(a), int(b) + 1)) if b else [int(a)]
    return order


def main(order):
    document = DECK.read_text()
    matches = list(SECTION.finditer(document))
    data = json.loads(DATA.search(document)[2])
    total = len(matches)
    assert total == len(data) and sorted(order) == list(range(1, total + 1)), "list every slide exactly once"
    new_of = {old: new for new, old in enumerate(order, 1)}
    sections, rows = [], []
    for new, old in enumerate(order, 1):
        section, row = matches[old - 1][0], dict(data[old - 1])
        section = re.sub(r'id="slide-\d+"', f'id="slide-{new}"', section, count=1)
        section = re.sub(r'aria-label="\d+\. ', f'aria-label="{new}. ', section, count=1)
        section = re.sub(r'(data-goto=")(\d+)', lambda m: m[1] + str(new_of[int(m[2])]), section)
        section = re.sub(r'<small>(\d+) →</small>', lambda m: f'<small>{new_of[int(m[1])]:02d} →</small>', section)
        section = re.sub(r'Page (\d+)', lambda m: f'Page {new_of[int(m[1])]:02d}', section)
        section = re.sub(rf'<span>\d+ / {total}</span></footer>', f'<span>{new:02d} / {total}</span></footer>', section)
        row["number"] = new
        row["text"] = re.sub(r'Page (\d+)', lambda m: f'Page {new_of[int(m[1])]:02d}', row["text"])
        sections.append(section)
        rows.append(row)
    document = document[:matches[0].start()] + "\n".join(sections) + document[matches[-1].end():]
    document = DATA.sub(lambda m: m[1] + json.dumps(rows, ensure_ascii=False).replace('</', '<\\/') + m[3], document, count=1)
    # talk / references / backup boundaries follow the first reference slide and the backup divider
    titles = [r["title"] for r in rows]
    ref_start = titles.index("Scientific references · 1") + 1
    backup_start = titles.index("Technical backup") + 1
    document = re.sub(r'talk 1–\d+, references \d+–\d+, technical backup \d+–\d+',
                      f'talk 1–{ref_start - 1}, references {ref_start}–{backup_start - 1}, technical backup {backup_start}–{total}', document)
    labels = re.compile(r"\$\{i<\d+\?'TALK':i<\d+\?'REFERENCES':'BACKUP'\}")
    new_labels = f"${{i<{ref_start - 1}?'TALK':i<{backup_start - 1}?'REFERENCES':'BACKUP'}}"
    document = labels.sub(lambda _: new_labels, document)
    DECK.write_text(document)
    js = ROOT / "tools/deck.js"
    js.write_text(labels.sub(lambda _: new_labels, js.read_text()))
    write_transcript(ROOT / "presentation/transcript.md", rows)
    settings_path = ROOT / "presentation/settings.json"
    settings = json.loads(settings_path.read_text())
    for item in settings["sections"]:
        item["slide"] = new_of[item["slide"]]
    settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
    catalog_path = ROOT / "papers/catalog.json"
    catalog = json.loads(catalog_path.read_text())
    for ref in catalog.get("presentation_references", []):
        if isinstance(ref.get("reference_slide"), int):
            ref["reference_slide"] = new_of[ref["reference_slide"]]
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    print("Moved:", ", ".join(f"{new}←{old}" for new, old in enumerate(order, 1) if new != old))


if __name__ == "__main__":
    main(parse(sys.argv[1:]))
