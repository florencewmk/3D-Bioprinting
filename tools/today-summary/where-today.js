(()=>{const s=document.querySelector('.progress-slide');if(!s)return;const cv=s.querySelector('canvas.wt-canvas'),cx=cv.getContext('2d'),W=1920,H=1080,Q=1.5;cv.width=W*Q;cv.height=H*Q;
const CY='100,223,255',LV='180,154,216',PK='227,148,173',MT='112,194,188',WH='241,245,245',GR='132,145,157';
const ease=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2,cl=x=>Math.max(0,Math.min(1,x));
let seed=11;const rnd=()=>(seed=seed*16807%2147483647)/2147483647;
const bez=(a,b,c,d,n=40)=>{const p=[];for(let i=0;i<=n;i++){const t=i/n,u=1-t;p.push([u*u*u*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t*t*t*d[0],u*u*u*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t*t*t*d[1]])}return p};
const chain=(...segs)=>segs.reduce((acc,s)=>acc.concat(acc.length?s.slice(1):s),[]);
function stroke(p,f,col,w,dash){f=cl(f);if(f<=0)return;const n=Math.max(2,Math.ceil(p.length*f));cx.save();cx.strokeStyle=col;cx.lineWidth=w;cx.lineCap='round';cx.lineJoin='round';if(dash)cx.setLineDash(dash);cx.beginPath();cx.moveTo(p[0][0],p[0][1]);for(let i=1;i<n;i++)cx.lineTo(p[i][0],p[i][1]);cx.stroke();cx.restore()}
function inside(pt,poly){let c=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const [xi,yi]=poly[i],[xj,yj]=poly[j];if(((yi>pt[1])!=(yj>pt[1]))&&(pt[0]<(xj-xi)*(pt[1]-yi)/(yj-yi)+xi))c=!c}return c}
function fillCells(poly,step,r){const xs=poly.map(p=>p[0]),ys=poly.map(p=>p[1]),out=[];for(let y=Math.min(...ys);y<Math.max(...ys);y+=step)for(let x=Math.min(...xs);x<Math.max(...xs);x+=step){const p=[x+(rnd()-.5)*step*.45,y+(rnd()-.5)*step*.45];if(inside(p,poly))out.push({p,d:rnd(),r})}return out}
function cells(list,f,col){for(const c of list){const a=cl((f-c.d*.6)/.4);if(a<=0)continue;const r=c.r*(.6+.4*ease(a));cx.globalAlpha*=1;cx.strokeStyle=`rgba(${col},${.9*a})`;cx.lineWidth=1.6;cx.beginPath();cx.arc(c.p[0],c.p[1],r,0,7);cx.stroke();cx.fillStyle=`rgba(${col},${a})`;cx.beginPath();cx.arc(c.p[0],c.p[1],r*.32,0,7);cx.fill()}}
let SC=1;function label(t,x,y,f,col='132,145,157',al='center'){if(f<=0||SC<.6)return;cx.fillStyle=`rgba(${col},${cl(f)})`;cx.font='300 22px Jost';cx.textAlign=al;cx.fillText(t,x,y)}

/* scene 0: vessel tree + heart */
const tree=[];(function grow(x,y,ang,len,dep,t0){if(dep>5||len<14)return;const x2=x+Math.cos(ang)*len,y2=y+Math.sin(ang)*len,mx=(x+x2)/2+Math.sin(ang)*len*.12,my=(y+y2)/2-Math.cos(ang)*len*.12;tree.push({p:bez([x,y],[mx,my],[mx,my],[x2,y2],14),t0,w:Math.max(1.5,7-dep*1.2)});const sp=.42+rnd()*.2;grow(x2,y2,ang-sp,len*.74,dep+1,t0+.13);grow(x2,y2,ang+sp,len*.72,dep+1,t0+.13)})(-240,280,-Math.PI/2,140,0,0);
const heart=[];for(let i=0;i<=120;i++){const t=i/120*Math.PI*2,x=16*Math.pow(Math.sin(t),3),y=-(13*Math.cos(t)-5*Math.cos(2*t)-2*Math.cos(3*t)-Math.cos(4*t));heart.push([170+x*9.5,30+y*9.5])}
const aorta=bez([178,-40],[170,-140],[255,-160],[262,-95],24),pulm=bez([152,-48],[140,-118],[92,-126],[82,-84],24);
const heartCells=fillCells(heart,24,6.5);
function scene0(d){for(const b of tree){const f=(d*1.45-b.t0)/.25;stroke(b.p,f,`rgba(${CY},.95)`,b.w)}
stroke(heart,(d-.25)/.55,`rgba(${LV},1)`,3);stroke(aorta,(d-.55)/.3,`rgba(${LV},1)`,3);stroke(pulm,(d-.6)/.3,`rgba(${LV},1)`,3);cells(heartCells,(d-.5)/.5,MT);
label('printed vessels',-240,345,(d-.6)/.3);label('mini heart · rabbit size',170,240,(d-.8)/.2)}

/* scene 1: ear */
const earOut=chain(bez([-60,-20],[-90,-150],[-40,-270],[60,-270]),bez([60,-270],[170,-270],[225,-160],[205,-60]),bez([205,-60],[190,40],[135,90],[122,160]),bez([122,160],[110,230],[60,285],[10,272]),bez([10,272],[-40,262],[-55,200],[-40,150]),bez([-40,150],[-30,120],[-62,90],[-62,60]),bez([-62,60],[-28,50],[-28,0],[-60,-20],20));
const earIn=chain(bez([-25,-150],[10,-232],[150,-238],[168,-120]),bez([168,-120],[178,-40],[122,30],[96,92]));
const earCon=chain(bez([40,-175],[62,-120],[102,-60],[82,10]),bez([82,10],[72,60],[32,82],[8,92]),bez([8,92],[-10,96],[-20,80],[-22,60],10));
const earCells=fillCells(earOut,26,7);
function scene1(d){stroke(earOut,d/.55,`rgba(${PK},1)`,3.2);stroke(earIn,(d-.3)/.4,`rgba(${PK},.8)`,2.4);stroke(earCon,(d-.45)/.3,`rgba(${PK},.7)`,2.2);cells(earCells,(d-.45)/.55,MT);label('printed from her own cartilage cells · 2022',30,340,(d-.75)/.25)}

/* scene 2: orbit */
const earth=[];for(let i=0;i<=90;i++){const t=i/90*Math.PI*2;earth.push([-80+Math.cos(t)*120,60+Math.sin(t)*120])}
const lat=[-.45,0,.45].map(k=>{const r=Math.sqrt(1-k*k)*120,p=[];for(let i=0;i<=40;i++){const t=Math.PI*(i/40);p.push([-80+Math.cos(t)*r,60+k*120+Math.sin(t)*r*.22])}return p});
const orb=[];for(let i=0;i<=140;i++){const t=i/140*Math.PI*2,x=Math.cos(t)*330,y=Math.sin(t)*105,a=-.2;orb.push([-80+x*Math.cos(a)-y*Math.sin(a),60+x*Math.sin(a)+y*Math.cos(a)])}
const men=chain(bez([150,-250],[260,-300],[330,-200],[300,-120],24),bez([300,-120],[285,-160],[230,-215],[165,-205],24),bez([165,-205],[150,-215],[140,-240],[150,-250],8));
const menCells=fillCells(men,16,4.6);
function scene2(d,now){stroke(earth,d/.4,`rgba(${CY},.95)`,3);lat.forEach((p,i)=>stroke(p,(d-.2-i*.06)/.3,`rgba(${CY},.35)`,1.6));stroke(orb,(d-.25)/.45,`rgba(${LV},.8)`,2,[8,10]);
if(d>.6){const a=cl((d-.6)/.2),k=(now/9000)%1,q=orb[Math.floor(k*140)];cx.save();cx.globalAlpha*=a;cx.translate(q[0],q[1]);cx.strokeStyle=`rgb(${WH})`;cx.lineWidth=2;cx.strokeRect(-9,-6,18,12);cx.strokeStyle=`rgba(${CY},1)`;cx.beginPath();cx.moveTo(-30,-10);cx.lineTo(-12,-10);cx.moveTo(12,-10);cx.lineTo(30,-10);cx.moveTo(-30,10);cx.lineTo(-12,10);cx.moveTo(12,10);cx.lineTo(30,10);cx.moveTo(-21,-10);cx.lineTo(-21,10);cx.moveTo(21,-10);cx.lineTo(21,10);cx.stroke();cx.restore()}
stroke(men,(d-.5)/.3,`rgba(${PK},1)`,2.6);cells(menCells,(d-.6)/.4,MT);label('meniscus · printed on the ISS 2023',235,-290,(d-.75)/.25)}

/* scene 3: hospital, dashed */
const hosp=chain(bez([-260,230],[-260,100],[-260,0],[-260,-80],6),bez([-260,-80],[-130,-80],[-50,-80],[-50,-80],4),bez([-50,-80],[-50,-140],[-50,-200],[-50,-200],4),bez([-50,-200],[60,-200],[110,-200],[110,-200],4),bez([110,-200],[110,-140],[110,-80],[110,-80],4),bez([110,-80],[200,-80],[300,-80],[300,-80],4),bez([300,-80],[300,0],[300,100],[300,230],6),bez([300,230],[100,230],[-100,230],[-260,230],8));
const door=chain(bez([0,230],[0,170],[0,150],[0,150],3),bez([0,150],[40,150],[60,150],[60,150],3),bez([60,150],[60,190],[60,230],[60,230],3));
const wins=[];for(const x of [-210,-130,170,240])for(const y of [-20,70]){wins.push(chain(bez([x,y],[x+40,y],[x+40,y],[x+40,y],2),bez([x+40,y],[x+40,y+40],[x+40,y+40],[x+40,y+40],2),bez([x+40,y+40],[x,y+40],[x,y+40],[x,y+40],2),bez([x,y+40],[x,y],[x,y],[x,y],2)))}
const crossV=bez([30,-180],[30,-150],[30,-130],[30,-100],6),crossH=bez([0,-140],[20,-140],[40,-140],[60,-140],6);
function scene3(d){stroke(hosp,d/.6,`rgba(${GR},.9)`,2.6,[12,12]);stroke(door,(d-.4)/.2,`rgba(${GR},.8)`,2.2,[8,8]);wins.forEach((w,i)=>stroke(w,(d-.45-i*.03)/.15,`rgba(${GR},.6)`,2,[6,7]));stroke(crossV,(d-.6)/.2,`rgba(${PK},1)`,7);stroke(crossH,(d-.7)/.2,`rgba(${PK},1)`,7)}

const scenes=[scene0,scene1,scene2,scene3],names=['Lab','Patient','Space','Medical'];
const NX=[980,1210,1440,1670],NY=930,CXp=1350,CYp=470;
const PH=[...s.querySelectorAll('.wt-ph')];let step=0,act=[0],k=[0,0,0,0],tp=0;
let raf=0;const go=(n,snap)=>{const now=performance.now();if(snap){for(let i=0;i<4;i++)k[i]=i===n?1:0;tp=n;act=[];for(let i=0;i<n;i++)act[i]=now-1e5}step=n;act[n]=now;s.querySelectorAll('.wt-cap').forEach(c=>c.classList.toggle('on',+c.dataset.i===n));if(!raf&&s.classList.contains('active')){last=now;raf=requestAnimationFrame(frame)}};
let last=performance.now();
function frame(now){if(!s.classList.contains('active')){raf=0;return}const dt=Math.min(.05,(now-last)/1000);last=now;cx.setTransform(Q,0,0,Q,0,0);cx.clearRect(0,0,W,H);
for(let i=0;i<4;i++){const tgt=i===step?1:0;k[i]+=(tgt-k[i])*Math.min(1,dt*3.2)}
tp+=(step-tp)*Math.min(1,dt*2.6);
/* track */
cx.strokeStyle=`rgba(${GR},.35)`;cx.lineWidth=3;cx.beginPath();cx.moveTo(NX[0],NY);cx.lineTo(NX[3],NY);cx.stroke();
const xe=NX[0]+(NX[3]-NX[0])*tp/3,g=cx.createLinearGradient(NX[0],0,NX[3],0);g.addColorStop(0,`rgb(${CY})`);g.addColorStop(.66,`rgb(${LV})`);g.addColorStop(1,`rgb(${PK})`);
cx.strokeStyle=g;cx.lineWidth=4;cx.beginPath();cx.moveTo(NX[0],NY);cx.lineTo(xe,NY);cx.stroke();
for(let i=0;i<4;i++){const on=tp>=i-.05,cur=i===step;cx.lineWidth=2.5;if(i===3){cx.setLineDash([4,4])}cx.strokeStyle=on?(i===3?`rgb(${PK})`:`rgb(${CY})`):`rgba(${GR},.7)`;cx.fillStyle='#050506';cx.beginPath();cx.arc(NX[i],NY,cur?11:8,0,7);cx.fill();cx.stroke();cx.setLineDash([]);if(on&&i<3){cx.fillStyle=`rgb(${CY})`;cx.beginPath();cx.arc(NX[i],NY,4,0,7);cx.fill()}
cx.font=(cur?'400 ':'300 ')+'22px Jost';cx.textAlign='center';cx.fillStyle=cur?(i===3?`rgb(${PK})`:`rgb(${WH})`):`rgba(${GR},1)`;cx.fillText(names[i],NX[i],NY+44)}
/* scenes: active big in centre, visited ones shrink to their node */
for(let i=0;i<4;i++){if(i>step&&k[i]<.01)continue;const kk=ease(k[i]),visited=i<step;
const sc=visited||kk<1?.2+.8*kk:1,x=NX[i]+(CXp-NX[i])*kk,y=(NY-62)+(CYp-NY+62)*kk;
const d=act[i]!==undefined?cl((now-act[i])/2600):0;
const pf=(i===step&&i<3&&act[i]!==undefined)?ease(cl((now-act[i]-2900)/900)):0;
SC=sc;cx.save();cx.translate(x,y);cx.scale(sc,sc);cx.globalAlpha=(i<=step?(visited?.7+.3*kk:1):kk)*(1-pf);if(i===3&&!visited&&step!==3)cx.globalAlpha=kk;
scenes[i](i===step?d:1,now);cx.restore();
if(pf>0){SC=.2;cx.save();cx.translate(NX[i],NY-62);cx.scale(.2,.2);cx.globalAlpha=.85*pf;scenes[i](1,now);cx.restore()}
PH.forEach(f=>{if(+f.dataset.s===i){f.style.opacity=pf;f.classList.toggle('on',pf>.3)}})}
PH.forEach(f=>{if(+f.dataset.s!==step)f.style.opacity=0});
raf=requestAnimationFrame(frame)}
const count=()=>s.querySelectorAll('.ps-step.revealed').length;
const mo=new MutationObserver(()=>go(count()));s.querySelectorAll('.ps-step').forEach(m=>mo.observe(m,{attributes:true,attributeFilter:['class']}));
let active=false;new MutationObserver(()=>{const a=s.classList.contains('active');if(a&&!active)go(count(),true);active=a}).observe(s,{attributes:true,attributeFilter:['class']});
document.fonts.ready.then(()=>{active=s.classList.contains('active');go(count(),true)});})();