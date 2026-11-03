/* === PUBLICATION COUNTS: DATA, ANIMATION AND ACCESSIBLE YEAR SELECTION === */
const publicationPalette=[['#72bbd6', '#4e88ad'], ['#83c9a5', '#548e78'], ['#af98d6', '#8069a5'], ['#e995bc', '#b46b96']];
class PublicationTimeline{
 constructor(){this.root=document.getElementById('publicationChart');if(!this.root)return;this.data=JSON.parse(document.getElementById('publicationData').textContent);this.rows=this.data.rows;this.techniques=this.data.techniques.map((technique,index)=>({...technique,color:publicationPalette[index][0]}));this.first=this.rows[0].year;this.last=this.data.last_verified_year;this.end=this.data.display_end_year;this.year=this.first;this.active=false;this.running=false;this.frame=null;this.durationMs=6000;this.reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;this.svg=document.getElementById('publicationPlot');this.slider=document.getElementById('publicationSlider');this.slider.min=this.first;this.slider.max=this.end;this.build();this.bind();this.draw(this.reduced?this.last:this.first);}
 build(){const left=80,top=30,width=1280,height=500;this.geometry={left,top,width,height};const totals=this.rows.filter(r=>Object.values(r.counts).every(Number.isFinite)).map(r=>Object.values(r.counts).reduce((a,b)=>a+b,0));this.yMax=Math.max(100,Math.ceil(Math.max(...totals)/100)*100);this.step=width/this.rows.length;let html='<defs>'+publicationPalette.map(([light,dark],index)=>
  `<linearGradient id="pub-fill-${index}" x2="0%" y2="100%"><stop stop-color="${light}"/><stop offset="1" stop-color="${dark}"/></linearGradient>`).join('')+'</defs>';
 const partialX=left+(this.rows.length-1)*width/this.rows.length;html+=`<rect x="${partialX}" y="${top}" width="${width/this.rows.length}" height="${height}" fill="#b49ad80d" stroke="#b49ad866" stroke-dasharray="6 6"/>`;
 for(let v=0;v<=this.yMax;v+=100){const y=top+height-v/this.yMax*height;html+=`<line class="pub-grid" x1="${left}" x2="${left+width}" y1="${y}" y2="${y}"/><text class="pub-axis" x="${left-20}" y="${y+7}" text-anchor="end">${v}</text>`;}

 const missingStart=this.rows.findIndex(r=>Object.values(r.counts).some(v=>v===null));if(missingStart>=0){const x=left+missingStart*this.step;html+=`<rect x="${x}" y="${top}" width="${left+width-x}" height="${height}" fill="#ffffff05" stroke="#9ba7b244" stroke-dasharray="7 7"/><text class="pub-nodata" x="${x+(left+width-x)/2}" y="${top+100}" text-anchor="middle"><tspan x="${x+(left+width-x)/2}">Not</tspan><tspan x="${x+(left+width-x)/2}" dy="27">verified</tspan></text>`;}
 this.rows.forEach((r,i)=>{const x=left+i*this.step+this.step*.17,w=this.step*.66;this.techniques.forEach((t,index)=>{html+=`<rect class="pub-bar" data-year="${r.year}" data-technique="${t.key}" x="${x}" y="${top+height}" width="${w}" height="0" fill="url(#pub-fill-${index})"/><path data-side="${r.year}-${index}" fill="${t.color}" opacity=".51" pointer-events="none"/>`});html+=`<path data-cap="${r.year}" pointer-events="none"/><rect class="pub-hit" data-select-year="${r.year}" x="${left+i*this.step}" y="${top}" width="${this.step}" height="${height}"><title>${r.year}: ${Object.values(r.counts).some(v=>v===null)?'Not verified':this.techniques.map(t=>`${t.key} ${r.counts[t.key]}`).join(', ')}</title></rect><text class="pub-axis pub-xlabel" data-year-label="${r.year}" x="${left+(i+.5)*this.step}" y="${top+height+36}" text-anchor="middle" transform="rotate(-48 ${left+(i+.5)*this.step} ${top+height+36})">${r.year}${r.status==='year_to_date'?'*':''}</text>`;});
 html+='<line id="publicationCursor" stroke="#b49ad8" stroke-dasharray="4 7" opacity=".55"/>';this.svg.innerHTML=html;
 document.getElementById('publicationLegend').innerHTML=this.techniques.map(t=>`<span><i style="background:${t.color}"></i>${t.key}</span>`).join('');
 document.getElementById('publicationCounts').innerHTML=this.techniques.map(t=>`<div class="pub-count-row"><span style="color:${t.color}">${t.key}</span><strong data-value="${t.key}">0</strong></div>`).join('');
 }
 draw(year){this.render(Math.max(this.first,Math.min(this.end,year)));}
 render(position){
 const selected=Math.max(this.first,Math.min(this.end,Math.floor(position))),row=this.rows.find(r=>r.year===selected);
 this.year=selected;this.position=position;
 const {left,top,height}=this.geometry;
 this.rows.forEach(r=>{
  const t=Math.max(0,Math.min(1,position-r.year+1)),growth=t*t*(3-2*t);let stack=0,capColor=null;
  this.techniques.forEach((tech,index)=>{const value=r.counts[tech.key]||0,h=value/this.yMax*height*growth;
   const rect=this.svg.querySelector(`[data-year="${r.year}"][data-technique="${tech.key}"]`);
   rect.setAttribute('y',top+height-stack-h);rect.setAttribute('height',h);
   const right=Number(rect.getAttribute('x'))+Number(rect.getAttribute('width'));
   const y=top+height-stack-h;
   const depth=10*growth, rise=6*growth;
   this.svg.querySelector(`[data-side="${r.year}-${index}"]`)
     .setAttribute('d',h ? `M${right} ${y}l${depth} -${rise}v${h}l-${depth} ${rise}Z` : '');
   if(h)capColor=tech.color;
   stack+=h;
  });
  const cap=this.svg.querySelector(`[data-cap="${r.year}"]`);
  const x=left+(r.year-this.first+.17)*this.step;
  const width=this.step*.66,depth=10*growth,rise=6*growth;
  cap.setAttribute('d',stack ? `M${x} ${top+height-stack}h${width}l${depth} -${rise}h-${width}Z` : '');
  if(capColor)cap.setAttribute('fill',capColor);
  this.svg.querySelector(`[data-year-label="${r.year}"]`).setAttribute('class',`pub-axis pub-xlabel${r.year===selected?' pub-current-year':''}`);
 });
 const x=left+(Math.max(0,Math.min(this.rows.length-1,position-this.first))+.5)*this.step,cursor=document.getElementById('publicationCursor');
 cursor.setAttribute('x1',x);cursor.setAttribute('x2',x);cursor.setAttribute('y1',top);cursor.setAttribute('y2',top+height);
 document.getElementById('publicationYear').textContent=selected;document.getElementById('publicationSliderYear').textContent=selected;this.slider.value=selected;
 document.getElementById('publicationStatus').textContent=row.status==='year_to_date'?'Scopus · 2026 partial':'Scopus · annual snapshot';
 this.root.querySelectorAll('[data-value]').forEach(el=>el.textContent=row.counts[el.dataset.value].toLocaleString());
 document.getElementById('publicationTotal').textContent=Object.values(row.counts).reduce((a,b)=>a+b,0).toLocaleString();
 }
 play(){this.targetYear=null;this.pause();this.running=true;const start=performance.now();this.render(this.first-1);
 const tick=now=>{if(!this.running||!this.active)return;
 const progress=Math.min(1,(now-start)/this.durationMs);
 this.render(this.first-1+progress*(this.last-this.first+1));
 if(progress===1){this.pause();return;}this.frame=requestAnimationFrame(tick);
 };this.frame=requestAnimationFrame(tick);}
 stepYear(direction){
 const target=Math.max(this.first,Math.min(this.last,(this.targetYear??this.year)+direction));
 this.pause();this.targetYear=target;const from=this.position,start=performance.now();
 if(this.reduced){this.draw(target);this.targetYear=null;return;}
 this.running=true;
 const tick=now=>{if(!this.running||!this.active)return;const t=Math.min(1,(now-start)/300),ease=t*t*(3-2*t);this.render(from+(target-from)*ease);if(t===1){this.draw(target);this.targetYear=null;this.pause();return;}this.frame=requestAnimationFrame(tick);};this.frame=requestAnimationFrame(tick);
 }
 pause(){this.running=false;if(this.frame!==null)cancelAnimationFrame(this.frame);this.frame=null;}
 activate(active){if(active===this.active)return;this.active=active;if(!active){this.pause();return}if(this.reduced)this.draw(this.last);else this.play(true)}
 bind(){this.slider.addEventListener('input',()=>{this.pause();this.draw(Number(this.slider.value))});this.svg.querySelectorAll('[data-select-year]').forEach(el=>el.addEventListener('click',()=>{this.pause();this.draw(Number(el.dataset.selectYear))}));this.root.addEventListener('wheel',e=>e.stopPropagation(),{passive:true});this.root.addEventListener('touchstart',e=>e.stopPropagation(),{passive:true});this.root.addEventListener('keydown',e=>{if(e.target===this.slider)e.stopPropagation()});addEventListener('beforeprint',()=>{this.pause();this.draw(this.last)});document.addEventListener('visibilitychange',()=>{if(document.hidden)this.pause()});}
}
window.publicationTimeline=new PublicationTimeline();window.publicationTimeline.activate(document.querySelector('.slide.active').contains(document.getElementById('publicationChart')));
