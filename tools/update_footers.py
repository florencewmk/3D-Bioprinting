"""Normalize every slide footer in presentation/offline.html.

Footers show the event label from settings.json ("footer_label") on the left,
nothing in the middle (no presenter name, as requested on 5 November 2026) and
only the current page number on the right (no "/ total").

Slide generators still emit the older "date · presenter · NN / total" footer;
build_online.py runs this normalizer first, so a rebuild never brings it back.
The page number is taken from each section's id, so it stays correct after
reordering.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
SECTION = re.compile(r'(<section\b[^>]*\bid="slide-(\d+)"[^>]*>)(.*?)(</section>)', re.S)
FOOTER = re.compile(r'<footer>.*?</footer>', re.S)


def footer(number, label):
    return f'<footer><span>{html.escape(label)}</span><span></span><span>{number:02d}</span></footer>'


def normalize(document):
    label = json.loads((ROOT / "presentation/settings.json").read_text())["footer_label"]
    return SECTION.sub(lambda m: m[1] + FOOTER.sub(lambda _: footer(int(m[2]), label), m[3]) + m[4], document)


def main():
    document = DECK.read_text()
    updated = normalize(document)
    if updated != document:
        DECK.write_text(updated)
    print(f"Footers: {len(FOOTER.findall(updated))} normalized.")


if __name__ == "__main__":
    main()
