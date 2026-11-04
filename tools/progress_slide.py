"""Render slide 17 "Where are we today?" (current progress of bioprinting).

A slide-4-style card stack in four reveals: Lab (Wyss vessels, Tel Aviv heart),
Patient (3DBio ear), Space (NASA meniscus, DLR bio-plaster), Medical ("Not yet").
Images and the generated orbit background live in tools/progress-slide/.

First run inserts the slide at POSITION and renumbers every later slide
(ids, footers, menu links, Contents pages, settings, catalog, transcript).
Later runs re-render the slide in place, so edit this file and rerun.
"""
import base64
import html
import json
import re
from pathlib import Path

from deck_structure import write_transcript

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
ASSETS = ROOT / "tools/progress-slide"
SECTION = re.compile(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>.*?</section>', re.S)
DATA = re.compile(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', re.S)
POSITION = 17
TITLE = "Where are we today?"

STEPS = [
    ("In the lab", "Printed blood vessels and a mini heart",
     "Harvard’s Wyss Institute prints branching vessels inside living heart tissue (2024). "
     "Tel Aviv printed a heart the size of a rabbit’s from a patient’s own cells (2019). It cannot pump yet."),
    ("In a patient", "A printed ear",
     "In 2022, a woman born with microtia received an ear printed from her own cartilage cells. "
     "It was the first clinical trial of its kind."),
    ("In space", "Printing on the space station",
     "NASA’s BioFabrication Facility printed a human knee meniscus on the ISS (2023). "
     "Germany tested a handheld bio-plaster printer there (2022)."),
    ("In medicine", "Ready for hospitals?",
     "<b>Not yet.</b> Maybe in the next 10 years, starting with simple tissues like skin and cartilage. "
     "Whole organs will take longer."),
]
# file, caption, width, height, left, top, rotation
CARDS = [
    ("c-vessel.jpg", "Printed vessels · Wyss Institute, Harvard 2024", 580, 432, 0, 0, -2),
    ("c-heart.jpg", "Printed heart · Tel Aviv University 2019", 580, 354, 380, 300, 3),
    ("c-ear.jpg", "Before and after · 3DBio Therapeutics 2022", 720, 426, 120, 120, 2),
    ("c-meniscus.jpg", "Meniscus printed on the ISS · NASA 2023", 620, 349, 40, 290, -2),
    ("c-iss.jpg", "Bio-plaster test on the ISS · DLR 2022", 520, 292, 420, 0, 4),
]
VISIBLE = [[0, 1], [0, 1, 2], [0, 1, 2, 3, 4], [0, 1, 2, 3, 4]]
FRONT = [[0, 1], [2], [4, 3], []]  # later in the list = on top
TRACK = ["Lab", "Patient", "Space", "Medical"]
SOURCE = ("Source: Harvard SEAS / Wyss Institute (2024) · Tel Aviv University (2019) · "
          "CELLINK / 3DBio (2022) · NASA (2023) · DLR (2022)")
PROVENANCE = {
    "bg-orbit.jpg": "Original background generated in Python for this talk (faded nebula and planet edge in the deck palette); tools/progress_slide.py.",
    "c-vessel.jpg": "co-SWIFT vessel image from Harvard SEAS / Wyss Institute news, 12 Aug 2024 (reference [15]); taken from the user's SoFe pptx.",
    "c-heart.jpg": "Printed heart photo, Tel Aviv University, 2019 (reference [20]); taken from the user's SoFe pptx.",
    "c-ear.jpg": "Before/after ear photo, Microtia-Congenital Ear Institute and 3DBio Therapeutics, 2022 (references [24], [49], [50]); taken from the user's SoFe pptx.",
    "c-meniscus.jpg": "Meniscus bioprinted in the BioFabrication Facility, NASA (reference [18]); existing deck asset.",
    "c-iss.jpg": "Matthias Maurer running Bioprint FirstAid on the ISS, DLR 2022 (reference [19]); existing deck asset.",
}
NOTES = """So where are we today?

In the lab, researchers at Harvard’s Wyss Institute can now print branching blood vessels inside living heart tissue. In Tel Aviv, a team printed a small heart, the size of a rabbit’s, from a patient’s own cells. It cannot pump yet.

The first printed tissue has already reached a patient. In 2022, a young woman born with microtia received an ear printed from her own cartilage cells, in a clinical trial.

And bioprinting has even gone to space. NASA printed a knee meniscus on the ISS, and Germany tested a handheld printer for wound plasters there.

So, is it ready for hospitals? Not yet. Maybe in the next ten years, starting with simple tissues like skin and cartilage. Whole organs will take longer."""

STYLE = """<style id="progress-slide-style">
.progress-slide .ps-bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0;pointer-events:none}
.progress-slide .ps-step{display:none}
.progress-slide h1.ps-title{position:absolute;left:110px;top:96px;margin:0;font-size:68px;font-weight:400;line-height:1.1;color:#F1F5F5;z-index:1}
.progress-slide .ps-layout{position:absolute;left:110px;right:110px;top:250px;bottom:230px;display:grid;grid-template-columns:1fr 1.3fr;gap:40px;align-items:start;z-index:1}
.progress-slide .ps-copy{grid-area:1/1;opacity:0;visibility:hidden;transition:opacity .3s;padding-top:30px}
.progress-slide[data-ps="0"] .ps-copy[data-step="0"],.progress-slide[data-ps="1"] .ps-copy[data-step="1"],
.progress-slide[data-ps="2"] .ps-copy[data-step="2"],.progress-slide[data-ps="3"] .ps-copy[data-step="3"]{opacity:1;visibility:visible}
.progress-slide .ps-copy .eb{color:#c6acef;font-size:30px;margin:0 0 16px}
.progress-slide .ps-copy h2{font-size:76px;font-weight:500;line-height:1.06;margin:0;color:#F1F5F5}
.progress-slide .ps-copy .dt{color:#c3c0cb;font-size:32px;line-height:1.4;margin:22px 0 0;max-width:720px}
.progress-slide .ps-copy .dt b{display:block;color:#E394AD;font-size:76px;font-weight:500;line-height:1.1;margin-bottom:14px}
.progress-slide .ps-stack{grid-area:1/2;position:relative;height:600px}
.progress-slide .ps-card{position:absolute;margin:0;background:#000;border:2px solid #52505c;border-radius:22px;overflow:hidden;box-shadow:0 22px 64px #000c;opacity:0;visibility:hidden;transform:translateY(24%);transition:transform .5s ease,opacity .4s ease,visibility .4s,filter .4s}
.progress-slide .ps-card img{width:100%;height:100%;object-fit:cover;display:block}
.progress-slide .ps-card[data-card="0"] img{object-fit:contain}
.progress-slide .ps-card figcaption{position:absolute;left:0;right:0;bottom:0;padding:40px 20px 14px;font-size:19px;color:#ecebf0;background:linear-gradient(transparent,#000d)}
.progress-slide .ps-card[data-card="0"] figcaption{top:0;bottom:auto;padding:14px 20px 40px;background:linear-gradient(#000d,transparent)}
.progress-slide .ps-card.on{opacity:1;visibility:visible;transform:rotate(var(--r))}
.progress-slide .ps-card.back{transform:translate(-8%,-10%) rotate(calc(var(--r) - 6deg)) scale(.86);filter:brightness(.45)}
.progress-slide[data-ps="3"] .ps-card{filter:brightness(.22) blur(1px)}
.progress-slide .ps-track{position:absolute;left:110px;bottom:150px;display:flex;list-style:none;margin:0;padding:0;z-index:1}
.progress-slide .ps-track li{position:relative;width:200px;font-size:22px;color:#77737f;padding-top:30px;transition:color .3s}
.progress-slide .ps-track li span{position:absolute;top:0;left:0;width:16px;height:16px;border-radius:50%;border:2px solid #77737f;transition:.3s;box-sizing:border-box}
.progress-slide .ps-track li:not(:last-child)::after{content:"";position:absolute;top:7px;left:24px;right:8px;height:2px;background:#3a3842}
.progress-slide .ps-track li.done{color:#F1F5F5}
.progress-slide .ps-track li.done span{background:#64DFFF;border-color:#64DFFF;box-shadow:0 0 14px #64DFFF}
.progress-slide .ps-track li.done:not(:last-child)::after{background:linear-gradient(90deg,#64DFFF,#B49AD8)}
.progress-slide .ps-track li.now{color:#64DFFF}
.progress-slide .ps-track li.open{color:#E394AD}
.progress-slide .ps-track li.open span{border-color:#E394AD;border-style:dashed;animation:ps-pulse 1.6s ease-in-out infinite}
@keyframes ps-pulse{50%{box-shadow:0 0 0 8px #e394ad33}}
.progress-slide .refs{position:absolute;left:70px;right:70px;bottom:60px;margin:0;font-size:16px;line-height:1.45;color:#8d8a96;z-index:1}
@media(prefers-reduced-motion:reduce){.progress-slide .ps-card,.progress-slide .ps-copy{transition:none}}
</style>"""

SCRIPT = """<script>(()=>{const s=document.querySelector('.progress-slide');if(!s)return;
const VIS=%s,FRONT=%s;
const sync=()=>{const n=s.querySelectorAll('.ps-step.revealed').length;s.dataset.ps=n;
s.querySelectorAll('.ps-card').forEach((c,i)=>{const on=VIS[n].includes(i),f=FRONT[n].indexOf(i);c.classList.toggle('on',on);c.classList.toggle('back',on&&n<3&&f<0);c.style.zIndex=f>=0?10+f:i});
s.querySelectorAll('.ps-track li').forEach((l,i)=>{l.className=i===3?(n===3?'open':''):[i<=n?'done':'',i===n?'now':''].join(' ').trim()})};
const mo=new MutationObserver(sync);s.querySelectorAll('.ps-step').forEach(m=>mo.observe(m,{attributes:true,attributeFilter:['class']}));sync();})();</script>""" % (
    json.dumps(VISIBLE), json.dumps(FRONT))


def b64(name):
    return "data:image/jpeg;base64," + base64.b64encode((ASSETS / name).read_bytes()).decode()


def plain(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text))


def render(number, total, conclusion, date, presenter):
    copy = "".join(
        f'<div class="ps-copy" data-step="{i}"><p class="eb">{e}</p><h2>{t}</h2><p class="dt">{d}</p></div>'
        for i, (e, t, d) in enumerate(STEPS))
    cards = "".join(
        f'<figure class="ps-card" data-card="{i}" style="width:{w}px;height:{h}px;left:{l}px;top:{t}px;--r:{r}deg">'
        f'<img alt="{html.escape(a, quote=True)}" src="{b64(f)}"><figcaption>{html.escape(a)}</figcaption></figure>'
        for i, (f, a, w, h, l, t, r) in enumerate(CARDS))
    track = "".join(f"<li><span></span>{t}</li>" for t in TRACK)
    markers = "".join(f'<i class="ps-step" data-reveal-step="{k}" aria-hidden="true" inert></i>' for k in range(1, 4))
    text = "\n".join([TITLE] + [f"{e}\n{t}\n{plain(d)}" for e, t, d in STEPS] + [SOURCE])
    nav = ('<nav class="section-nav" aria-label="Talk sections"><button data-goto="3" class="">Introduction</button>'
           f'<button data-goto="10" class="current">Printing methods</button><button data-goto="{conclusion}" class="">'
           'Conclusion</button><span></span></nav>')
    section = (
        f'<section class="slide progress-slide" data-ps="0" id="slide-{number}" aria-label="{number}. {html.escape(TITLE)}" aria-hidden="true">'
        + nav + STYLE + f'<img class="ps-bg" alt="" src="{b64("bg-orbit.jpg")}">'
        + f'<h1 class="ps-title">{TITLE}</h1><div class="ps-layout">{copy}<div class="ps-stack">{cards}</div></div>'
        + f'<ol class="ps-track">{track}</ol><p class="refs">{html.escape(SOURCE)}</p>' + markers
        + f'<div class="sr-only">{html.escape(text)}</div><!-- Speaker notes: {html.escape(NOTES)} -->'
        + f'<footer><span>{date}</span><span>{presenter}</span><span>{number:02d} / {total}</span></footer>'
        + SCRIPT + "</section>")
    return section, {"number": number, "title": TITLE, "text": text, "notes": NOTES}


def insert(document, data, settings):
    matches = list(SECTION.finditer(document))
    old_total = len(matches)
    assert len(data) == old_total and data[POSITION - 1]["title"] != TITLE
    total = old_total + 1
    shift = lambda n: n + 1 if n >= POSITION else n
    sections = []
    for m in matches:
        old = int(m[1]); new = shift(old); section = m[0]
        section = re.sub(r'id="slide-\d+"', f'id="slide-{new}"', section, count=1)
        section = re.sub(r'aria-label="\d+\. ', f'aria-label="{new}. ', section, count=1)
        section = re.sub(r'(data-goto=")(\d+)', lambda x: x[1] + str(shift(int(x[2]))), section)
        section = re.sub(r'<small>(\d+) →</small>', lambda x: f'<small>{shift(int(x[1])):02d} →</small>', section)
        section = re.sub(r'Page (\d+)', lambda x: f'Page {shift(int(x[1])):02d}', section)
        section = re.sub(rf'<span>\d+ / {old_total}</span></footer>', f'<span>{new:02d} / {total}</span></footer>', section)
        sections.append(section)
    for row in data:
        row["number"] = shift(row["number"])
        row["text"] = re.sub(r'Page (\d+)', lambda x: f'Page {shift(int(x[1])):02d}', row["text"])
    conclusion = shift(next(s["slide"] for s in settings["sections"] if s["label"] == "Conclusion"))
    section, record = render(POSITION, total, conclusion, settings["event"]["date"], settings["presenter"])
    sections.insert(POSITION - 1, section)
    data.insert(POSITION - 1, record)
    document = document[:matches[0].start()] + "\n".join(sections) + document[matches[-1].end():]
    summary = re.search(r'talk 1–(\d+), references (\d+)–(\d+), technical backup (\d+)–(\d+)', document)
    if summary:
        a, b, c, d, _ = map(int, summary.groups())
        document = document.replace(summary[0], f"talk 1–{shift(a)}, references {shift(b)}–{shift(c)}, technical backup {shift(d)}–{total}")
    document = document.replace(f"{old_total} slides", f"{total} slides")
    for item in settings["sections"]:
        item["slide"] = shift(item["slide"])
    settings["slide_count"] = total
    catalog_path = ROOT / "papers/catalog.json"
    catalog = json.loads(catalog_path.read_text())
    for ref in catalog.get("presentation_references", []):
        if isinstance(ref.get("reference_slide"), int):
            ref["reference_slide"] = shift(ref["reference_slide"])
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    return document, data


def rerender(document, data, settings):
    matches = list(SECTION.finditer(document))
    m = next(m for m in matches if "progress-slide" in m[0].split(">", 1)[0])
    number = int(m[1])
    conclusion = next(s["slide"] for s in settings["sections"] if s["label"] == "Conclusion")
    section, record = render(number, len(matches), conclusion, settings["event"]["date"], settings["presenter"])
    data[number - 1] = record
    return document[:m.start()] + section + document[m.end():], data


def main():
    settings_path = ROOT / "presentation/settings.json"
    settings = json.loads(settings_path.read_text())
    document = DECK.read_text()
    data = json.loads(DATA.search(document)[2])
    if 'class="slide progress-slide"' in document:
        document, data = rerender(document, data, settings)
    else:
        document, data = insert(document, data, settings)
        settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
    document = DATA.sub(lambda m: m[1] + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + m[3], document, count=1)
    DECK.write_text(document)
    write_transcript(ROOT / "presentation/transcript.md", data)
    print(f"Rendered slide {POSITION} ({TITLE}); deck has {len(data)} slides.")


if __name__ == "__main__":
    main()
