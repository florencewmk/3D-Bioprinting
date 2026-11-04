"""Archive media and SVG artwork from the current offline presentation.

Uses only the Python standard library. --check verifies the saved inventory
against both the presentation and archived files without writing anything.
"""
import argparse
import base64
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
OUT = ROOT / "materials"
MIMES = {
    "image/webp": ("images", "webp"),
    "image/avif": ("images", "avif"),
    "image/gif": ("images", "gif"),
    "image/png": ("images", "png"),
    "image/jpeg": ("images", "jpg"),
    "video/mp4": ("videos", "mp4"),
    "font/ttf": ("fonts", "ttf"),
    "font/woff2": ("fonts", "woff2"),
    "image/svg+xml": ("diagrams", "svg"),
    "text/html": ("interactive", "html"),
}
LIGHT_PROVENANCE = {
    "image/png": "Illustrated likeness of Chuck Hull generated for this talk from the National Inventors Hall of Fame portrait (invent.org/inductees/charles-hull); illustration, not a photograph. Used on the printing-with-light slides rendered by tools/light_slides.py.",
    "video/mp4": "Original Blender render of a top-down SLA cutaway printing the Baby Groot mesh by Byambaa (Thingiverse 2014307, CC BY-NC-ND 4.0, credited on the slide); burned-in caption and credit removed with FFmpeg delogo on 4 November 2026. Rendered by tools/light_slides.py.",
    "image/svg+xml": "Original animated SVG schematic drawn for this talk; template tools/light-slides.html, rendered by tools/light_slides.py.",
}
WEB_OPTIMIZED = json.loads((ROOT / "materials/web-optimized.json").read_text()) if (ROOT / "materials/web-optimized.json").exists() else {}
PROGRESS_PROVENANCE = {
    hashlib.sha256(path.read_bytes()).hexdigest(): text
    for name, text in __import__("progress_slide").PROVENANCE.items()
    for path in [ROOT / "tools/progress-slide" / name]
}
PROGRESS_PROVENANCE.update({
    hashlib.sha256(path.read_bytes()).hexdigest(): text
    for name, text in __import__("conclusion_slide").PROVENANCE.items()
    for path in [ROOT / "tools/conclusion-slide" / name]
})
DATA = re.compile(r"data:([^;,\s\"']+);base64,([A-Za-z0-9+/=\s]+)")


def inventory():
    source = DECK.read_bytes()
    document = source.decode("utf-8")
    sections = list(re.finditer(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>.*?</section>', document, re.S))
    records, blobs = {}, {}

    def add(blob, mime, slide, provenance=None):
        folder, extension = MIMES[mime]
        digest = hashlib.sha256(blob).hexdigest()
        path = f"materials/{folder}/{digest}.{extension}"
        if path not in records:
            records[path] = {"path": path, "mime": mime, "bytes": len(blob),
                             "sha256": digest, "slides": [],
                             "source": "presentation/offline.html",
                             "provenance": "Exported web asset; original credits are in the deck and transcript. Asset-level original attribution is not independently resolved."}
            if digest in WEB_OPTIMIZED:
                derived = WEB_OPTIMIZED[digest]
                provenance = (f"Web-optimized copy of {derived['derived_from']} (higher-quality original retained). "
                              f"{derived['method']} Original credits are in the deck and transcript.")
            if provenance is not None:
                records[path]["provenance"] = provenance
            elif mime == "text/html":
                records[path]["provenance"] = ("Bundled bioprinting globe and map, built by "
                    "tools/offline_map_slide.py from map/ and archived Natural Earth boundaries.")
            blobs[path] = blob
        if slide is not None and slide not in records[path]["slides"]:
            records[path]["slides"].append(slide)

    light = {int(s[1]) for s in sections if 'light-slide' in s[0].split(">", 1)[0]}
    for match in DATA.finditer(document):
        slide = next((int(s[1]) for s in sections if s.start() <= match.start() < s.end()), None)
        blob = base64.b64decode(re.sub(r"\s", "", match[2]), validate=True)
        add(blob, match[1], slide, PROGRESS_PROVENANCE.get(hashlib.sha256(blob).hexdigest())
            or (LIGHT_PROVENANCE.get(match[1]) if slide in light else None))
    for section in sections:
        for asset in re.findall(r'data-turntable-src="\.\./(materials/images/[a-f0-9]{64}\.(?:webp|avif))"', section[0]):
            blob = (ROOT / asset).read_bytes()
            if hashlib.sha256(blob).hexdigest() != Path(asset).stem:
                raise ValueError(f"Turntable hash mismatch: {asset}")
            add(blob, "image/avif" if asset.endswith(".avif") else "image/webp", int(section[1]))
        for svg in re.finditer(r"<svg\b.*?</svg>", section[0], re.S):
            add(svg[0].encode("utf-8"), "image/svg+xml", int(section[1]),
                LIGHT_PROVENANCE["image/svg+xml"] if int(section[1]) in light else None)
        for frame in re.finditer(r'<iframe class="offline-map-frame"[^>]*\bsrcdoc="([^"]+)"', section[0]):
            add(html.unescape(frame[1]).encode("utf-8"), "text/html", int(section[1]))
        for frame in re.finditer(r'<iframe class="tram-story-frame"[^>]*\bsrcdoc="([^"]+)"', section[0]):
            add(html.unescape(frame[1]).encode("utf-8"), "text/html", int(section[1]),
                "Original editable SVG tram story from materials/interactive/munich-tram-story.html, embedded by tools/update_tram_slide.py.")
    manifest = {"source": "presentation/offline.html", "source_sha256": hashlib.sha256(source).hexdigest(),
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
