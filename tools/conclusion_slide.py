"""Render the conclusion slide "Take-home summary" (light ring).

A ring closes in four arcs, one per takeaway (Why, How, Today, Next); the first
point shows with the title, Left/Right steps the rest, and the fourth point
closes the ring. The Readily3D volumetric printing loop plays on its own,
looping, in a card on the right (three columns: ring, points, video;
tools/conclusion-slide/).

First run replaces "Precision is a beginning" with this slide and deletes the
old backup diagram "Layers to living tissue", renumbering every later slide
(ids, footers, menu links, Contents pages, settings, catalog, transcript).
Later runs re-render the slide in place, so edit this file and rerun.
"""
import base64
import html
import json
import math
import re
from pathlib import Path

from deck_structure import write_transcript

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
ASSETS = ROOT / "tools/conclusion-slide"
SECTION = re.compile(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>.*?</section>', re.S)
DATA = re.compile(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', re.S)
REPLACES = "Precision is a beginning"
REMOVES = "Layers to living tissue"
TITLE = "Take-home summary"
TITLE_HTML = 'Take-home <em class="gradient">summary</em>'

# label in ring, ring word, headline, detail, colour
POINTS = [
    ("WHY", "Need", "Transplant demand outpaces donors",
     "532,905 waiting · 40,019 deaths on waiting lists (2025)", "#E394AD"),
    ("HOW", "Build", "Living cells in a gel, layer by layer",
     "Light, cure, repeat", "#B49AD8"),
    ("TODAY", "Research", "Lab successes, first steps in patients",
     "Printed vessels in the lab · a bioprinted ear implanted (2022)", "#64DFFF"),
    ("NEXT", "Future", "Tissues in ~10 years, organs in 20–30",
     "AI may speed up development", "#70C2BC"),
]
FINAL = "Not yet. But closer."
SOURCE = ("Source: EDQM–ONT Newsletter Transplant (2026) · Wyss Institute (2024) · 3DBio (2022) · "
          "Skylar-Scott, Stanford, via 3DPrint.com (2025) · Video: Readily3D, Tomolite")
PROVENANCE = {
    "bg-volumetric.mp4": "Readily3D Tomolite volumetric bioprinting animation (20200930_PROZESS_ANIMATION_LOOP_01, "
                         "also on the former slide 'Precision is a beginning'); audio removed and re-encoded "
                         "(H.264, CRF 28) on 4 November 2026; shown as a looping card beside the conclusion ring since 5 November 2026. Credited on the slide.",
}
NOTES = """To take home:

Why do we need it? Because transplant demand outpaces donors. More than half a million people are waiting, and forty thousand died on waiting lists last year.

How does it work? We print living cells in a gel, layer by layer. With light: expose, cure, repeat.

Where are we today? There are real successes in the lab, like printed blood vessels, and the first steps in patients, like the printed ear in 2022.

What comes next? Experts expect simple tissues in about ten years, and whole organs in twenty to thirty. AI may help speed up the development."""

R = 112


def xy(deg):
    a = math.radians(deg - 90)
    return f"{150 + R * math.cos(a):.2f} {150 + R * math.sin(a):.2f}"


STYLE = """<style id="ring-slide-style">
.ring-slide .rs-card{position:absolute;left:1310px;top:236px;width:550px;height:668px;margin:0;border-radius:28px;overflow:hidden;z-index:2;background:#02040c;box-shadow:0 0 90px #3a4cff40,inset 0 0 0 1px #F1F5F526}
.ring-slide .rs-card video{width:100%;height:100%;object-fit:cover;object-position:52% 50%;pointer-events:none}
.ring-slide .rs-step{display:none}
.ring-slide h1.rs-title{position:absolute;left:110px;top:96px;margin:0;font-size:68px;font-weight:400;line-height:1.1;color:#F1F5F5;z-index:2}
.ring-slide h1.rs-title em{font-style:normal}
.ring-slide svg.rs-ring{position:absolute;left:60px;top:300px;width:540px;height:540px;z-index:2;overflow:visible}
.ring-slide svg.rs-ring text{font-family:'Jost',sans-serif}
.ring-slide .rs-points{position:absolute;left:610px;width:670px;top:236px;height:668px;display:flex;flex-direction:column;justify-content:center;gap:44px;z-index:2}
.ring-slide .rs-pt{opacity:0;transform:translateX(24px);transition:opacity .6s ease,transform .6s ease}
.ring-slide .rs-pt.on{opacity:1;transform:none}
.ring-slide .rs-pt.on.past{opacity:.38}
.ring-slide .rs-pt b{display:block;font-size:36px;font-weight:500;line-height:1.2}
.ring-slide .rs-pt span{display:block;font-size:23px;line-height:1.35;color:#F1F5F5;opacity:.72;margin-top:8px}
.ring-slide .refs{position:absolute;left:70px;right:70px;bottom:60px;margin:0;font-size:16px;line-height:1.45;color:#84919D;z-index:2}
@media(prefers-reduced-motion:reduce){.ring-slide .rs-pt{transition:none}}
</style>"""

SCRIPT = """<script>(()=>{const s=document.querySelector('.ring-slide');if(!s)return;
const P=%s,FINAL=%s,R=%d,v=s.querySelector('.rs-card video'),spot=s.querySelector('.rs-spot'),c1=s.querySelector('.rs-c1'),c2=s.querySelector('.rs-c2');
const arcs=[...s.querySelectorAll('.rs-arc')],pts=[...s.querySelectorAll('.rs-pt')];let deg=0,raf,active=false;
const xy=d=>{const a=(d-90)*Math.PI/180;return[150+R*Math.cos(a),150+R*Math.sin(a)]};
const paint=()=>{const[x,y]=xy(deg);spot.setAttribute('cx',x);spot.setAttribute('cy',y);arcs.forEach((a,i)=>{const k=Math.max(0,Math.min(1,(deg-i*90-4)/82));a.setAttribute('stroke-dashoffset',1-k);a.style.opacity=k>0.005?1:0})};
const go=to=>{cancelAnimationFrame(raf);const from=deg,t0=performance.now(),still=matchMedia('(prefers-reduced-motion: reduce)').matches;
const f=t=>{const k=still?1:Math.min(1,(t-t0)/1100);deg=from+(to-from)*(1-Math.pow(1-k,3));paint();if(k<1)raf=requestAnimationFrame(f)};raf=requestAnimationFrame(f)};
const sync=()=>{const n=s.querySelectorAll('.rs-step.revealed').length,fin=false;s.dataset.rs=n;
pts.forEach((p,i)=>{p.classList.toggle('on',fin||i<=n);p.classList.toggle('past',!fin&&i<n)});
c1.textContent=fin?'':P[n][0];c1.setAttribute('fill',fin?'#F1F5F5':P[n][4]);c2.textContent=fin?FINAL:P[n][1];go(fin?360:(n+1)*90)};
const slow=()=>{if(v)v.playbackRate=1};v?.addEventListener('ended',()=>{v.currentTime=0;v.play().catch(()=>{})});v?.addEventListener('loadedmetadata',slow);v?.addEventListener('play',slow);
const watch=()=>{const a=s.classList.contains('active');if(a&&!active){deg=0;paint();sync();if(v){slow();v.play().catch(()=>{})}}if(!a&&active&&v)v.pause();active=a};
const mo=new MutationObserver(sync);s.querySelectorAll('.rs-step').forEach(m=>mo.observe(m,{attributes:true,attributeFilter:['class']}));
new MutationObserver(watch).observe(s,{attributes:true,attributeFilter:['class']});paint();sync();watch();})();</script>"""


def render(number, total, conclusion, date, presenter):
    video = "data:video/mp4;base64," + base64.b64encode((ASSETS / "bg-volumetric.mp4").read_bytes()).decode()
    arcs = "".join(
        f'<path class="rs-arc" d="M{xy(i * 90 + 4)} A{R} {R} 0 0 1 {xy(i * 90 + 86)}" fill="none" stroke="{p[4]}" '
        'stroke-width="7" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" style="opacity:0"/>'
        for i, p in enumerate(POINTS))
    ring = ('<svg class="rs-ring" viewBox="0 0 300 300" aria-hidden="true">'
            f'<circle cx="150" cy="150" r="{R}" fill="none" stroke="#F1F5F5" stroke-opacity=".12" stroke-width="7"/>'
            + arcs + f'<circle class="rs-spot" r="5.5" cx="150" cy="{150 - R}" fill="#F1F5F5"/>'
            '<text class="rs-c1" x="150" y="140" text-anchor="middle" style="font-size:12px;letter-spacing:3px"></text>'
            '<text class="rs-c2" x="150" y="168" text-anchor="middle" fill="#F1F5F5" style="font-size:19px"></text></svg>')
    points = "".join(
        f'<div class="rs-pt"><b style="color:{p[4]}">{html.escape(p[2])}</b><span>{html.escape(p[3])}</span></div>'
        for p in POINTS)
    markers = "".join(f'<i class="rs-step" data-reveal-step="{k}" aria-hidden="true" inert></i>'
                      for k in range(1, len(POINTS)))
    text = "\n".join([TITLE] + [f"{p[2]}\n{p[3]}" for p in POINTS] + [SOURCE])
    nav = ('<nav class="section-nav" aria-label="Talk sections"><button data-goto="3" class="">Introduction</button>'
           f'<button data-goto="8" class="">Printing methods</button><button data-goto="{conclusion}" class="current">'
           'Conclusion</button><span></span></nav>')
    section = (
        f'<section class="slide ring-slide" data-rs="0" id="slide-{number}" aria-label="{number}. {html.escape(TITLE)}" aria-hidden="true">'
        + nav + STYLE
        + f'<h1 class="rs-title">{TITLE_HTML}</h1>{ring}<div class="rs-points">{points}</div>'
        + f'<figure class="rs-card" aria-hidden="true"><video autoplay muted loop playsinline preload="auto" src="{video}"></video></figure>'
        + f'<p class="refs">{html.escape(SOURCE)}</p>' + markers
        + f'<div class="sr-only">{html.escape(text)}</div><!-- Speaker notes: {html.escape(NOTES)} -->'
        + f'<footer><span>{date}</span><span>{presenter}</span><span>{number:02d} / {total}</span></footer>'
        + SCRIPT % (json.dumps(POINTS, ensure_ascii=False), json.dumps(FINAL), R) + "</section>")
    return section, {"number": number, "title": TITLE, "text": text, "notes": NOTES}


def remove(document, data, settings, removed):
    """Delete slide `removed` and renumber every later slide."""
    matches = list(SECTION.finditer(document))
    old_total = len(matches)
    total = old_total - 1
    shift = lambda n: n - 1 if n > removed else n
    sections = []
    for m in matches:
        old = int(m[1])
        if old == removed:
            continue
        new = shift(old); section = m[0]
        assert f'data-goto="{removed}"' not in section, "a link points at the removed slide"
        section = re.sub(r'id="slide-\d+"', f'id="slide-{new}"', section, count=1)
        section = re.sub(r'aria-label="\d+\. ', f'aria-label="{new}. ', section, count=1)
        section = re.sub(r'(data-goto=")(\d+)', lambda x: x[1] + str(shift(int(x[2]))), section)
        section = re.sub(r'<small>(\d+) →</small>', lambda x: f'<small>{shift(int(x[1])):02d} →</small>', section)
        section = re.sub(r'Page (\d+)', lambda x: f'Page {shift(int(x[1])):02d}', section)
        section = re.sub(rf'<span>\d+ / {old_total}</span></footer>', f'<span>{new:02d} / {total}</span></footer>', section)
        sections.append(section)
    data = [row for row in data if row["number"] != removed]
    for row in data:
        row["number"] = shift(row["number"])
        row["text"] = re.sub(r'Page (\d+)', lambda x: f'Page {shift(int(x[1])):02d}', row["text"])
    document = document[:matches[0].start()] + "\n".join(sections) + document[matches[-1].end():]
    titles = [r["title"] for r in data]
    ref_start = titles.index("Scientific references · 1") + 1
    backup_start = titles.index("Technical backup") + 1
    document = re.sub(r'talk 1–\d+, references \d+–\d+, technical backup \d+–\d+',
                      f'talk 1–{ref_start - 1}, references {ref_start}–{backup_start - 1}, technical backup {backup_start}–{total}', document)
    document = document.replace(f"{old_total} slides", f"{total} slides")
    labels = re.compile(r"\$\{i<\d+\?'TALK':i<\d+\?'REFERENCES':'BACKUP'\}")
    new_labels = f"${{i<{ref_start - 1}?'TALK':i<{backup_start - 1}?'REFERENCES':'BACKUP'}}"
    document = labels.sub(lambda _: new_labels, document)
    js = ROOT / "tools/deck.js"
    js.write_text(labels.sub(lambda _: new_labels, js.read_text()))
    for item in settings["sections"]:
        item["slide"] = shift(item["slide"])
    if "slide_count" in settings:
        settings["slide_count"] = total
    catalog_path = ROOT / "papers/catalog.json"
    catalog = json.loads(catalog_path.read_text())
    for ref in catalog.get("presentation_references", []):
        if isinstance(ref.get("reference_slide"), int):
            ref["reference_slide"] = shift(ref["reference_slide"])
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    return document, data


def place(document, data, settings, number):
    matches = list(SECTION.finditer(document))
    m = matches[number - 1]
    conclusion = next(s["slide"] for s in settings["sections"] if s["label"] == "Conclusion")
    section, record = render(number, len(matches), conclusion, settings["event"]["date"], settings["presenter"])
    data[number - 1] = record
    return document[:m.start()] + section + document[m.end():], data


def main():
    settings_path = ROOT / "presentation/settings.json"
    settings = json.loads(settings_path.read_text())
    document = DECK.read_text()
    data = json.loads(DATA.search(document)[2])
    titles = [r["title"] for r in data]
    if 'class="slide ring-slide"' in document:
        number = next(int(m[1]) for m in SECTION.finditer(document) if "ring-slide" in m[0].split(">", 1)[0])
    else:
        number = titles.index(REPLACES) + 1
        if REMOVES in titles:
            removed = titles.index(REMOVES) + 1
            assert removed > number
            document, data = remove(document, data, settings, removed)
            settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
    document, data = place(document, data, settings, number)
    document = DATA.sub(lambda m: m[1] + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + m[3], document, count=1)
    DECK.write_text(document)
    write_transcript(ROOT / "presentation/transcript.md", data)
    print(f"Rendered slide {number} ({TITLE}); deck has {len(data)} slides.")


if __name__ == "__main__":
    main()
