/* === SOURCE DATA AND LOCAL TEXT EDITING === */
const slidesData=JSON.parse(document.getElementById('sourceData').textContent);
const storageKey='sofe-c-2026-51slides-v1';
class SlidePresentation{
 constructor(){this.slides=[...document.querySelectorAll('.slide')];this.stage=document.getElementById('deckStage');this.current=0;this.editing=false;this.setup();this.restore();this.scale();this.show(this.hash());document.fonts.ready.then(()=>{
  this.fitText();
  // Let the deck paint its fitted layout before starting the SVG clock.
  requestAnimationFrame(()=>requestAnimationFrame(()=>{
   this.introReady=true;
   this.startIntroCharacter();
  }));
 });}
 hash(){return Math.max(0,(parseInt(location.hash.replace('#',''),10)||1)-1)}
 /* === STAGE FITTING: NEVER REFLOW SLIDES === */
 scale(){const s=Math.min(innerWidth/1920,innerHeight/1080);this.stage.style.transform=`translate(${(innerWidth-1920*s)/2}px,${(innerHeight-1080*s)/2}px) scale(${s})`;this.scaleFactor=s}
 fitText(){document.querySelectorAll('.textline').forEach(e=>{e.style.transform='none';const desired=Number(e.dataset.width),actual=e.scrollWidth;if(actual>desired&&desired>0)e.style.transform=`scaleX(${desired/actual})`;});}
 /* === NAVIGATION AND MEDIA LIFECYCLE === */
 show(index){const next=Math.max(0,Math.min(index,this.slides.length-1));const entering=next!==this.current||!this.started;if(next!==this.current){
  this.stopCover();
  this.slides[this.current].querySelectorAll('video').forEach(v=>v.pause());
 }this.current=next;if(entering){this.resetProfile(this.slides[next]);this.tramStory(this.slides[next])?.reset();this.started=true;}this.slides.forEach((s,i)=>{s.classList.toggle('active',i===next);s.classList.toggle('visible',i===next);s.setAttribute('aria-hidden',String(i!==next));s.inert=i!==next;});this.loadMap(this.slides[next]);this.startIntroCharacter();history.replaceState(null,'',`#${next+1}`);document.getElementById('counter').textContent=`${next+1} / ${this.slides.length}`;document.getElementById('progress').style.width=`${(next+1)/this.slides.length*100}%`;document.title=`${next+1} · ${slidesData[next].title} — Bioprinting`;document.querySelectorAll('.thumb').forEach((b,i)=>b.classList.toggle('selected',i===next));this.updateNotes();const chart=this.chartActive();const turntable=this.coverTurntable();
 document.getElementById('chartReplay').hidden=!(chart||turntable);
 if(entering&&turntable&&!matchMedia('(prefers-reduced-motion: reduce)').matches)this.playCover();window.publicationTimeline?.activate(this.slides[next].contains(document.getElementById('publicationChart')));window.organTimeline?.activate(this.slides[next].contains(document.getElementById('organChart')));}
 startIntroCharacter(){
  if(!this.introReady)return;
  const character=this.slides[this.current].querySelector('img[data-intro-src]:not([src])');
  if(!character)return;
  character.addEventListener('load',()=>{character.dataset.introLoaded='';},{once:true});
  character.src=character.dataset.introSrc;
 }
 loadMap(slide){
  const frame=slide.querySelector('iframe[data-srcdoc]');
  if(frame&&!frame.hasAttribute('srcdoc'))frame.srcdoc=frame.dataset.srcdoc;
 }
 chartActive(){const slide=this.slides[this.current];return slide.contains(document.getElementById('organChart'))?'organ':slide.contains(document.getElementById('publicationChart'))?'publication':null;}
 activeTimeline(){return this.chartActive()==='organ'?window.organTimeline:window.publicationTimeline;}
 coverTurntable(){return this.slides[this.current].querySelector('.cover-turntable');}
 async playCover(){
  const image=this.coverTurntable();
  if(!image)return;
  this.stopCover();
  this.coverPoster ??= image.getAttribute('src');
  const request={};
  this.coverRequest=request;
  try{
   this.coverAnimation ??= fetch(image.dataset.turntableSrc).then(response=>{
    if(!response.ok)throw new Error('Cover animation unavailable');
    return response.blob();
   });
   const animation=await this.coverAnimation;
   if(this.coverRequest!==request)return;
   this.coverUrl=URL.createObjectURL(animation);
   image.src=this.coverUrl;
  }catch{
   this.coverAnimation=null;
  }
 }
 stopCover(){
  this.coverRequest=null;
  if(!this.coverUrl)return;
  this.coverTurntable().src=this.coverPoster;
  URL.revokeObjectURL(this.coverUrl);
  this.coverUrl=null;
 }
 replayChart(){if(this.coverTurntable()){this.playCover();return;}const chart=this.activeTimeline();if(this.chartActive())chart?.[this.chartActive()==='organ'?'replay':'play']();}
 tramStory(slide){return slide.querySelector('.tram-story-frame')?.contentWindow?.tramStory;}
 navigate(direction){if(this.tramStory(this.slides[this.current])?.step(direction))return;this.show(this.current+direction);}
 advance(direction){if(this.editing)return;if(this.profileStep(direction))return;this.navigate(direction);}
 resetProfile(slide){slide.querySelectorAll('[data-reveal-step]').forEach(e=>{e.classList.remove('revealed');e.setAttribute('aria-hidden',String(!this.editing));e.inert=!this.editing;});}
 profileStep(direction){const slide=this.slides[this.current];if(!slide.classList.contains('profile-slide'))return false;const items=[...slide.querySelectorAll('[data-reveal-step]')],count=items.filter(e=>e.classList.contains('revealed')).length;if(direction>0&&count<items.length){const e=items[count];e.classList.add('revealed');e.setAttribute('aria-hidden','false');e.inert=false;return true;}if(direction<0&&count>0){const e=items[count-1];e.classList.remove('revealed');e.setAttribute('aria-hidden','true');e.inert=true;return true;}return false;}
 updateNotes(){const d=slidesData[this.current];document.getElementById('notesTitle').textContent=`${d.number}. ${d.title}`;document.getElementById('notes').textContent=d.notes||'No speaker notes in the original slide.';document.getElementById('transcript').textContent=d.text;}
 open(id){document.getElementById(id).showModal()}
 message(text){const el=document.getElementById('status');el.textContent=text;clearTimeout(this.messageTimer);this.messageTimer=setTimeout(()=>el.textContent='',4000)}
 async fullscreen(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen()}catch{this.message('Fullscreen is unavailable in this browser.')}}
 /* === TEXT EDITOR, LOCAL AUTOSAVE AND PORTABLE EXPORT === */
 toggleEdit(){this.editing=!this.editing;document.body.classList.toggle('editing',this.editing);document.getElementById('editToggle').classList.toggle('active',this.editing);document.querySelectorAll('.editable').forEach(e=>e.contentEditable=String(this.editing));document.querySelectorAll('[data-reveal-step]').forEach(e=>{const hidden=!this.editing&&!e.classList.contains('revealed');e.setAttribute('aria-hidden',String(hidden));e.inert=hidden;});this.message(this.editing?'Click text to edit · Ctrl/Cmd + S downloads your HTML':'Editing off');}
 restore(){try{const saved=JSON.parse(localStorage.getItem(storageKey)||'{}');document.querySelectorAll('[data-edit]').forEach(e=>{if(Object.hasOwn(saved,e.dataset.edit))e.innerHTML=saved[e.dataset.edit]});}catch{}}
 autosave(){try{localStorage.setItem(storageKey,JSON.stringify(Object.fromEntries([...document.querySelectorAll('[data-edit]')].map(e=>[e.dataset.edit,e.innerHTML]))));}catch{this.message('Browser storage is full. Use Ctrl/Cmd + S to save a copy.')}this.fitText();}
 async save(){const clone=document.documentElement.cloneNode(true);clone.querySelectorAll('img[data-intro-src]').forEach(img=>{img.removeAttribute('src');img.removeAttribute('data-intro-loaded');});clone.querySelectorAll('iframe[data-srcdoc]').forEach(frame=>frame.removeAttribute('srcdoc'));const cover=clone.querySelector('.cover-turntable');
 if(this.coverPoster)cover?.setAttribute('src',this.coverPoster);
 if(cover&&!cover.dataset.turntableSrc.startsWith('data:')){
  try{
   this.message('Preparing the offline presentation…');
   const response=await fetch(cover.dataset.turntableSrc);
   if(!response.ok)throw new Error('Cover animation unavailable');
   const animation=await response.blob();
   cover.dataset.turntableSrc=await new Promise((resolve,reject)=>{
    const reader=new FileReader();
    reader.onload=()=>resolve(reader.result);
    reader.onerror=reject;
    reader.readAsDataURL(animation);
   });
  }catch{
   this.message('Could not download the cover animation. Please try again.');
   return;
  }
 }
 clone.querySelector('body').classList.remove('editing');clone.querySelectorAll('[contenteditable]').forEach(e=>e.removeAttribute('contenteditable'));clone.querySelector('#editToggle').classList.remove('active');clone.querySelector('#status').textContent='';clone.querySelectorAll('dialog').forEach(d=>d.removeAttribute('open'));clone.querySelectorAll('[data-reveal-step]').forEach(e=>{e.classList.remove('revealed');e.setAttribute('aria-hidden','true');e.setAttribute('inert','');});const blob=new Blob(['<!doctype html>\n'+clone.outerHTML],{type:'text/html;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='3D-Bioprinting.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1500);this.message('Downloaded the updated presentation');}
 /* === KEYBOARD, TOUCH, WHEEL AND ACCESSIBLE PANELS === */
 setup(){addEventListener('resize',()=>this.scale());addEventListener('hashchange',()=>this.show(this.hash()));document.getElementById('prev').onclick=()=>this.navigate(-1);document.getElementById('next').onclick=()=>this.navigate(1);document.getElementById('chartReplay').onclick=()=>this.replayChart();document.getElementById('overviewButton').onclick=()=>this.open('overview');document.getElementById('notesButton').onclick=()=>this.open('notesDialog');document.getElementById('helpButton').onclick=()=>this.open('helpDialog');document.getElementById('fullButton').onclick=()=>this.fullscreen();document.getElementById('editToggle').onclick=()=>this.toggleEdit();document.getElementById('saveButton').onclick=()=>this.save();document.getElementById('resetButton').onclick=()=>{try{localStorage.removeItem(storageKey)}catch{}location.reload()};
 document.querySelectorAll('[data-goto]').forEach(b=>b.onclick=()=>{if(!this.editing)this.show(Number(b.dataset.goto)-1)});document.querySelectorAll('dialog .close').forEach(b=>b.onclick=()=>b.closest('dialog').close());
 document.getElementById('grid').replaceChildren();slidesData.forEach((d,i)=>{const b=document.createElement('button');b.className='thumb';const label=document.createElement('small');label.textContent=`${String(i+1).padStart(2,'0')} / ${i<23?'TALK':i<28?'REFERENCES':'BACKUP'}`;const title=document.createElement('span');title.textContent=d.title;b.append(label,title);b.onclick=()=>{this.show(i);document.getElementById('overview').close()};document.getElementById('grid').append(b)});
 document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='s'){e.preventDefault();this.save();return}if(e.target.isContentEditable||(/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)&&e.target.id!=='organYearSlider')||e.ctrlKey||e.metaKey||e.altKey||document.querySelector('dialog[open]'))return;if(e.target.closest('button,a,video')&&[' ','Enter'].includes(e.key))return;const k=e.key.toLowerCase();
 if(this.slides[this.current].classList.contains('tram-story-slide')&&['arrowup','arrowdown','arrowleft','arrowright'].includes(k)){
  e.preventDefault();
  if(k==='arrowup'||k==='arrowdown')this.tramStory(this.slides[this.current])?.step(k==='arrowup'?-1:1);
  else this.show(this.current+(k==='arrowleft'?-1:1));
  return;
 }
 if(k==='arrowleft'||k==='arrowright'){e.preventDefault();const direction=k==='arrowleft'?-1:1;if(this.slides[this.current].classList.contains('profile-slide'))this.advance(direction);else this.navigate(direction);return;}if(this.chartActive()&&['arrowup','arrowdown','r'].includes(k)){e.preventDefault();if(k==='r')this.replayChart();else this.activeTimeline()?.stepYear(k==='arrowup'?1:-1);return;}if(['arrowright','arrowdown',' ','pagedown'].includes(k)){e.preventDefault();this.advance(1)}else if(['arrowleft','arrowup','pageup'].includes(k)){e.preventDefault();this.advance(-1)}else if(k==='home'){e.preventDefault();this.show(0);this.resetProfile(this.slides[0]);}else if(k==='end'){e.preventDefault();this.show(this.slides.length-1)}else if(k==='o')this.open('overview');else if(k==='n')this.open('notesDialog');else if(k==='f')this.fullscreen();else if(k==='e')this.toggleEdit();else if(k==='?')this.open('helpDialog');});
 let start=null;const view=document.querySelector('.deck-viewport');view.addEventListener('click',e=>{if(e.button!==0||this.editing||document.querySelector('dialog[open]')||e.target.closest('button,a,video,input,textarea,select,[contenteditable="true"]'))return;if(this.slides[this.current].matches('.profile-slide,.tram-story-slide'))this.advance(1);});view.addEventListener('touchstart',e=>{if(!this.editing&&!e.target.closest('video,button,a'))start={x:e.touches[0].clientX,y:e.touches[0].clientY}},{passive:true});view.addEventListener('touchend',e=>{if(!start||document.querySelector('dialog[open]'))return;const dx=e.changedTouches[0].clientX-start.x,dy=e.changedTouches[0].clientY-start.y;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy))this.advance(dx<0?1:-1);start=null},{passive:true});let lastWheel=0;addEventListener('wheel',e=>{if(this.editing||document.querySelector('dialog[open]')||e.target.closest('video'))return;e.preventDefault();if(Date.now()-lastWheel>700&&Math.abs(e.deltaY)>20){lastWheel=Date.now();this.advance(e.deltaY>0?1:-1)}},{passive:false});
 document.querySelectorAll('.editable').forEach(e=>{e.addEventListener('input',()=>this.autosave());e.addEventListener('paste',event=>{if(!this.editing)return;event.preventDefault();document.execCommand('insertText',false,event.clipboardData.getData('text/plain'));});});
 /* === HOVER HOTZONE: 400 MS GRACE PERIOD KEEPS THE BUTTON CLICKABLE === */
 const hot=document.querySelector('.edit-hotzone'),toggle=document.getElementById('editToggle');let hideEdit;[hot,toggle].forEach(el=>{el.addEventListener('mouseenter',()=>{clearTimeout(hideEdit);toggle.classList.add('show')});el.addEventListener('mouseleave',()=>{hideEdit=setTimeout(()=>{if(!this.editing)toggle.classList.remove('show')},400)})});hot.onclick=()=>this.toggleEdit();let hideControls;const reveal=()=>{document.body.classList.add('controls-visible');clearTimeout(hideControls);hideControls=setTimeout(()=>document.body.classList.remove('controls-visible'),2400)};addEventListener('pointermove',reveal);addEventListener('touchstart',reveal,{passive:true});reveal();
 }
}
const presentation=new SlidePresentation();
