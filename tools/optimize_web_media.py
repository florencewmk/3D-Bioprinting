"""Replace the heaviest deck media with smaller web encodings (4 November 2026).

The originals stay in materials/ as higher-quality sources; this script records
each derived file in materials/web-optimized.json so archive_materials.py can
state its provenance. Requires Pillow and FFmpeg with libaom-av1 and libx264.

    python3 tools/optimize_web_media.py
    python3 tools/archive_materials.py && python3 tools/build_online.py
"""
import base64
import hashlib
import io
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
LOG = ROOT / "materials/web-optimized.json"
IMAGES = ROOT / "materials/images"
VIDEOS = ROOT / "materials/videos"

TURNTABLE = "1786970f76a9a466241c8f1d73348d20887c56f67d4135e133495fb97bac3c88.webp"
PNGS = [
    "888dfc578edba15cffbee51962d479e468315db11c5c9f853429f8899660b64a.png",  # slides 2, 26 background
    "45ce8684cee3a64960e394d3b57d499b1e356e1bfe8dc75db5ef9b88f6b6d4ed.png",  # slide 3 card
    "7b1ce1f737590ff915b1e8ed64000c73d767ea1c363cd6a54d6117dd88d58bfb.png",  # slide 3 card
]
VIDEO = "aa7b24fa286e97b34f74e5d0d0e09adfab6d23c4d30fb798159611dec5f93fc9.mp4"  # 5 Mbit/s process loop
STAGE_BG = (5, 5, 6, 255)  # the cover slide's flat background behind the lung


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def data_uri(mime, blob):
    return f"data:{mime};base64,{base64.b64encode(blob).decode()}"


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def turntable():
    """96-frame RGBA WebP -> opaque animated AVIF, 960 px wide, composited on the slide colour."""
    source = Image.open(IMAGES / TURNTABLE)
    with tempfile.TemporaryDirectory() as tmp:
        for index, frame in enumerate(ImageSequence.Iterator(source)):
            canvas = Image.new("RGBA", (1200, 968), STAGE_BG)
            canvas.alpha_composite(frame.convert("RGBA"))
            canvas.convert("RGB").save(f"{tmp}/{index:03d}.png")
        out = f"{tmp}/lung.avif"
        ffmpeg("-framerate", "16", "-i", f"{tmp}/%03d.png",
               "-vf", "scale=960:-2:flags=lanczos,format=yuv420p",
               "-c:v", "libaom-av1", "-crf", "36", "-b:v", "0", "-cpu-used", "6", "-row-mt", "1",
               "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
               "-color_range", "tv", out)
        return Path(out).read_bytes()


def webp(name):
    image = Image.open(IMAGES / name)
    if image.mode == "RGBA" and image.getchannel("A").getextrema() == (255, 255):
        image = image.convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, "WEBP", quality=85, method=6, alpha_quality=90)
    return buffer.getvalue()


def video():
    with tempfile.TemporaryDirectory() as tmp:
        out = f"{tmp}/clip.mp4"
        ffmpeg("-i", str(VIDEOS / VIDEO), "-c:v", "libx264", "-preset", "slow", "-crf", "23",
               "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", out)
        return Path(out).read_bytes()


def main():
    deck = DECK.read_text()
    log = json.loads(LOG.read_text()) if LOG.exists() else {}

    def record(blob, folder, ext, original, method):
        digest = sha(blob)
        (ROOT / f"materials/{folder}/{digest}.{ext}").write_bytes(blob)
        log[digest] = {"derived_from": f"materials/{original}", "method": method}
        return digest

    old = f'data-turntable-src="../materials/images/{TURNTABLE}"'
    if old in deck:
        digest = record(turntable(), "images", "avif", f"images/{TURNTABLE}",
                        "Composited on #050506 and re-encoded as a 960 px animated AVIF (AV1 CRF 36) for faster web loading.")
        deck = deck.replace(old, f'data-turntable-src="../materials/images/{digest}.avif"')
        print(f"turntable -> {digest}.avif")

    for name in PNGS:
        original = data_uri("image/png", (IMAGES / name).read_bytes())
        if original not in deck:
            continue
        blob = webp(name)
        record(blob, "images", "webp", f"images/{name}", "Re-encoded as WebP (quality 85) for faster web loading.")
        deck = deck.replace(original, data_uri("image/webp", blob))
        print(f"{name[:8]} png -> webp {len(blob):,} bytes")

    original = data_uri("video/mp4", (VIDEOS / VIDEO).read_bytes())
    if original in deck:
        blob = video()
        record(blob, "videos", "mp4", f"videos/{VIDEO}", "Re-encoded with H.264 CRF 23 (audio copied) for faster web loading.")
        deck = deck.replace(original, data_uri("video/mp4", blob))
        print(f"video -> {len(blob):,} bytes")

    DECK.write_text(deck)
    LOG.write_text(json.dumps(dict(sorted(log.items())), indent=2) + "\n")


if __name__ == "__main__":
    main()
