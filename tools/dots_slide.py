"""Render the slide "Behind the numbers" (organ shortage as dots), right after
"The organ shortage persists".

One dot = 1,000. Steps (Left/Right or click):
  0 (with the title) 533 lavender dots pop in: 532,905 waiting-list entries, end of 2025
  1 184 cyan dots: 183,879 transplant procedures in 2025
  2 40 pink dots that fade to rings: 40,019 deaths on waiting lists in 2025
  3 closing question

Figures: EDQM–ONT Newsletter Transplant 2026 (2025 data), as on the chart slide
(data/organ-transplants). Waiting-list figures are summed organ-list entries, not
deduplicated patients, so the wording says "entries" / "deaths on waiting lists".
Dots are rounded to the nearest 1,000.

First run inserts the slide (tools/slide_insert.py renumbers later slides);
later runs re-render it in place. Then run tools/build_online.py.
"""
import html
import json
from pathlib import Path

from slide_insert import insert_or_rerender, nav

ROOT = Path(__file__).resolve().parents[1]
CLS = "dots-slide"
AFTER = "The organ shortage persists"
TITLE = "Behind the numbers"
WAITING, TRANSPLANTS, DEATHS = 532_905, 183_879, 40_019
CAPTIONS = [
    ("Every dot is 1,000 entries on organ waiting lists", "Worldwide reports, end of 2025."),
    ("183,879 transplants in the whole year", "Roughly one for every three entries still waiting."),
    ("40,019 deaths on waiting lists", "About 110 every day."),
    ("There are not enough organs.", "What if we could print them?"),
]
NOTES = ("Let’s look at what these numbers mean. Every dot is a thousand entries on organ waiting lists at the end of 2025, "
         "more than half a million. In the whole year, about 184,000 transplants were done, roughly one for every three still waiting. "
         "And 40,000 deaths were reported on waiting lists, about 110 every day. There simply are not enough organs. "
         "So what if we could print them?")


def _check_figures():
    data = json.loads((ROOT / "data/organ-transplants/annual_counts.json").read_text())
    text = json.dumps(data)
    for n in (TRANSPLANTS,):
        assert str(n) in text, f"{n} not found in data/organ-transplants/annual_counts.json"


STYLE = """<style id="dots-slide-style">
.dots-slide .ds-step{display:none}
.dots-slide canvas.ds-canvas{position:absolute;inset:0;width:100%;height:100%;z-index:0}
.dots-slide h1.ds-title{position:absolute;left:110px;top:96px;margin:0;font-size:68px;font-weight:400;line-height:1.1;color:#F1F5F5;z-index:1}
.dots-slide .ds-caps{position:absolute;left:110px;top:200px;width:1500px;height:110px;z-index:1}
.dots-slide .ds-cap{position:absolute;inset:0;opacity:0;transform:translateY(10px);transition:opacity .5s,transform .5s}
.dots-slide .ds-cap.on{opacity:1;transform:none}
.dots-slide .ds-cap b{display:block;font-weight:500;font-size:42px;line-height:1.2;color:#F1F5F5}
.dots-slide .ds-cap span{display:block;font-size:30px;line-height:1.35;color:#c3c0cb;margin-top:6px}
@media print{.dots-slide .ds-cap{opacity:0}.dots-slide .ds-cap:last-child{opacity:1;transform:none}}
</style>"""

SCRIPT = r"""<script>(()=>{const s=document.querySelector('.dots-slide');if(!s)return;
const cv=s.querySelector('canvas'),cx=cv.getContext('2d'),W=1920,H=1080,Q=2;cv.width=W*Q;cv.height=H*Q;cx.scale(Q,Q);
const LV='180,154,216',CY='100,223,255',PK='227,148,173',WH='#F1F5F5',MU='#99A3AE';
const N=[__W__,__T__,__D__],K=N.map(n=>Math.round(n/1000)),G=28,R=10,TOP=430;
const grids=[{x:110,cols:26,col:LV,label:'waiting-list entries',sub:'end of 2025'},{x:980,cols:14,col:CY,label:'transplants',sub:'in 2025'},{x:1480,cols:8,col:PK,label:'deaths on waiting lists',sub:'in 2025'}];
let seed=5;const rnd=()=>(seed=seed*16807%2147483647)/2147483647;
grids.forEach((g,i)=>{g.dots=[];for(let k=0;k<K[i];k++){const c=k%g.cols,r=Math.floor(k/g.cols);g.dots.push({x:g.x+R+c*G,y:TOP+R+r*G,d:rnd()})}
  const o=g.dots.map((_,k)=>k).sort(()=>rnd()-.5);o.forEach((k,j)=>g.dots[k].o=j/g.dots.length)});
const D=[2.4,2.0,2.6,1.2],reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
const cl=x=>Math.max(0,Math.min(1,x)),back=x=>{x=cl(x);const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)},ease=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2};
let step=0,st=[0,null,null,null],raf=0;
const P=(k,now)=>reduce?(k<=step?1:0):st[k]==null?0:cl((now-st[k])/1000/D[k]);
const fmt=n=>Math.round(n).toLocaleString('en-US');
function draw(now){cx.clearRect(0,0,W,H);let busy=false;
 const p=[0,1,2,3].map(k=>P(k,now));p.forEach((v,k)=>{if(k<=step&&v<1)busy=true});
 const dim=ease(p[3]);
 grids.forEach((g,i)=>{const q=p[i];if(q<=0)return;
  const a=i===0?1-.55*dim:i===1?1:1;
  g.dots.forEach(d=>{const t=cl((q-d.o*.75)/.25);if(t<=0)return;const sc=back(t);
   if(i===2){const f=ease((q-.55-d.o*.3)/.3);cx.globalAlpha=a;cx.fillStyle='rgba('+g.col+','+(1-f*.85)+')';cx.beginPath();cx.arc(d.x,d.y,R*sc,0,7);cx.fill();
    cx.strokeStyle='rgba('+g.col+','+(.9*f)+')';cx.lineWidth=2;cx.beginPath();cx.arc(d.x,d.y,R*sc,0,7);cx.stroke();cx.globalAlpha=1}
   else{cx.globalAlpha=a;cx.fillStyle='rgba('+g.col+',.92)';cx.beginPath();cx.arc(d.x,d.y,R*sc,0,7);cx.fill();cx.globalAlpha=1}});
  const la=cl(q*3);cx.globalAlpha=la*(i===0?1-.4*dim:1);
  cx.font='500 48px Jost, sans-serif';cx.textAlign='left';cx.fillStyle='rgb('+g.col+')';cx.fillText(fmt(N[i]*ease(q/.85)),g.x,TOP-62);
  cx.font='26px Jost, sans-serif';cx.fillStyle=MU;cx.fillText(g.label+' · '+g.sub,g.x,TOP-24);cx.globalAlpha=1});
 raf=busy?requestAnimationFrame(draw):0}
const caps=[...s.querySelectorAll('.ds-cap')],count=()=>s.querySelectorAll('.ds-step.revealed').length;
function go(n,snap){const now=performance.now();if(snap){for(let k=0;k<4;k++)st[k]=k<=n?now-1e6:null;if(n===0)st[0]=now}
 else if(n>step){for(let k=step+1;k<=n;k++)st[k]=k===n?now:now-1e6}else{for(let k=n+1;k<4;k++)st[k]=null}
 step=n;caps.forEach((c,i)=>c.classList.toggle('on',i===n));cancelAnimationFrame(raf);raf=requestAnimationFrame(draw)}
const mo=new MutationObserver(()=>go(count(),false));s.querySelectorAll('.ds-step').forEach(m=>mo.observe(m,{attributes:true,attributeFilter:['class']}));
new MutationObserver(()=>{if(s.getAttribute('aria-hidden')==='false')go(count(),true)}).observe(s,{attributes:true,attributeFilter:['aria-hidden']});
go(count(),true);})();</script>"""


def visible_text():
    return "\n".join([TITLE] + [f"{a} {b}" for a, b in CAPTIONS])


def render(number, conclusion, printing):
    caps = "".join(f'<div class="ds-cap{" on" if i == 0 else ""}"><b>{html.escape(a)}</b><span>{html.escape(b)}</span></div>'
                   for i, (a, b) in enumerate(CAPTIONS))
    markers = "".join(f'<i class="ds-step" data-reveal-step="{k}" aria-hidden="true" inert></i>' for k in range(1, len(CAPTIONS)))
    script = SCRIPT.replace("__W__", str(WAITING)).replace("__T__", str(TRANSPLANTS)).replace("__D__", str(DEATHS))
    return (f'<section class="slide canvas-step-slide {CLS}" id="slide-{number}" aria-label="{number}. {html.escape(TITLE)}" aria-hidden="true">'
            + nav(conclusion, printing, "Introduction") + STYLE
            + '<canvas class="ds-canvas" role="img" aria-label="Dot chart, one dot per 1,000: 533 dots for waiting-list entries at the end of 2025, 184 for transplants in 2025, 40 for deaths on waiting lists in 2025."></canvas>'
            + f'<h1 class="ds-title">{html.escape(TITLE)}</h1><div class="ds-caps">{caps}</div>' + markers
            + f'<div class="sr-only">{html.escape(visible_text())}</div><!-- Speaker notes: {html.escape(NOTES.replace("--", "–"))} -->'
            + f'<footer><span></span><span></span><span>{number}</span></footer>' + script + '</section>')


if __name__ == "__main__":
    _check_figures()
    total = insert_or_rerender(CLS, AFTER, render, TITLE, visible_text(), NOTES)
    print(f"Dots slide rendered; deck has {total} slides.")
