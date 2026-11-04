"""Generate the web deck from the offline deck and its archived media."""
import argparse
import base64
import hashlib
import html
import re

from archive_materials import DECK, MIMES, ROOT

ONLINE = DECK.with_name("index.html")
SLIDE = re.compile(r'<section\b[^>]*\bid="slide-\d+"[^>]*>.*?</section>', re.S)
MEDIA = re.compile(r'(?<![\w:-])(?:xlink:)?(src|href|poster)="data:([^;,"]+);base64,([A-Za-z0-9+/=\s]+)"')  # SVG xlink:href becomes plain data-media-href
MAP = re.compile(r'(<iframe class="offline-map-frame"[^>]*?)\bdata-srcdoc="([^"]+)"')


def archived_url(mime, blob):
    folder, extension = MIMES[mime]
    digest = hashlib.sha256(blob).hexdigest()
    path = f"materials/{folder}/{digest}.{extension}"
    if not (ROOT / path).is_file():
        raise ValueError(f"Missing archived asset: {path}. Run tools/archive_materials.py first.")
    return f"../{path}"


def externalize(match):
    attribute, mime, encoded = match.groups()
    if len(encoded) < 65_536 and mime != "video/mp4":
        return match[0]
    blob = base64.b64decode(re.sub(r"\s", "", encoded), validate=True)
    return f'data-media-{attribute}="{archived_url(mime, blob)}"'


def externalize_map(match):
    url = archived_url("text/html", html.unescape(match[2]).encode())
    return f'{match[1]}data-srcdoc-url="{url}"'


def online_document(document):
    document = SLIDE.sub(lambda slide: MEDIA.sub(externalize, slide[0]), document)
    document = MAP.sub(externalize_map, document)
    if document.count('<html lang="en">') != 1:
        raise ValueError("Expected one deck document element")
    return document.replace('<html lang="en">', '<html lang="en" data-offline-source="offline.html">', 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document = online_document(DECK.read_text())
    if args.check:
        if not ONLINE.exists() or ONLINE.read_text() != document:
            raise SystemExit("Online deck is stale. Run tools/build_online.py.")
    else:
        ONLINE.write_text(document)
    print(f"Online deck: {len(document.encode()):,} bytes.")


if __name__ == "__main__":
    main()
