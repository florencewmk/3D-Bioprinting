"""Reorder the talk (2026-11-04 evening).

- Globe "Bioprinting around the world" (old 9) moves after "Where are we today?" (old 17).
- "What if we could print organs?" (old 5) and old 19–23 (tissue engineering, bioinks to
  bioprinters, soft tissue research in orbit, bio-plaster on ISS, conclusion diagram) move
  to the start of the technical backup, right after its divider.

Renumbers slide ids, aria labels, footers, data-goto links, Contents page numbers,
speaker data, transcript, settings sections, paper catalog reference slides, the help
summary and the overview's TALK / REFERENCES / BACKUP labels. Runs once (asserts the
old order) and keeps the deck at 60 slides.
"""
import json
import re
from pathlib import Path

from deck_structure import write_transcript

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
SECTION = re.compile(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>.*?</section>', re.S)
DATA = re.compile(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', re.S)
ORDER = [1, 2, 3, 4, 6, 7, 8, *range(10, 18), 9, 18, 24, 25, *range(26, 31), 31, 5, *range(19, 24), *range(32, 61)]
EXPECT = {5: "What if we could print organs?", 9: "Bioprinting around the world", 17: "Where are we today?",
          23: "Layers to living tissue", 24: "Engineering tomorrow’s possibilities", 31: "Technical backup"}
TALK_END, REF_END = 19, 24  # new numbers: talk 1–19, references 20–24, backup 25–60


def main():
    document = DECK.read_text()
    matches = list(SECTION.finditer(document))
    data = json.loads(DATA.search(document)[2])
    total = len(matches)
    assert total == len(data) == 60 and sorted(ORDER) == list(range(1, 61))
    for old, title in EXPECT.items():
        assert data[old - 1]["title"] == title, (old, data[old - 1]["title"])
    renumber = {old: new for new, old in enumerate(ORDER, 1)}
    goto = lambda old: renumber[24] if old == 23 else renumber[old]  # "Conclusion" links now open the closing slide
    sections, rows = [], []
    for new, old in enumerate(ORDER, 1):
        section, row = matches[old - 1][0], dict(data[old - 1])
        section = re.sub(r'id="slide-\d+"', f'id="slide-{new}"', section, count=1)
        section = re.sub(r'aria-label="\d+\. ', f'aria-label="{new}. ', section, count=1)
        section = re.sub(r'(data-goto=")(\d+)', lambda m: m[1] + str(goto(int(m[2]))), section)
        section = re.sub(r'<small>(\d+) →</small>', lambda m: f'<small>{goto(int(m[1])):02d} →</small>', section)
        section = re.sub(r'Page (\d+)', lambda m: f'Page {goto(int(m[1])):02d}', section)
        section = re.sub(r'<span>\d+ / 60</span></footer>', f'<span>{new:02d} / {total}</span></footer>', section)
        row["number"] = new
        row["text"] = re.sub(r'Page (\d+)', lambda m: f'Page {goto(int(m[1])):02d}', row["text"])
        sections.append(section)
        rows.append(row)
    document = document[:matches[0].start()] + "\n".join(sections) + document[matches[-1].end():]
    document = DATA.sub(lambda m: m[1] + json.dumps(rows, ensure_ascii=False).replace('</', '<\\/') + m[3], document, count=1)
    old_summary = "talk 1–25, references 26–30, technical backup 31–60"
    assert old_summary in document
    document = document.replace(old_summary, f"talk 1–{TALK_END}, references {TALK_END + 1}–{REF_END}, technical backup {REF_END + 1}–{total}")
    old_labels = "${i<24?'TALK':i<29?'REFERENCES':'BACKUP'}"
    new_labels = f"${{i<{TALK_END}?'TALK':i<{REF_END}?'REFERENCES':'BACKUP'}}"
    assert document.count(old_labels) == 1
    document = document.replace(old_labels, new_labels)
    DECK.write_text(document)
    js = ROOT / "tools/deck.js"
    js.write_text(js.read_text().replace(old_labels, new_labels))
    write_transcript(ROOT / "presentation/transcript.md", rows)

    settings_path = ROOT / "presentation/settings.json"
    settings = json.loads(settings_path.read_text())
    for item in settings["sections"]:
        item["slide"] = goto(item["slide"])
    settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
    catalog_path = ROOT / "papers/catalog.json"
    catalog = json.loads(catalog_path.read_text())
    for ref in catalog.get("presentation_references", []):
        if isinstance(ref.get("reference_slide"), int):
            ref["reference_slide"] = renumber[ref["reference_slide"]]
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    print("New order:", ", ".join(f"{new}←{old}" for new, old in enumerate(ORDER, 1) if new != old))


if __name__ == "__main__":
    main()
