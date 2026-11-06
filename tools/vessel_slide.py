"""Render the slide "How far can oxygen reach?" (organ → tissue zoom).

A 3Blue1Brown-style continuous animation on one canvas, stepped by the deck
controller (Left/Right or click):
  0 (with the title) a whole organ
  1 the organ dissolves into a zoom on its cells (scale bar 1 cm → 200 µm)
  2 one blood vessel draws itself and its oxygen reach (~0.2 mm) grows around it
  3 cells beyond that reach turn grey: they starve
  4 a branching vessel network draws in and every cell lights up again

Drawn entirely in code (no images or video); geometry is illustrative, the
0.1–0.2 mm diffusion limit is from Bishop et al., Genes & Diseases 4 (2017),
already cited on the reference slides.

First run inserts the slide right after "Why cells struggle" and renumbers
every later slide (ids, aria labels, footers, menu links, settings sections,
talk/reference ranges, catalog reference slides, speaker-notes.json,
transcript). Later runs re-render the slide in place, so edit this file and
rerun, then run tools/build_online.py.
"""
import html
import json
import re
from pathlib import Path

from deck_structure import write_transcript

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
SECTION = re.compile(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*>.*?</section>', re.S)
DATA = re.compile(r'(<script id="sourceData" type="application/json">)(.*?)(</script>)', re.S)
AFTER = "Why cells struggle"
TITLE = "How far can oxygen reach?"
SELECTOR_OLD = ".ring-slide,.publication-slide'"
SELECTOR_NEW = ".ring-slide,.publication-slide,.vessel-slide'"

CAPTIONS = [
    ("An organ measures centimetres.", "Let’s zoom in."),
    ("It is packed with living cells.", "Every single one needs oxygen."),
    ("Oxygen only reaches about 0.2 mm", "from the nearest blood vessel."),
    ("Any cell further away starves.", "A solid printed block dies from the inside."),
    ("So we have to print the vessels too.", "A network close enough to reach every cell."),
]
STEPS = len(CAPTIONS) - 1

NOTES = ("Let’s zoom in. An organ is a few centimetres big, but it is made of millions of cells, "
         "and every one of them needs oxygen. In our body, oxygen comes from the blood vessels, "
         "and it only reaches about 0.2 millimetres, one or two sheets of paper. Any cell further "
         "away starves. So if we print a solid block of tissue, it dies from the inside. "
         "That’s why we also have to print the blood vessels, a network close enough to reach every cell.")

STYLE = """<style id="vessel-slide-style">
.vessel-slide .vs-step{display:none}
.vessel-slide canvas.vs-canvas{position:absolute;inset:0;width:100%;height:100%;z-index:0;
  -webkit-mask-image:linear-gradient(180deg,transparent 0,transparent 24%,#000 40%,#000 90%,transparent 100%);
  mask-image:linear-gradient(180deg,transparent 0,transparent 24%,#000 40%,#000 90%,transparent 100%)}
.vessel-slide h1.vs-title{position:absolute;left:110px;top:96px;margin:0;font-size:68px;font-weight:400;line-height:1.1;color:#F1F5F5;z-index:1}
.vessel-slide .vs-caps{position:absolute;left:110px;top:200px;width:1300px;height:120px;z-index:1}
.vessel-slide .vs-cap{position:absolute;inset:0;opacity:0;transform:translateY(10px);transition:opacity .5s,transform .5s}
.vessel-slide .vs-cap.on{opacity:1;transform:none}
.vessel-slide .vs-cap b{display:block;font-weight:500;font-size:42px;line-height:1.2;color:#F1F5F5}
.vessel-slide .vs-cap span{display:block;font-size:30px;line-height:1.35;color:#c3c0cb;margin-top:6px}
@media print{.vessel-slide .vs-cap{opacity:0}.vessel-slide .vs-cap:last-child{opacity:1;transform:none}}
</style>"""

SCRIPT = r"""<script>(()=>{const s=document.querySelector('.vessel-slide');if(!s)return;
const cv=s.querySelector('canvas'),cx=cv.getContext('2d'),W=1920,H=1080,Q=2;cv.width=W*Q;cv.height=H*Q;cx.scale(Q,Q);
const PINK='#E394AD',CY='100,223,255',LV='180,154,216',WH='#F1F5F5',GR='#84919D',R=170,VY=650;
const T=[{z:0,v:0,b:0,d:0,br:0,bb:0},{z:1,v:0,b:0,d:0,br:0,bb:0},{z:1,v:1,b:1,d:0,br:0,bb:0},{z:1,v:1,b:1,d:1,br:0,bb:0},{z:1,v:1,b:1,d:1,br:1,bb:1}];
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches,DUR=reduce?1:1500;
const ease=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const line=(f,n)=>{const p=[];for(let i=0;i<=n;i++)p.push(f(i/n));return p};
const main=line(u=>[-60+u*2040,VY+70*Math.sin(u*5.2)+24*Math.sin(u*13)],120);
const br=[];for(let i=0;i<8;i++){const [x0,y0]=main[Math.round((i+.5)/8*120)],k=i%2?1:-1;
br.push(line(v=>[x0+k*v*50+30*Math.sin(v*6),y0-v*560],50));br.push(line(v=>[x0-k*v*45+26*Math.sin(v*5+1),y0+v*560],50))}
const pill=(x,y,w,h)=>{cx.fillStyle='rgba(5,5,6,.88)';cx.beginPath();cx.roundRect(x,y,w,h,14);cx.fill()};
const dist=(p,poly)=>{let m=1e9;for(const q of poly){const d=Math.hypot(p[0]-q[0],p[1]-q[1]);if(d<m)m=d}return m};
let seed=7;const rnd=()=>(seed=seed*16807%2147483647)/2147483647,cells=[];
for(let y=300;y<H+20;y+=34)for(let x=16;x<W;x+=34){const c=[x+(rnd()-.5)*16,y+(rnd()-.5)*16];c.dm=dist(c,main);c.db=Math.min(...br.map(b=>dist(c,b)));c.r=6+rnd()*3.5;cells.push(c)}
const poly=(p,f,w,st)=>{if(f<=0)return;const n=Math.max(2,Math.ceil(p.length*Math.min(1,f)));cx.beginPath();cx.moveTo(p[0][0],p[0][1]);
for(let i=1;i<n;i++)cx.lineTo(p[i][0],p[i][1]);cx.lineWidth=w;cx.strokeStyle=st;cx.lineCap='round';cx.lineJoin='round';cx.stroke()};
const OX=1180,OY=700;
function organ(){cx.beginPath();for(let a=0;a<=Math.PI*2+.01;a+=.03){const r=250+30*Math.sin(3*a)+16*Math.cos(5*a),x=OX+r*Math.cos(a)*1.2,y=OY+r*Math.sin(a)*.9;a?cx.lineTo(x,y):cx.moveTo(x,y)}
cx.closePath();cx.fillStyle='rgba('+LV+',.14)';cx.fill();cx.lineWidth=4;cx.strokeStyle='rgba('+LV+',.9)';cx.stroke();
cx.strokeStyle='rgba('+CY+',.6)';const tree=(x,y,a,l,d)=>{if(d>6)return;const x2=x+Math.cos(a)*l,y2=y+Math.sin(a)*l;cx.lineWidth=Math.max(1.2,5-d*.7);
cx.beginPath();cx.moveTo(x,y);cx.lineTo(x2,y2);cx.stroke();tree(x2,y2,a-.42,l*.74,d+1);tree(x2,y2,a+.42,l*.74,d+1)};tree(OX,OY+210,-Math.PI/2,110,0)}
function bar(label,len,a){if(a<=0)return;cx.globalAlpha=a;pill(W-110-len-24,H-214,len+48,90);cx.strokeStyle=WH;cx.lineWidth=4;cx.beginPath();cx.moveTo(W-110-len,H-150);cx.lineTo(W-110,H-150);cx.stroke();
cx.font='28px Jost, sans-serif';cx.fillStyle=GR;cx.textAlign='right';cx.fillText(label,W-110,H-170);cx.globalAlpha=1}
let step=0,cur={...T[0]},from={...cur},t0=0,raf=0;
function draw(now){const k=ease(Math.min(1,(now-t0)/DUR));for(const key in cur)cur[key]=from[key]+(T[step][key]-from[key])*k;
cx.clearRect(0,0,W,H);const z=cur.z;
if(z<.99){cx.save();const sc=1+z*16;cx.translate(1250,640);cx.scale(sc,sc);cx.translate(-1250,-640);cx.globalAlpha=Math.max(0,1-z*1.6);organ();cx.restore()}
if(z>.01){cx.save();const sc=.06+.94*z;cx.translate(W/2,VY);cx.scale(sc,sc);cx.translate(-W/2,-VY);cx.globalAlpha=Math.min(1,z*1.4);
poly(main,cur.v,2*R*cur.b,'rgba('+CY+',.10)');br.forEach(b=>poly(b,cur.br,2*R*cur.bb,'rgba('+CY+',.07)'));
for(const c of cells){const ok=(cur.v>.5&&c.dm<R*cur.b)||(cur.br>.05&&c.db<R*cur.bb*Math.min(1,cur.br*1.2));
cx.fillStyle=ok||cur.d<.01?'rgba('+LV+',.88)':cur.d<.5?'rgba('+LV+','+(.88-.6*cur.d)+')':'rgba(132,145,157,'+(.5-.2*cur.d)+')';
cx.beginPath();cx.arc(c[0],c[1],c.r,0,7);cx.fill()}
poly(main,cur.v,16,'rgb('+CY+')');br.forEach(b=>poly(b,cur.br,9,'rgb('+CY+')'));cx.restore();cx.globalAlpha=1}
bar('1 cm',150,1-z*2);bar('200 µm',R,z*2-1);
if(cur.b>.3&&cur.br<.15){const [vx,vy]=main[60],h=R*cur.b;cx.globalAlpha=Math.min(1,(cur.b-.3)*2)*Math.max(0,1-cur.br*7);
cx.strokeStyle=PINK;cx.lineWidth=3;cx.setLineDash([10,10]);cx.beginPath();cx.moveTo(vx,vy);cx.lineTo(vx,vy-h);cx.stroke();cx.setLineDash([]);
cx.beginPath();cx.moveTo(vx-16,vy-h);cx.lineTo(vx+16,vy-h);cx.stroke();cx.font='500 34px Jost, sans-serif';pill(vx+12,vy-h/2-26,cx.measureText('~0.2 mm').width+28,54);cx.fillStyle=PINK;cx.textAlign='left';cx.fillText('~0.2 mm',vx+26,vy-h/2+12);cx.globalAlpha=1}
if(k<1&&!s.hidden)raf=requestAnimationFrame(draw);else raf=0}
const caps=[...s.querySelectorAll('.vs-cap')];
function go(n,snap){if(n!==step||snap){from={...cur};step=n;t0=performance.now()-(snap?DUR:0);caps.forEach((c,i)=>c.classList.toggle('on',i===n))}
if(!raf)raf=requestAnimationFrame(draw)}
const count=()=>s.querySelectorAll('.vs-step.revealed').length;
const mo=new MutationObserver(()=>go(count(),false));s.querySelectorAll('.vs-step').forEach(m=>mo.observe(m,{attributes:true,attributeFilter:['class']}));
new MutationObserver(()=>{if(s.getAttribute('aria-hidden')==='false')go(count(),true)}).observe(s,{attributes:true,attributeFilter:['aria-hidden']});
go(count(),true);})();</script>"""


def visible_text():
    lines = [TITLE] + [f"{a} {b}" for a, b in CAPTIONS]
    return "\n".join(lines)


def render(number, conclusion, printing):
    nav = ('<nav class="section-nav" aria-label="Talk sections"><button data-goto="2" class="">Introduction</button>'
           f'<button data-goto="{printing}" class="current">Printing methods</button><button data-goto="{conclusion}" class="">'
           'Conclusion</button><span></span></nav>')
    caps = "".join(f'<div class="vs-cap{" on" if i == 0 else ""}"><b>{html.escape(a)}</b><span>{html.escape(b)}</span></div>'
                   for i, (a, b) in enumerate(CAPTIONS))
    markers = "".join(f'<i class="vs-step" data-reveal-step="{k}" aria-hidden="true" inert></i>' for k in range(1, STEPS + 1))
    safe_notes = NOTES.replace("--", "–")
    return (f'<section class="slide vessel-slide" id="slide-{number}" aria-label="{number}. {html.escape(TITLE)}" aria-hidden="true">'
            + nav + STYLE
            + '<canvas class="vs-canvas" role="img" aria-label="Animation: zoom from an organ to its cells; oxygen reaches about 0.2 mm around a blood vessel, cells further away starve until a vessel network is added."></canvas>'
            + f'<h1 class="vs-title">{html.escape(TITLE)}</h1><div class="vs-caps">{caps}</div>' + markers
            + f'<div class="sr-only">{html.escape(visible_text())}</div><!-- Speaker notes: {html.escape(safe_notes)} -->'
            + f'<footer><span></span><span></span><span>{number}</span></footer>' + SCRIPT + '</section>')


def add_selector(path):
    text = path.read_text()
    if SELECTOR_NEW not in text:
        assert SELECTOR_OLD in text, path
        path.write_text(text.replace(SELECTOR_OLD, SELECTOR_NEW))


def insert(document, data, settings):
    titles = [r["title"] for r in data]
    at = titles.index(AFTER) + 2  # new slide number (right after AFTER)
    matches = list(SECTION.finditer(document))
    shift = lambda n: n + 1 if n >= at else n
    conclusion = shift(next(s["slide"] for s in settings["sections"] if s["label"] == "Conclusion"))
    printing = shift(next(s["slide"] for s in settings["sections"] if s["label"] == "Printing methods"))
    sections, rows = [], []
    for i, m in enumerate(matches):
        old = i + 1
        new = shift(old)
        sec = m[0]
        sec = re.sub(r'id="slide-\d+"', f'id="slide-{new}"', sec, count=1)
        sec = re.sub(r'aria-label="\d+\. ', f'aria-label="{new}. ', sec, count=1)
        sec = re.sub(r'(data-goto=")(\d+)', lambda g: g[1] + str(shift(int(g[2]))), sec)
        sec = re.sub(r'<span>\d+</span></footer>', f'<span>{new}</span></footer>', sec)
        row = dict(data[i]); row["number"] = new
        if old == at:
            sections.append(render(at, conclusion, printing))
            rows.append({"number": at, "title": TITLE, "text": visible_text(), "notes": NOTES})
        sections.append(sec); rows.append(row)
    document = document[:matches[0].start()] + "\n".join(sections) + document[matches[-1].end():]
    total = len(rows)
    ref = titles.index("Scientific references · 1") + 2  # shifted by one
    document = re.sub(r'talk 1–\d+, references \d+–\d+', f'talk 1–{ref - 1}, references {ref}–{total}', document)
    labels = re.compile(r"\$\{i<\d+\?'TALK':i<\d+\?'REFERENCES':'BACKUP'\}")
    new_labels = f"${{i<{ref - 1}?'TALK':i<{total}?'REFERENCES':'BACKUP'}}"
    document = labels.sub(lambda _: new_labels, document)
    js = ROOT / "tools/deck.js"
    js.write_text(labels.sub(lambda _: new_labels, js.read_text()))
    for item in settings["sections"]:
        item["slide"] = shift(item["slide"])
    settings["slide_count"] = total
    catalog_path = ROOT / "papers/catalog.json"
    catalog = json.loads(catalog_path.read_text())
    for r in catalog.get("presentation_references", []):
        if isinstance(r.get("reference_slide"), int):
            r["reference_slide"] = shift(r["reference_slide"])
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    notes_path = ROOT / "presentation/speaker-notes.json"
    notes = json.loads(notes_path.read_text())
    out = {}
    for k, v in notes.items():
        out[str(shift(int(k))) if k.isdigit() else k] = v
    out[str(at)] = NOTES
    ordered = {k: out[k] for k in sorted(out, key=lambda k: (k.isdigit(), int(k) if k.isdigit() else 0))}
    notes_path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n")
    return document, rows


def rerender(document, data, settings):
    m = re.search(r'<section class="slide vessel-slide" id="slide-(\d+)".*?</section>', document, re.S)
    number = int(m[1])
    conclusion = next(s["slide"] for s in settings["sections"] if s["label"] == "Conclusion")
    printing = next(s["slide"] for s in settings["sections"] if s["label"] == "Printing methods")
    document = document[:m.start()] + render(number, conclusion, printing) + document[m.end():]
    for r in data:
        if r["number"] == number:
            r.update(title=TITLE, text=visible_text(), notes=NOTES)
    return document, data


def main():
    settings_path = ROOT / "presentation/settings.json"
    settings = json.loads(settings_path.read_text())
    document = DECK.read_text()
    data = json.loads(DATA.search(document)[2])
    if 'class="slide vessel-slide"' in document:
        document, data = rerender(document, data, settings)
    else:
        document, data = insert(document, data, settings)
        settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
    document = DATA.sub(lambda g: g[1] + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + g[3], document, count=1)
    DECK.write_text(document)
    add_selector(DECK)
    add_selector(ROOT / "tools/deck.js")
    write_transcript(ROOT / "presentation/transcript.md", data)
    print(f"Vessel slide rendered; deck has {len(data)} slides.")


if __name__ == "__main__":
    main()
