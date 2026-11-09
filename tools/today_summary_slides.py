"""Re-render "Where are we today?" and "Take-home summary" in the deck's drawn style (9 Nov 2026).

Where are we today? (class progress-slide, steps via hidden .ps-step markers):
  Lab → Patient → Space → Medical. Each point draws a line figure on the canvas
  (vessel tree + heart, ear, Earth/orbit + meniscus, dashed hospital), then the real
  photo fades in on the same spot and the drawing shrinks into its timeline stop.
  The DLR bio-plaster photo was removed on Florence's request.
Take-home summary (class ring-slide, steps via hidden .rs-step markers):
  ring + four points; the right-hand visual recalls earlier slides
  (dots, light vat, vessels in cells, timeline). Replaces the Readily3D video.

Canvas code: tools/today-summary/where-today.js and summary.js (previewed standalone
first). Photos: tools/progress-slide/c-*.jpg (provenance in progress_slide.py).
Re-renders both sections in place; run tools/archive_materials.py,
tools/build_online.py, then archive_materials.py again.
"""
import base64
import html
import json
import re
from pathlib import Path

from deck_structure import write_transcript

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
ASSETS = ROOT / "tools/today-summary"
PHOTOS = ROOT / "tools/progress-slide"
SECTION = re.compile(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>.*?</section>', re.S)
DATA = re.compile(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', re.S)
NAV = re.compile(r'<nav class="section-nav".*?</nav>', re.S)

TODAY = [
    ("In the lab", "Printed blood vessels and a mini heart",
     "Harvard’s Wyss Institute prints branching vessels inside living heart tissue (2024). Tel Aviv printed a heart the size of a rabbit’s from a patient’s own cells (2019). It cannot pump yet."),
    ("In a patient", "A printed ear",
     "In 2022, a woman born with microtia received an ear printed from her own cartilage cells. It was the first clinical trial of its kind."),
    ("In space", "Printing without gravity",
     "NASA’s BioFabrication Facility printed a human knee meniscus on the ISS (2023)."),
    ("In medicine", "Ready for hospitals?",
     "Maybe in the next 10 years, starting with simple tissues like skin and cartilage. Whole organs will take longer."),
]
PHOTO_LAYOUT = [  # file, caption, scene, left, top, width
    ("c-vessel.jpg", "Printed vessels · Wyss Institute, Harvard 2024", 0, 860, 300, 490),
    ("c-heart.jpg", "Printed heart · Tel Aviv University 2019", 0, 1390, 360, 490),
    ("c-ear.jpg", "Before and after · 3DBio Therapeutics 2022", 1, 940, 250, 830),
    ("c-meniscus.jpg", "Meniscus printed on the ISS · NASA 2023", 2, 1010, 270, 680),
]
TODAY_SOURCES = "Source: Harvard SEAS / Wyss Institute (2024) · Tel Aviv University (2019) · CELLINK / 3DBio (2022) · NASA (2023)"
DLR_NOTE = " And Germany printed a bio-plaster. It’s not close to printing organs, but in a medical sense it’s also useful."

SUMMARY = [
    ("#E394AD", "Transplant demand outpaces donors", "532,905 waiting · 40,019 deaths on waiting lists (2025)"),
    ("#B49AD8", "Living cells in a gel, layer by layer", "Light, cure, repeat"),
    ("#64DFFF", "Lab successes, first steps in patients", "Printed vessels in the lab · a bioprinted ear implanted (2022)"),
    ("#70C2BC", "Tissues in ~10 years, organs in 20–30", "AI may speed up development"),
]
SUMMARY_LEGENDS = [
    '<i style="background:#B49AD8;margin-left:0"></i>waiting<i style="background:#64DFFF"></i>transplants'
    '<i style="border:2px solid #E394AD;width:9px;height:9px;background:none"></i>deaths<br><span>1 dot = 10,000 · 2025</span>',
    "", "cells close to a printed vessel stay alive", "expert estimate · Skylar-Scott, Stanford (2025)",
]
SUMMARY_SOURCES = "Source: EDQM–ONT Newsletter Transplant (2026) · Wyss Institute (2024) · 3DBio (2022) · Skylar-Scott, Stanford, via 3DPrint.com (2025)"

TODAY_STYLE = """<style id="progress-slide-style">
.progress-slide .ps-step{display:none}
.progress-slide canvas.wt-canvas{position:absolute;inset:0;width:100%;height:100%;z-index:0}
.progress-slide h1.wt-title{position:absolute;left:110px;top:96px;margin:0;font-size:68px;font-weight:400;line-height:1.1;color:#F1F5F5;z-index:2}
.progress-slide .wt-cap{position:absolute;left:110px;top:300px;width:660px;z-index:2;opacity:0;transform:translateY(12px);transition:opacity .6s,transform .6s}
.progress-slide .wt-cap.on{opacity:1;transform:none}
.progress-slide .wt-cap small{display:block;font-size:24px;color:#B49AD8;margin-bottom:14px;letter-spacing:.02em}
.progress-slide .wt-cap b{display:block;font-size:56px;font-weight:500;line-height:1.12;color:#F1F5F5}
.progress-slide .wt-cap b.no{color:#E394AD;margin-top:6px}
.progress-slide .wt-cap p{font-size:27px;line-height:1.45;color:#c3c0cb;margin:22px 0 0}
.progress-slide .wt-ph{position:absolute;margin:0;z-index:1;opacity:0;transform:scale(.97);transition:opacity .5s,transform .9s}
.progress-slide .wt-ph.on{transform:none}
.progress-slide .wt-ph img{display:block;width:100%;height:auto;border-radius:14px;border:1px solid rgba(241,245,245,.16);box-shadow:0 20px 60px rgba(0,0,0,.6)}
.progress-slide .wt-ph figcaption{font-size:19px;color:#84919D;margin-top:12px;text-align:center}
@media print{.progress-slide .wt-cap{opacity:0}.progress-slide .wt-cap:last-of-type{opacity:1;transform:none}}
</style>"""

SUMMARY_STYLE = """<style id="ring-slide-style">
.ring-slide .rs-step{display:none}
.ring-slide canvas.sm-canvas{position:absolute;inset:0;width:100%;height:100%;z-index:0}
.ring-slide h1.rs-title{position:absolute;left:110px;top:96px;margin:0;font-size:68px;font-weight:400;line-height:1.1;color:#F1F5F5;z-index:2}
.ring-slide h1.rs-title em{font-style:normal}
.ring-slide .sm-it{position:absolute;left:640px;width:600px;z-index:2;opacity:0;transform:translateY(10px);transition:opacity .6s,transform .6s}
.ring-slide .sm-it.on{opacity:1;transform:none}.ring-slide .sm-it.past{opacity:.38;transform:none}
.ring-slide .sm-it b{display:block;font-size:34px;font-weight:500;line-height:1.2}
.ring-slide .sm-it span{display:block;font-size:22px;color:#a9b2ba;margin-top:6px}
.ring-slide .sm-lg{position:absolute;left:1290px;top:850px;width:520px;z-index:2;font-size:20px;color:#84919D;text-align:center;opacity:0;transition:opacity .6s}
.ring-slide .sm-lg.on{opacity:1}
.ring-slide .sm-lg span{font-size:18px}
.ring-slide .sm-lg i{display:inline-block;width:12px;height:12px;border-radius:50%;margin:0 6px 0 18px;vertical-align:-1px}
@media print{.ring-slide .sm-it{opacity:1;transform:none}}
</style>"""


def b64(path):
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


def markers(cls):
    return "".join(f'<i class="{cls}" data-reveal-step="{k}" aria-hidden="true" inert></i>' for k in (1, 2, 3))


def today_text():
    lines = ["Where are we today?"]
    for small, head, body in TODAY:
        lines += [small, head, ("Not yet. " + body) if small == "In medicine" else body]
    return "\n".join(lines + [TODAY_SOURCES])


def summary_text():
    return "\n".join(["Take-home summary"] + [x for _, a, b in SUMMARY for x in (a, b)] + [SUMMARY_SOURCES])


def render_today(number, nav, notes):
    caps = ""
    for i, (small, head, body) in enumerate(TODAY):
        no = '<b class="no">Not yet.</b>' if small == "In medicine" else ""
        caps += (f'<div class="wt-cap{" on" if i == 0 else ""}" data-i="{i}"><small>{html.escape(small)}</small>'
                 f'<b>{html.escape(head)}</b>{no}<p>{html.escape(body)}</p></div>')
    photos = "".join(
        f'<figure class="wt-ph" data-s="{s}" style="left:{l}px;top:{t}px;width:{w}px">'
        f'<img alt="{html.escape(c, quote=True)}" src="{b64(PHOTOS / f)}"><figcaption>{html.escape(c)}</figcaption></figure>'
        for f, c, s, l, t, w in PHOTO_LAYOUT)
    return (f'<section class="slide progress-slide" data-ps="0" id="slide-{number}" aria-label="{number}. Where are we today?" aria-hidden="true">'
            + nav + TODAY_STYLE
            + '<canvas class="wt-canvas" role="img" aria-label="Line drawings on a timeline: printed vessels and a heart in the lab, a printed ear in a patient, a meniscus printed in orbit, and a dashed hospital for not yet."></canvas>'
            + '<h1 class="wt-title">Where are we today?</h1>' + caps + photos + markers("ps-step")
            + f'<div class="sr-only">{html.escape(today_text())}</div><!-- Speaker notes: {html.escape(notes.replace(chr(10) * 2, " ").replace("--", "–"))} -->'
            + f'<footer><span></span><span></span><span>{number}</span></footer>'
            + '<script>' + (ASSETS / "where-today.js").read_text() + '</script></section>')


def render_summary(number, nav, notes):
    items = "".join(f'<div class="sm-it{" on" if i == 0 else ""}" style="top:{330 + 120 * i}px"><b style="color:{c}">{html.escape(a)}</b><span>{html.escape(b)}</span></div>'
                    for i, (c, a, b) in enumerate(SUMMARY))
    legends = "".join(f'<div class="sm-lg{" on" if i == 0 else ""}" data-i="{i}">{l}</div>' for i, l in enumerate(SUMMARY_LEGENDS))
    return (f'<section class="slide ring-slide" data-rs="0" id="slide-{number}" aria-label="{number}. Take-home summary" aria-hidden="true">'
            + nav + SUMMARY_STYLE
            + '<canvas class="sm-canvas" role="img" aria-label="Summary ring with four points; each point recalls an earlier slide: dots for the organ shortage, a light-curing vat, vessels feeding cells, and a timeline to printed tissues and organs."></canvas>'
            + '<h1 class="rs-title">Take-home <em class="gradient">summary</em></h1>' + items + legends + markers("rs-step")
            + f'<div class="sr-only">{html.escape(summary_text())}</div><!-- Speaker notes: {html.escape(notes.replace(chr(10) * 2, " ").replace("--", "–"))} -->'
            + f'<footer><span></span><span></span><span>{number}</span></footer>'
            + '<script>' + (ASSETS / "summary.js").read_text() + '</script></section>')


def main():
    document = DECK.read_text()
    rows = json.loads(DATA.search(document)[2])
    titles = [r["title"] for r in rows]
    today, summary = titles.index("Where are we today?") + 1, titles.index("Take-home summary") + 1
    rows[today - 1]["notes"] = rows[today - 1]["notes"].replace(DLR_NOTE, "")
    rows[today - 1]["text"] = today_text()
    rows[summary - 1]["text"] = summary_text()

    def replace(match):
        n = int(match[1])
        if n not in (today, summary):
            return match[0]
        nav = NAV.search(match[0])[0]
        notes = rows[n - 1]["notes"]
        return render_today(n, nav, notes) if n == today else render_summary(n, nav, notes)

    document = SECTION.sub(replace, document)
    document = DATA.sub(lambda m: m[1] + json.dumps(rows, ensure_ascii=False).replace('</', '<\\/') + m[3], document, count=1)
    DECK.write_text(document)
    write_transcript(ROOT / "presentation/transcript.md", rows)
    print(f"Re-rendered slides {today} and {summary}.")


if __name__ == "__main__":
    main()
