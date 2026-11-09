"""Delete slides and renumber everything that refers to slide numbers.

Usage: python3 tools/delete_slides.py 2-4
Links to a deleted slide go to the next remaining slide.
"""
import json
import re
import sys
from pathlib import Path

from deck_structure import write_transcript
from move_slides import DATA, DECK, ROOT, SECTION, parse


def main(drop):
    document = DECK.read_text()
    matches = list(SECTION.finditer(document))
    data = json.loads(DATA.search(document)[2])
    total = len(matches)
    assert total == len(data)
    keep = [n for n in range(1, total + 1) if n not in set(drop)]
    new_total = len(keep)
    new_of = {}
    for old in range(total, 0, -1):
        new_of[old] = keep.index(old) + 1 if old in keep else new_of.get(old + 1, new_total)
    sections, rows = [], []
    for new, old in enumerate(keep, 1):
        section, row = matches[old - 1][0], dict(data[old - 1])
        section = re.sub(r'id="slide-\d+"', f'id="slide-{new}"', section, count=1)
        section = re.sub(r'aria-label="\d+\. ', f'aria-label="{new}. ', section, count=1)
        section = re.sub(r'(data-goto=")(\d+)', lambda m: m[1] + str(new_of[int(m[2])]), section)
        section = re.sub(r'<small>(\d+) →</small>', lambda m: f'<small>{new_of[int(m[1])]:02d} →</small>', section)
        section = re.sub(r'Page (\d+)', lambda m: f'Page {new_of[int(m[1])]:02d}', section)
        section = re.sub(rf'<span>\d+ / {total}</span></footer>', f'<span>{new:02d} / {new_total}</span></footer>', section)
        row["number"] = new
        row["text"] = re.sub(r'Page (\d+)', lambda m: f'Page {new_of[int(m[1])]:02d}', row["text"])
        sections.append(section)
        rows.append(row)
    document = document[:matches[0].start()] + "\n".join(sections) + document[matches[-1].end():]
    document = DATA.sub(lambda m: m[1] + json.dumps(rows, ensure_ascii=False).replace('</', '<\\/') + m[3], document, count=1)
    titles = [r["title"] for r in rows]
    ref_start = titles.index("Scientific references · 1") + 1
    document = re.sub(r'talk 1–\d+, references \d+–\d+', f'talk 1–{ref_start - 1}, references {ref_start}–{new_total}', document)
    labels = re.compile(r"\$\{i<\d+\?'TALK':i<\d+\?'REFERENCES':'BACKUP'\}")
    new_labels = f"${{i<{ref_start - 1}?'TALK':i<{new_total}?'REFERENCES':'BACKUP'}}"
    document = labels.sub(lambda _: new_labels, document)
    DECK.write_text(document)
    js = ROOT / "tools/deck.js"
    js.write_text(labels.sub(lambda _: new_labels, js.read_text()))
    write_transcript(ROOT / "presentation/transcript.md", rows)
    settings_path = ROOT / "presentation/settings.json"
    settings = json.loads(settings_path.read_text())
    for item in settings["sections"]:
        item["slide"] = new_of[item["slide"]]
    if "slide_count" in settings:
        settings["slide_count"] = new_total
    settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
    catalog_path = ROOT / "papers/catalog.json"
    catalog = json.loads(catalog_path.read_text())
    for ref in catalog.get("presentation_references", []):
        if isinstance(ref.get("reference_slide"), int):
            ref["reference_slide"] = new_of[ref["reference_slide"]]
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    print("Deleted", drop, "→", new_total, "slides")


if __name__ == "__main__":
    main(parse(sys.argv[1:]))
