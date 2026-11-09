/* ---------- laws + misuse scenes (slide "What is still in the way", 10 Nov 2026) ---------- */
function rules(cv){
  if(!cv)return()=>{};
  const W=1920,H=1080,Q=2,cx=cv.getContext('2d');cv.width=W*Q;cv.height=H*Q;cx.scale(Q,Q);
  const rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const cl=x=>Math.max(0,Math.min(1,x)),ease=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2};
  const CY_='100,223,255',LV='180,154,216',PK='227,148,173',MT='112,194,188',WH='241,245,245',GR='132,145,157';
  let seed=9;const rnd=()=>(seed=seed*16807%2147483647)/2147483647;
  const at={},prevT={v:-1};
  const txt=(s,x,y,size,col,w,al)=>{cx.font=(w||400)+' '+size+'px Jost, sans-serif';cx.textAlign=al||'center';cx.fillStyle=col;cx.fillText(s,x,y)};
  /* the printed tissue: a soft gel blob with cells and a little vessel */
  const blobPts=[];for(let i=0;i<40;i++){const a=i/40*Math.PI*2,r=52+7*Math.sin(a*3+1)+5*Math.cos(a*5);blobPts.push([Math.cos(a)*r*1.12,Math.sin(a)*r*.86])}
  const blobCells=[];for(let i=0;i<22;i++){const a=rnd()*6.283,r=Math.sqrt(rnd())*40;blobCells.push([Math.cos(a)*r*1.1,Math.sin(a)*r*.8])}
  function tissue(x,y,s,alpha,shake){cx.save();cx.translate(x+(shake||0),y);cx.scale(s,s);cx.globalAlpha*=alpha;
    cx.beginPath();blobPts.forEach((p,i)=>i?cx.lineTo(p[0],p[1]):cx.moveTo(p[0],p[1]));cx.closePath();cx.fillStyle='rgba('+LV+',.14)';cx.fill();cx.strokeStyle='rgba('+LV+',.9)';cx.lineWidth=2.4;cx.stroke();
    cx.strokeStyle='rgba('+CY_+',.85)';cx.lineWidth=3;cx.beginPath();cx.moveTo(-46,10);cx.bezierCurveTo(-15,-12,10,20,44,-6);cx.stroke();
    blobCells.forEach(c=>{cx.strokeStyle='rgba('+MT+',.95)';cx.lineWidth=1.6;cx.beginPath();cx.arc(c[0],c[1],6,0,7);cx.stroke();cx.fillStyle='rgb('+MT+')';cx.beginPath();cx.arc(c[0],c[1],2,0,7);cx.fill()});cx.restore()}
  /* ---- laws: three drawers, nothing fits ---- */
  const DR=[{x:600,label:'Drug rules',slot:'pill'},{x:960,label:'Device rules',slot:'square'},{x:1320,label:'Transplant rules',slot:'bean'}],DY=905;
  function slot(kind,x,y,col){cx.strokeStyle=col;cx.lineWidth=2.6;cx.beginPath();
    if(kind==='pill'){cx.roundRect(x-46,y-17,92,34,17)}else if(kind==='square'){cx.rect(x-30,y-30,60,60)}else{cx.moveTo(x-34,y-8);cx.bezierCurveTo(x-40,y-40,x+10,y-44,x+30,y-22);cx.bezierCurveTo(x+46,y-6,x+38,y+30,x+8,y+30);cx.bezierCurveTo(x-8,y+30,x-4,y+10,x-16,y+12);cx.bezierCurveTo(x-30,y+14,x-30,y+4,x-34,y-8)}cx.stroke()}
  function laws(e,alpha){if(alpha<=0)return;cx.globalAlpha=alpha;
    DR.forEach((d,i)=>{const a=cl((e-i*.15)*2.5);cx.globalAlpha=alpha*a;
      cx.strokeStyle='rgba('+WH+',.55)';cx.lineWidth=2;cx.beginPath();cx.roundRect(d.x-120,DY-62,240,124,14);cx.stroke();
      const tryAt=1.2+i*1.25,hit=e>tryAt+.35&&e<tryAt+1.05;slot(d.slot,d.x,DY+4,hit?'rgb('+PK+')':'rgba('+WH+',.75)');
      txt(d.label,d.x,DY+100,26,'rgb('+GR+')',400);
      if(e>tryAt+.45){const k=cl((e-tryAt-.45)*4);cx.globalAlpha=alpha*k;cx.strokeStyle='rgb('+PK+')';cx.lineWidth=4;cx.beginPath();cx.moveTo(d.x+78,DY-48);cx.lineTo(d.x+100,DY-26);cx.moveTo(d.x+100,DY-48);cx.lineTo(d.x+78,DY-26);cx.stroke()}});
    cx.globalAlpha=alpha;
    /* the tissue visits each drawer, bumps, backs off */
    let x=230,y=DY,s=.9,sh=0;
    const path=[[0,230,DY]];DR.forEach((d,i)=>{const t=1.2+i*1.25;path.push([t,d.x,DY-150],[t+.4,d.x,DY-20],[t+.8,d.x,DY-150])});path.push([5.3,960,DY-150]);
    for(let i=0;i<path.length-1;i++){const [t0,x0,y0]=path[i],[t1,x1,y1]=path[i+1];if(e>=t0&&e<t1){const k=ease((e-t0)/(t1-t0));x=x0+(x1-x0)*k;y=y0+(y1-y0)*k;
        if(y1>y0&&k>.85){sh=Math.sin(e*70)*5}}else if(e>=path[path.length-1][0]){x=960;y=DY-150}}
    if(e<1.2){const k=ease(e/1.2);x=230+(DR[0].x-230)*k;y=DY-150*k}
    tissue(x,y,s,cl(e*3),sh);
    if(e>5.3){const k=cl((e-5.3)*2.5);cx.globalAlpha=alpha*k;txt('?',1050,DY-128+8*(1-k),72,'rgb('+PK+')',500)}
    cx.globalAlpha=1}
  /* ---- misuse: two roads from the printer ---- */
  const PX=360,PY=880,FX=720,HX=1430,HY=790,BX=1430,BY=975;
  const up=t=>{if(t<.35){const k=t/.35;return[PX+60+(FX-PX-60)*k,PY]}const k=(t-.35)/.65;return[FX+(HX-100-FX)*k,PY+(HY-PY)*Math.sin(Math.min(1,k*1.6)*Math.PI/2)]};
  const dn=t=>{if(t<.35){const k=t/.35;return[PX+60+(FX-PX-60)*k,PY]}const k=(t-.35)/.65;return[FX+(BX-100-FX)*k,PY+(BY-PY)*Math.sin(Math.min(1,k*1.6)*Math.PI/2)]};
  function road(f,u,col,w,dash){cx.save();cx.strokeStyle=col;cx.lineWidth=w;if(dash)cx.setLineDash(dash);cx.beginPath();for(let i=0;i<=60*u;i++){const p=f(i/60);i?cx.lineTo(p[0],p[1]):cx.moveTo(p[0],p[1])}cx.stroke();cx.restore()}
  function kidney(x,y,s,col,alpha){cx.save();cx.translate(x,y);cx.scale(s,s);cx.globalAlpha*=alpha;cx.beginPath();cx.moveTo(-20,-26);cx.bezierCurveTo(10,-40,34,-18,30,6);cx.bezierCurveTo(26,30,-4,36,-20,24);cx.bezierCurveTo(-8,12,-8,0,-20,-6);cx.bezierCurveTo(-30,-12,-30,-22,-20,-26);cx.closePath();cx.fillStyle='rgba('+col+',.25)';cx.fill();cx.strokeStyle='rgb('+col+')';cx.lineWidth=2.4;cx.stroke();
    [[4,-12],[14,4],[-2,14],[10,-24]].forEach(c=>{cx.fillStyle='rgb('+col+')';cx.beginPath();cx.arc(c[0],c[1],2.6,0,7);cx.fill()});cx.restore()}
  const CHECKS=['cells tested','sterile','tracked'];
  function misuse(e,alpha){if(alpha<=0)return;cx.globalAlpha=alpha;const a0=cl(e*2.5);cx.globalAlpha=alpha*a0;
    /* printer */
    cx.strokeStyle='rgba('+WH+',.7)';cx.lineWidth=2.4;cx.beginPath();cx.roundRect(PX-70,PY-80,140,130,12);cx.moveTo(PX-50,PY-50);cx.lineTo(PX+50,PY-50);cx.moveTo(PX,PY-50);cx.lineTo(PX,PY-22);cx.stroke();
    cx.fillStyle='rgb('+CY_+')';cx.beginPath();cx.moveTo(PX-7,PY-22);cx.lineTo(PX+7,PY-22);cx.lineTo(PX,PY-10);cx.fill();txt('Bioprinter',PX,PY+90,24,'rgb('+GR+')');
    /* roads */
    const ru=cl((e-.3)/1.0);road(up,ru,'rgba('+CY_+',.9)',4);road(dn,cl((e-2.6)/1.0),'rgba('+GR+',.75)',3,[10,10]);
    /* hospital */
    const ha=cl((e-.9)*2.5);cx.globalAlpha=alpha*ha;cx.strokeStyle='rgb('+CY_+')';cx.lineWidth=2.6;cx.beginPath();cx.rect(HX-80,HY-55,160,110);cx.stroke();
    cx.lineWidth=6;cx.beginPath();cx.moveTo(HX,HY-20);cx.lineTo(HX,HY+20);cx.moveTo(HX-20,HY);cx.lineTo(HX+20,HY);cx.stroke();txt('Hospital',HX+110,HY+10,28,'rgb('+CY_+')',500,'left');
    /* back-alley clinic */
    const ba=cl((e-3.0)*2.5);cx.globalAlpha=alpha*ba;cx.save();cx.setLineDash([8,8]);cx.strokeStyle='rgba('+GR+',.85)';cx.lineWidth=2.4;cx.beginPath();cx.rect(BX-80,BY-48,160,96);cx.stroke();cx.restore();
    txt('?',BX,BY+20,58,'rgb('+PK+')',500);txt('Black market',BX+110,BY+10,28,'rgb('+PK+')',500,'left');
    /* organ 1: checked road */
    cx.globalAlpha=alpha;if(e>1.1){const k=ease(cl((e-1.1)/1.5)),p=up(k);
      CHECKS.forEach((c,i)=>{const kk=.45+i*.17;if(k<kk-.02)return;const q=up(kk),ca=cl((k-kk+.02)*8);cx.globalAlpha=alpha*ca;
        cx.strokeStyle='rgb('+MT+')';cx.lineWidth=3.4;cx.beginPath();cx.moveTo(q[0]-9,q[1]-44);cx.lineTo(q[0]-2,q[1]-36);cx.lineTo(q[0]+12,q[1]-54);cx.stroke();txt(c,q[0],q[1]-66,20,'rgb('+MT+')')});
      cx.globalAlpha=alpha;kidney(p[0],p[1]-4,1,MT,cl((e-1.1)*4))}
    /* organ 2: no checks */
    if(e>3.2){const k=ease(cl((e-3.2)/1.5)),p=dn(k);
      [.45,.62,.79].forEach(kk=>{if(k<kk)return;const q=dn(kk);cx.globalAlpha=alpha*cl((k-kk)*8);txt('✗',q[0],q[1]-30,26,'rgba('+PK+',.8)')});
      cx.globalAlpha=alpha;kidney(p[0],p[1]-4,1,PK,cl((e-3.2)*4))}
    cx.globalAlpha=1}
  return (t,step)=>{
    if(t<prevT.v){for(const k in at)delete at[k]}prevT.v=t;
    [2,3,4].forEach(s=>{if(step>=s&&at[s]===undefined)at[s]=t;if(step<s)delete at[s]});
    cx.setTransform(Q,0,0,Q,0,0);cx.clearRect(0,0,W,H);
    const lawsOn=step===2,misOn=step===3;
    const lawsA=at[2]===undefined?0:(lawsOn?1:1-ease((t-(at[3]??t))/.5));
    const misA=at[3]===undefined?0:(misOn?1:1-ease((t-(at[4]??t))/.5));
    if(at[2]!==undefined&&(lawsOn||lawsA>0))laws(rm?99:t-at[2],lawsA);
    if(at[3]!==undefined&&(misOn||misA>0))misuse(rm?99:t-at[3],misA);
  };
}
