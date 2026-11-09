(()=>{const s=document.querySelector('.ring-slide');if(!s)return;const cv=s.querySelector('canvas.sm-canvas'),cx=cv.getContext('2d'),W=1920,H=1080,Q=1.5;cv.width=W*Q;cv.height=H*Q;
const CY='100,223,255',LV='180,154,216',PK='227,148,173',MT='112,194,188',WH='241,245,245',GR='132,145,157';
const COL=[PK,LV,CY,MT],LAB=[['WHY','Need'],['HOW','Build'],['TODAY','Progress'],['NEXT','Future']];
const ease=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2,cl=x=>Math.max(0,Math.min(1,x));
let seed=5;const rnd=()=>(seed=seed*16807%2147483647)/2147483647;
const RX=360,RY=560,RR=190,PX=1550,PY=520;
let step=0,act=[],k=[0,0,0,0],ring=0;
let raf=0;const go=(n,snap)=>{const now=performance.now();if(snap){for(let i=0;i<4;i++)k[i]=i===n?1:0;ring=n===0?0:n+1}step=n;act[n]=now;s.querySelectorAll('.sm-it').forEach((e,i)=>{e.classList.toggle('on',i===n);e.classList.toggle('past',i<n)});s.querySelectorAll('.sm-lg').forEach(e=>e.classList.toggle('on',+e.dataset.i===n));if(!raf&&s.classList.contains('active')){last=now;raf=requestAnimationFrame(frame)}};

/* 0: dots (callback to "Behind the numbers") */
const dots=[];{const tot=53;let i=0;for(;i<tot;i++)dots.push({c:LV,i});}
const tr=[];for(let i=0;i<18;i++)tr.push(i);const de=[0,1,2,3];
function vWhy(d){const cols=12,s=34,x0=PX-cols*s/2+s/2,y0=PY-140;
for(let i=0;i<53;i++){const a=cl((d*1.6-i/53*.7)/.2),x=x0+(i%cols)*s,y=y0+Math.floor(i/cols)*s;if(a<=0)continue;cx.fillStyle=`rgba(${LV},${.9*a})`;cx.beginPath();cx.arc(x,y,9*ease(a),0,7);cx.fill()}
for(let i=0;i<18;i++){const a=cl((d*1.6-.8-i/18*.4)/.2),x=x0+(i%cols)*s,y=y0+190+Math.floor(i/cols)*s;if(a<=0)continue;cx.fillStyle=`rgba(${CY},${a})`;cx.beginPath();cx.arc(x,y,9*ease(a),0,7);cx.fill()}
for(let i=0;i<4;i++){const a=cl((d*1.6-1.25-i*.06)/.2),x=x0+i*s,y=y0+300;if(a<=0)continue;cx.strokeStyle=`rgba(${PK},${a})`;cx.lineWidth=2.5;cx.beginPath();cx.arc(x,y,9,0,7);cx.stroke()}}

/* 1: light vat (callback to "Bioink & curing") */
function vHow(d,now){const t=(now-(act[1]||0))/1000,x0=PX-220,x1=PX+220,yb=PY+170,yt=PY-170,a=cl(d/.3);cx.globalAlpha*=a;
cx.strokeStyle=`rgba(${WH},.7)`;cx.lineWidth=2.5;cx.beginPath();cx.moveTo(x0,yt);cx.lineTo(x0,yb);cx.lineTo(x1,yb);cx.lineTo(x1,yt);cx.stroke();
cx.fillStyle=`rgba(${LV},.12)`;cx.fillRect(x0+2,PY-90,x1-x0-4,yb-PY+88);
const cyc=1.8,ph=(t%cyc)/cyc,n=Math.min(9,Math.floor(t/cyc)%10);const layers=n+ (ph>.6?1:0);
const lift=layers*14;cx.fillStyle=`rgba(${WH},.85)`;
const py=yb-30-lift;cx.fillRect(PX-140,py-10,280,8);cx.fillRect(PX-4,yt-60,8,py-yt+50);
for(let i=0;i<layers;i++){cx.fillStyle=`rgba(${MT},${.55+.04*i})`;cx.fillRect(PX-110+((i*37)%20)-10,py-2+i*14,220-((i*23)%30),12)}
if(ph>.2&&ph<.6){const s=Math.sin((ph-.2)/.4*Math.PI);const g=cx.createLinearGradient(0,yb+80,0,py+layers*14);g.addColorStop(0,`rgba(${CY},0)`);g.addColorStop(1,`rgba(${CY},${.55*s})`);cx.fillStyle=g;cx.beginPath();cx.moveTo(PX-60,yb+80);cx.lineTo(PX+60,yb+80);cx.lineTo(PX+110,py+layers*14+12);cx.lineTo(PX-110,py+layers*14+12);cx.fill()}
cx.strokeStyle=`rgba(${CY},.9)`;cx.lineWidth=2;cx.strokeRect(PX-40,yb+80,80,22);
cx.font='300 22px Jost';cx.textAlign='center';const w=['light','cure','repeat'],wi=ph<.2?2:ph<.6?0:1;cx.fillStyle=`rgba(${WH},.9)`;cx.fillText(w[wi],PX,yb+150)}

/* 2: vessels + cells (callback to oxygen slide) */
const cells=[];for(let y=PY-230;y<PY+230;y+=30)for(let x=PX-260;x<PX+260;x+=30)cells.push([x+(rnd()-.5)*12,y+(rnd()-.5)*12]);
const line=(f,n)=>{const p=[];for(let i=0;i<=n;i++)p.push(f(i/n));return p};
const mainV=line(u=>[PX-280+u*560,PY+30*Math.sin(u*5)+10*Math.sin(u*13)],80);
const brs=[];for(let i=0;i<6;i++){const [x0,y0]=mainV[Math.round((i+.5)/6*80)],kk=i%2?1:-1;brs.push(line(v=>[x0+kk*v*30+18*Math.sin(v*6),y0-v*240],30));brs.push(line(v=>[x0-kk*v*28+16*Math.sin(v*5+1),y0+v*240],30))}
const dist=(p,poly)=>{let m=1e9;for(const q of poly){const d=Math.hypot(p[0]-q[0],p[1]-q[1]);if(d<m)m=d}return m};
cells.forEach(c=>c.d=Math.min(dist(c,mainV),...brs.map(b=>dist(c,b))));
function poly(p,f,w,col){if(f<=0)return;const n=Math.max(2,Math.ceil(p.length*Math.min(1,f)));cx.strokeStyle=col;cx.lineWidth=w;cx.lineCap='round';cx.beginPath();cx.moveTo(p[0][0],p[0][1]);for(let i=1;i<n;i++)cx.lineTo(p[i][0],p[i][1]);cx.stroke()}
function vToday(d){const vf=cl((d-.15)/.6);for(const c of cells){const a=cl(d/.2),lit=cl((vf*300-c.d*1.2)/40);const fx=Math.abs(c[0]-PX)/280,fy=Math.abs(c[1]-PY)/240,edge=cl(1.25-Math.max(fx,fy));cx.fillStyle=lit>0?`rgba(${MT},${a*edge*(.5+.5*lit)})`:`rgba(${LV},${a*edge*.55})`;cx.beginPath();cx.arc(c[0],c[1],5.5,0,7);cx.fill()}
poly(mainV,vf*1.3,6,`rgba(${CY},.95)`);brs.forEach((b,i)=>poly(b,(vf-.25-i*.02)/.5,3,`rgba(${CY},.85)`))}

/* 3: timeline */
function vNext(d){const x0=PX-280,x1=PX+280,y=PY,sx=yr=>x0+(yr-2026)/32*(x1-x0);const f=cl(d/.45);
cx.strokeStyle=`rgba(${GR},.6)`;cx.lineWidth=3;cx.beginPath();cx.moveTo(x0,y);cx.lineTo(x0+(x1-x0)*f,y);cx.stroke();
const mk=(yr,col,t,sub,dy,ft)=>{const a=cl((d-ft)/.2);if(a<=0)return;cx.fillStyle=`rgba(${col},${a})`;cx.beginPath();cx.arc(sx(yr),y,10*ease(a),0,7);cx.fill();cx.font='500 26px Jost';cx.textAlign='center';cx.fillText(t,sx(yr),y+dy);cx.font='300 20px Jost';cx.fillStyle=`rgba(${GR},${a})`;cx.fillText(sub,sx(yr),y+dy+28)};
mk(2026,CY,'today','2026',60,.1);mk(2036,LV,'simple tissues','~10 years',-58,.4);
const a=cl((d-.65)/.25);if(a>0){cx.fillStyle=`rgba(${PK},${.35*a})`;cx.beginPath();cx.roundRect(sx(2046),y-9,(sx(2056)-sx(2046))*ease(a),18,9);cx.fill();cx.font='500 26px Jost';cx.textAlign='center';cx.fillStyle=`rgba(${PK},${a})`;cx.fillText('whole organs',sx(2051),y-58);cx.font='300 20px Jost';cx.fillStyle=`rgba(${GR},${a})`;cx.fillText('20–30 years',sx(2051),y-30)}
const b=cl((d-.9)/.2);if(b>0){cx.strokeStyle=`rgba(${MT},${b})`;cx.lineWidth=2;cx.setLineDash([6,6]);cx.beginPath();cx.moveTo(sx(2046)-6,y+40);cx.lineTo(sx(2040),y+40);cx.stroke();cx.setLineDash([]);cx.beginPath();cx.moveTo(sx(2040)+10,y+32);cx.lineTo(sx(2040),y+40);cx.lineTo(sx(2040)+10,y+48);cx.stroke();cx.font='300 20px Jost';cx.textAlign='left';cx.fillStyle=`rgba(${MT},${b})`;cx.fillText('AI could pull this closer',sx(2037),y+76)}}

const vis=[vWhy,vHow,vToday,vNext];let last=performance.now();
function frame(now){if(!s.classList.contains('active')){raf=0;return}const dt=Math.min(.05,(now-last)/1000);last=now;cx.setTransform(Q,0,0,Q,0,0);cx.clearRect(0,0,W,H);
for(let i=0;i<4;i++)k[i]+=((i===step?1:0)-k[i])*Math.min(1,dt*4);
ring+=(step+1-ring)*Math.min(1,dt*2.4);
/* ring */
cx.lineWidth=7;cx.strokeStyle='rgba(255,255,255,.08)';cx.beginPath();cx.arc(RX,RY,RR,0,7);cx.stroke();
for(let i=0;i<4;i++){const f=cl(ring-i);if(f<=0)continue;const a0=-Math.PI/2+i*Math.PI/2+.04,a1=a0+(Math.PI/2-.08)*f;cx.strokeStyle=`rgba(${COL[i]},${i===step?1:.75})`;cx.lineCap='round';cx.beginPath();cx.arc(RX,RY,RR,a0,a1);cx.stroke()}
const ae=-Math.PI/2+ring*Math.PI/2;cx.fillStyle=`rgb(${WH})`;cx.beginPath();cx.arc(RX+Math.cos(ae)*RR,RY+Math.sin(ae)*RR,8,0,7);cx.fill();
cx.textAlign='center';cx.font='400 20px Jost';cx.fillStyle=`rgb(${COL[step]})`;cx.save();cx.letterSpacing='5px';cx.fillText(LAB[step][0],RX+2,RY-14);cx.restore();cx.font='400 36px Jost';cx.fillStyle=`rgb(${WH})`;cx.fillText(LAB[step][1],RX,RY+28);
/* right-hand callback visual */
for(let i=0;i<4;i++){if(k[i]<.01)continue;const d=act[i]!==undefined?cl((now-act[i])/2800):0;cx.save();cx.globalAlpha=ease(k[i]);vis[i](d,now);cx.restore()}
raf=requestAnimationFrame(frame)}
const count=()=>s.querySelectorAll('.rs-step.revealed').length;
const mo=new MutationObserver(()=>go(count()));s.querySelectorAll('.rs-step').forEach(m=>mo.observe(m,{attributes:true,attributeFilter:['class']}));
let active=false;new MutationObserver(()=>{const a=s.classList.contains('active');if(a&&!active)go(count(),true);active=a}).observe(s,{attributes:true,attributeFilter:['class']});
document.fonts.ready.then(()=>{active=s.classList.contains('active');go(count(),true)});})();