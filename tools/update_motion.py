"""Embed content-aware motion without touching slide/controller source content.

Run after a full conversion. Other targeted slide updaters preserve this separate
script block. --input/--output support isolated previews during concurrent edits.
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- SLIDE_MOTION_BEGIN -->'
END = '<!-- SLIDE_MOTION_END -->'


def with_motion(document):
    document = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\s*', '', document, flags=re.S)
    script = (ROOT / 'tools/slide-motion.js').read_text().rstrip()
    block = f'{START}\n<script id="slideMotionScript">\n{script}\n</script>\n{END}\n'
    assert '</body>' in document and 'id="deckStage"' in document
    return document.replace('</body>', block + '</body>', 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'presentation/offline.html')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or args.input
    before = args.input.read_text()
    after = with_motion(before)
    sections = lambda text: re.findall(r'<section\b[^>]*\bid="slide-\d+".*?</section>', text, re.S)
    assert sections(before) == sections(after), 'Slide content must remain unchanged'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(after)
    print(f'Embedded motion; all {len(sections(after))} slide sections preserved: {output}')
