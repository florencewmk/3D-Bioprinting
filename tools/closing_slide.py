"""Render the closing slide (9 Nov 2026): "Engineering tomorrow’s possibilities." in dots.

Replaces the slide titled "Thank You!" (class closing-thanks) in place. The tree slide
"Engineering tomorrow’s possibilities" was merged into this one and then removed with
tools/delete_slides.py.
  0 (on entry) a few thousand dots fly in and settle into the three lines; the last line
    uses the pink → lavender → cyan gradient; "Florence Wong" fades in underneath
  1 the words glide left and the GitHub QR code appears on the right
Rerun to re-render in place, then tools/archive_materials.py and tools/build_online.py.
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
TITLE = "Engineering tomorrow’s possibilities"
LINES = ["Engineering", "tomorrow’s", "possibilities."]
NAME = "Florence Wong"
REPO = "https://github.com/florencewmk/3D-Bioprinting"
NOTES = ("With that, I’ll leave you with a quote, from me to all of you: engineering tomorrow’s possibilities.\n\n"
         "Stay curious, stay motivated.\n\n"
         "[Next: the GitHub link and QR code.] Thank you for today, and I hope you enjoyed it. "
         "I’ve also uploaded this presentation and all the sources to my GitHub.")

STYLE = """<style id="end-slide-style">
.end-slide .es-step{display:none}
.end-slide canvas.es-canvas{position:absolute;inset:0;width:100%;height:100%;z-index:0}
.end-slide .es-name{position:absolute;left:0;right:0;top:770px;text-align:center;font-size:30px;color:#84919D;opacity:0;z-index:1;transition:opacity .8s,right .9s cubic-bezier(.6,0,.2,1)}
.end-slide .es-name.on{opacity:1}.end-slide .es-name.left{right:660px}
.end-slide .es-qr{position:absolute;left:1290px;top:330px;width:420px;text-align:center;z-index:2;opacity:0;transform:translateY(16px) scale(.97);transition:opacity .7s .35s,transform .7s .35s;pointer-events:none}
.end-slide .es-qr.on{opacity:1;transform:none;pointer-events:auto}
.end-slide .es-qr a{color:#64DFFF;text-decoration:none}
.end-slide .es-card{width:300px;height:300px;margin:0 auto;border-radius:24px;background:#F1F5F5;display:grid;place-items:center;box-shadow:0 0 0 1px rgba(255,255,255,.1),0 0 80px rgba(180,154,216,.35),0 0 140px rgba(100,223,255,.18)}
.end-slide .es-card img{width:252px;height:252px;image-rendering:pixelated}
.end-slide .es-qr p{margin:26px 0 0;font-size:24px;color:#c3c0cb}
.end-slide .es-qr span{display:inline-block;margin-top:8px;font-size:22px}
@media print{.end-slide .es-qr,.end-slide .es-name{opacity:1;transform:none}}
</style>"""

SCRIPT = r"""<script>(()=>{const s=document.querySelector('.end-slide');if(!s)return;
const cv=s.querySelector('canvas.es-canvas'),cx=cv.getContext('2d'),W=1920,H=1080,Q=1.5;cv.width=W*Q;cv.height=H*Q;
const LINES=__LINES__,FS=140,LH=168,TOP=330,SHIFT=330,name=s.querySelector('.es-name'),qr=s.querySelector('.es-qr');
const cl=x=>Math.max(0,Math.min(1,x)),ease=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
let seed=3;const rnd=()=>(seed=seed*16807%2147483647)/2147483647;
const stops=[[227,148,173],[180,154,216],[100,223,255]];
const grad=u=>{const k=u<.5?0:1,f=u<.5?u*2:(u-.5)*2,a=stops[k],b=stops[k+1];return a.map((v,i)=>Math.round(v+(b[i]-v)*f))};
let P=[],step=0,t0=0,raf=0,ready=false,nameT=0;
function build(){const o=document.createElement('canvas');o.width=W;o.height=H;const g=o.getContext('2d');g.font='500 '+FS+'px Jost';g.textAlign='center';g.textBaseline='middle';
 LINES.forEach((t,li)=>{g.clearRect(0,0,W,H);g.fillStyle='#fff';g.fillText(t,960,TOP+li*LH);const w=g.measureText(t).width,x0=960-w/2,d=g.getImageData(0,0,W,H).data;
  for(let y=TOP+li*LH-FS;y<TOP+li*LH+FS;y+=5)for(let x=0;x<W;x+=5)if(d[(y*W+x)*4+3]>140){const u=cl((x-x0)/w),last=li===LINES.length-1;
   const c=last?grad(u):[241-8*u,245-12*u,245];P.push({a:[x,y],b:[x-SHIFT,y],d:rnd()*.45+li*.25+u*.25,ph:rnd()*6.283,r:1.7+rnd()*1.1,c,x:0,y:0,sx:0,sy:0})}});ready=true}
function scatter(){P.forEach(p=>{const ang=rnd()*6.283,r=600+rnd()*900;p.x=p.sx=960+Math.cos(ang)*r;p.y=p.sy=540+Math.sin(ang)*r*.6})}
function go(n,snap){const now=performance.now();if(!ready)return;
 if(snap){if(n===0)scatter();else P.forEach(p=>{p.x=p.sx=p.b[0];p.y=p.sy=p.b[1]});}
 else P.forEach(p=>{p.sx=p.x;p.sy=p.y});
 step=n;t0=snap&&n>0?now-5e3:now;name.classList.toggle('left',n===1);qr.classList.toggle('on',n===1);
 if(snap){name.classList.remove('on');clearTimeout(nameT);nameT=setTimeout(()=>name.classList.add('on'),n===0?2600:0)}
 if(!raf&&s.classList.contains('active'))raf=requestAnimationFrame(frame)}
function frame(now){if(!s.classList.contains('active')){raf=0;return}cx.setTransform(Q,0,0,Q,0,0);cx.clearRect(0,0,W,H);const t=(now-t0)/1000;
 for(const p of P){const tg=step===0?p.a:p.b,dur=step===0?1.9:1.0,dl=step===0?p.d:p.d*.2,k=ease(cl((t-dl)/dur)),bx=Math.sin(now/900+p.ph)*1.1*k,by=Math.cos(now/1100+p.ph)*1.1*k;
  p.x=p.sx+(tg[0]-p.sx)*k+bx;p.y=p.sy+(tg[1]-p.sy)*k+by;cx.fillStyle=`rgba(${p.c[0]|0},${p.c[1]|0},${p.c[2]|0},${step===0?.25+.75*k:1})`;cx.beginPath();cx.arc(p.x,p.y,p.r,0,7);cx.fill()}
 raf=requestAnimationFrame(frame)}
const count=()=>s.querySelectorAll('.es-step.revealed').length;
const mo=new MutationObserver(()=>go(count()));s.querySelectorAll('.es-step').forEach(m=>mo.observe(m,{attributes:true,attributeFilter:['class']}));
let active=false;new MutationObserver(()=>{const a=s.classList.contains('active');if(a&&!active)go(count(),true);active=a}).observe(s,{attributes:true,attributeFilter:['class']});
document.fonts.load('500 140px Jost').then(()=>{build();active=s.classList.contains('active');go(count(),true)});})();</script>"""


def render(number, qr_src):
    text = " ".join(LINES)
    return (f'<section class="slide canvas-step-slide closing-slide end-slide" id="slide-{number}" aria-label="{number}. {html.escape(TITLE)}" aria-hidden="true">'
            + STYLE
            + f'<canvas class="es-canvas" role="img" aria-label="{html.escape(text)} written in coloured dots"></canvas>'
            + f'<div class="es-name">{html.escape(NAME)}</div>'
            + f'<div class="es-qr"><a href="{REPO}" target="_blank" rel="noopener"><div class="es-card"><img src="{qr_src}" alt="QR code for the 3D Bioprinting GitHub repository"></div>'
            + '<p>Slides, sources and the bioprinting map</p><span>github.com/florencewmk/3D-Bioprinting</span></a></div>'
            + '<i class="es-step" data-reveal-step="1" aria-hidden="true" inert></i>'
            + f'<div class="sr-only">{html.escape(text)}\n{html.escape(NAME)}\n{REPO}</div>'
            + f'<!-- Speaker notes: {html.escape(NOTES.replace(chr(10) * 2, " "))} -->'
            + f'<footer><span></span><span></span><span>{number}</span></footer>'
            + SCRIPT.replace("__LINES__", json.dumps(LINES, ensure_ascii=False)) + '</section>')


def main():
    document = DECK.read_text()
    rows = json.loads(DATA.search(document)[2])

    def replace(m):
        sec = m[0]
        if 'closing-thanks' not in sec and 'end-slide' not in sec:
            return sec
        qr = re.search(r'<img[^>]*src="(data:image/png;base64,[^"]+)"', sec)[1]
        n = int(m[1])
        rows[n - 1].update(title=TITLE, text=" ".join(LINES) + f"\n{NAME}\n{REPO}", notes=NOTES)
        return render(n, qr)

    document = SECTION.sub(replace, document)
    document = DATA.sub(lambda m: m[1] + json.dumps(rows, ensure_ascii=False).replace('</', '<\\/') + m[3], document, count=1)
    DECK.write_text(document)
    write_transcript(ROOT / "presentation/transcript.md", rows)
    print("Closing slide rendered.")


if __name__ == "__main__":
    main()
