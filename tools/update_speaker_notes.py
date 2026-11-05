"""Apply presentation/speaker-notes.json to the offline deck and transcript.

Updates the notes panel data (sourceData), the per-slide "Speaker notes" HTML
comments and the "### Speaker notes" sections of presentation/transcript.md.
Run tools/build_online.py afterwards to refresh presentation/index.html.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation" / "offline.html"
TRANSCRIPT = ROOT / "presentation" / "transcript.md"
NOTES = ROOT / "presentation" / "speaker-notes.json"
DATA = re.compile(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', re.S)


def main():
    notes = {int(k): v.strip() for k, v in json.loads(NOTES.read_text()).items() if k.isdigit()}
    deck = DECK.read_text()
    match = DATA.search(deck)
    slides = json.loads(match[2])
    for slide in slides:
        if slide["number"] in notes:
            slide["notes"] = notes[slide["number"]]
    payload = json.dumps(slides, ensure_ascii=False).replace("</", "<\\/")
    deck = deck[:match.start(2)] + payload + deck[match.end(2):]

    for number, text in notes.items():
        start = deck.find(f'id="slide-{number}"')
        end = deck.find("</section>", start)
        section = deck[start:end]
        comment = re.search(r"<!-- Speaker notes: .*? -->", section, re.S)
        if comment:
            safe = text.replace("--", "–").replace("\n\n", " ")
            section = section[:comment.start()] + f"<!-- Speaker notes: {safe} -->" + section[comment.end():]
            deck = deck[:start] + section + deck[end:]
    DECK.write_text(deck)

    transcript = TRANSCRIPT.read_text()
    for number, text in notes.items():
        heading = re.search(rf"^## {number:02d}\. .*$", transcript, re.M)
        nxt = re.search(r"^## \d+\. ", transcript[heading.end():], re.M)
        stop = heading.end() + nxt.start() if nxt else len(transcript)
        block = transcript[heading.end():stop]
        if "### Speaker notes" in block:
            block = block[:block.index("### Speaker notes")]
        block = block.rstrip() + f"\n\n### Speaker notes\n\n{text}\n\n"
        transcript = transcript[:heading.end()] + block + transcript[stop:]
    TRANSCRIPT.write_text(transcript)
    print(f"Updated speaker notes for {len(notes)} slides.")


if __name__ == "__main__":
    main()
