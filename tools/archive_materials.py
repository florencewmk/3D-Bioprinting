"""Archive media and SVG artwork from the current offline presentation.

Uses only the Python standard library. --check verifies the saved inventory
against both the presentation and archived files without writing anything.
"""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/index.html"
OUT = ROOT / "materials"
MIMES = {
    "image/webp": ("images", "webp"),
    "image/png": ("images", "png"),
    "image/jpeg": ("images", "jpg"),
    "video/mp4": ("videos", "mp4"),
    "font/ttf": ("fonts", "ttf"),
    "font/woff2": ("fonts", "woff2"),
    "image/svg+xml": ("diagrams", "svg"),
}
DATA = re.compile(r"data:([^;,\s\"']+);base64,([A-Za-z0-9+/=\s]+)")


def inventory():
    source = DECK.read_bytes()
    document = source.decode("utf-8")
    sections = list(re.finditer(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>.*?</section>', document, re.S))
    records, blobs = {}, {}

    def add(blob, mime, slide):
        folder, extension = MIMES[mime]
        digest = hashlib.sha256(blob).hexdigest()
        path = f"materials/{folder}/{digest}.{extension}"
        if path not in records:
            records[path] = {"path": path, "mime": mime, "bytes": len(blob),
                             "sha256": digest, "slides": [],
                             "source": "presentation/index.html",
                             "provenance": "Exported web asset; original credits are in the deck and transcript. Asset-level original attribution is not independently resolved."}
            blobs[path] = blob
        if slide is not None and slide not in records[path]["slides"]:
            records[path]["slides"].append(slide)

    for match in DATA.finditer(document):
        slide = next((int(s[1]) for s in sections if s.start() <= match.start() < s.end()), None)
        add(base64.b64decode(re.sub(r"\s", "", match[2]), validate=True), match[1], slide)
    for section in sections:
        for svg in re.finditer(r"<svg\b.*?</svg>", section[0], re.S):
            add(svg[0].encode("utf-8"), "image/svg+xml", int(section[1]))
    manifest = {"source": "presentation/index.html", "source_sha256": hashlib.sha256(source).hexdigest(),
                "slides": len(sections), "asset_count": len(records),
                "assets": sorted(records.values(), key=lambda r: r["path"])}
    return manifest, blobs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest, blobs = inventory()
    target = OUT / "manifest.json"
    if args.check:
        if json.loads(target.read_text()) != manifest:
            raise SystemExit("Material inventory is stale; rerun tools/archive_materials.py")
        for path, blob in blobs.items():
            if (ROOT / path).read_bytes() != blob:
                raise SystemExit(f"Material differs from presentation: {path}")
        print(f"Verified {len(blobs)} materials across {manifest['slides']} slides.")
    else:
        for path, blob in blobs.items():
            destination = ROOT / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(blob)
        target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        print(f"Archived {len(blobs)} materials across {manifest['slides']} slides.")


if __name__ == "__main__":
    main()
