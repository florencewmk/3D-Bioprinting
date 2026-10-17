"""Build the selected C design. Source PPTX is never modified.
Requires python-pptx, Pillow and PyMuPDF; render-source.pdf is a temporary
LibreOffice export with Arial substituted to avoid unavailable Futura metrics.
"""
from pathlib import Path
import base64,html,json,re,hashlib,argparse
import pymupdf as fitz
from pptx import Presentation
from PIL import Image
from io import BytesIO
from publication_chart import render_publication_slide
from organ_chart import render_organ_slide
from deck_structure import display_number, web_section, write_transcript
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source',type=Path,help='Original competition PPTX')
parser.add_argument('pdf',type=Path,help='PDF exported with Arial substitution')
parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'presentation')
args=parser.parse_args()
OUT=args.output.resolve()
BUILD=OUT/'build-metadata'
BUILD.mkdir(parents=True,exist_ok=True)
SOURCE=args.source.resolve()
PDF=args.pdf.resolve()
OUT.mkdir(parents=True,exist_ok=True)
prs=Presentation(SOURCE);pdf=fitz.open(PDF)
base=(Path(__file__).parent/'viewport-base.css').read_text()
H=lambda x:html.escape(str(x),quote=True)
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
def walk(shapes):
 for s in shapes:
  if s.shape_type==6:yield from walk(s.shapes)
  else:yield s
def texts(slide):
 result=[]
 for s in walk(slide.shapes):
  if s.has_text_frame and s.text.strip():result.append(s.text.replace('\v','\n'))
  if s.has_table:result+=[' | '.join(c.text for c in row.cells) for row in s.table.rows]
 return result
def uri(blob,mime):return 'data:'+mime+';base64,'+base64.b64encode(blob).decode()
def svg_scope(svg,n):
 # Inline SVG IDs must be unique across all 51 slides.
 ids=re.findall(r'\bid="([^"]+)"',svg)
 for old in sorted(set(ids),key=len,reverse=True):
  new=f's{n}_{old}'
  svg=svg.replace(f'id="{old}"',f'id="{new}"').replace(f'#{old}"',f'#{new}"').replace(f'#{old})',f'#{new})')
 return svg
TITLES=['Stereolithographic Bioprinting','About me','Contents','What comes to your mind?','From everyday objects to living tissue','From research to real-world use','The bioprinting landscape','Publication trends · 2000–2023','The organ shortage persists','Bioprinting technologies','A structure forms one layer at a time','SLA · DLP · multiphoton lithography','Four light-based curing routes','UV / violet and NIR','Thermal activation','Precision is a beginning','Tissue engineering in practice','From bioinks to bioprinters','Soft tissue research in orbit','3D-printed bio-plaster on ISS','Layers to living tissue','Engineering tomorrow’s possibilities','Thank you · Questions','Scientific references · 1','Scientific references · 2','Data and online sources · 1','Data and online sources · 2','Image references','Technical backup']
sections=[];data=[];manifest=[]
for i,(slide,page) in enumerate(zip(prs.slides,pdf)):
 n=i+1
 if n==2:continue
 src=texts(slide);title=TITLES[i] if i<len(TITLES) else (src[0] if src else f'Slide {n}')
 notes=slide.notes_slide.notes_text_frame.text if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None else ''
 data.append({'number':display_number(n),'title':title,'text':'\n\n'.join(src),'notes':notes})
 if n==3:data[-1]['text']=re.sub(r'Page (\d+)',lambda m:f'Page {display_number(int(m[1])):02d}',data[-1]['text'])
 # Posters are rebuilt directly in semantic HTML in the chosen design.
 special=n in [1,3,4,8,16,22,23,29] or 24<=n<=28
 art='';native=[]
 if not special:
  dictionary=page.get_text('dict')
  # Remove photographic template backgrounds and inherited ornamental rules.
  for info in page.get_image_info(xrefs=True):
   x0,y0,x1,y1=info['bbox'];w=x1-x0;h=y1-y0
   if info['xref'] and ((w>page.rect.width*.92 and h>page.rect.height*.72) or (w>page.rect.width*.85 and h<12)):
    page.delete_image(info['xref'])
  # Strip the original navigation/footer, replaced by consistent HTML chrome.
  page.add_redact_annot(fitz.Rect(0,0,page.rect.width,59),fill=False)
  page.add_redact_annot(fitz.Rect(0,506,page.rect.width,540),fill=False)
  page.apply_redactions(images=2,graphics=2,text=0)
  # The PDF supplies final line placement; scientific paths and photos remain vector/raster artwork.
  line_id=0
  for block in dictionary['blocks']:
   if block['type']!=0:continue
   for line in block['lines']:
    x0,y0,x1,y1=line['bbox'];direction=line['dir']
    if y0>=506 or abs(direction[1])>.01:continue
    if y0<59 and max(s['size'] for s in line['spans'])<20:continue
    spans=[s for s in line['spans'] if s['text'].strip()]
    if not spans:continue
    text=''.join(s['text'] for s in line['spans'])
    # A subtitle in the saved source overlaps its title; retain its wording in a clear separate line.
    if n==13 and ('4 types of STLG' in text or text.strip()=='methods'):
     page.add_redact_annot(fitz.Rect(x0-.2,y0-.15,x1+.2,y1+.15),fill=False)
     continue
    size=max(s['size'] for s in spans)*2
    baseline=spans[0]['origin'][1]*2
    top=baseline-size*.81
    if y0<59:top=96
    color=spans[0]['color'];color=f'#{color:06x}'
    if color.lower() in ['#ff0000','#c00000']:color='#e394ad'
    weight=500 if any(s['flags']&16 for s in spans) else 400
    native.append(f'<div class="textline editable" data-edit="s{n}-{line_id}" data-width="{(x1-x0)*2:.2f}" style="left:{x0*2:.2f}px;top:{top:.2f}px;font-size:{size:.2f}px;font-weight:{weight};color:{color}">{H(text)}</div>')
    line_id+=1
    # Remove only native text, retaining original plotted/rotated labels as artwork.
    page.add_redact_annot(fitz.Rect(x0-.2,y0-.15,x1+.2,y1+.15),fill=False)
  page.apply_redactions(images=0,graphics=0,text=0)
  # SVG images are downsampled losslessly in layout, compressed only in resolution/encoding.
  svg=page.get_svg_image(text_as_path=True)
  def compress_image(m):
   blob=base64.b64decode(re.sub(r'\s','',m.group(2)))
   try:
    im=Image.open(BytesIO(blob));im.thumbnail((2300,1800),Image.Resampling.LANCZOS);buf=BytesIO();im.save(buf,'WEBP',quality=88,method=5)
    return 'xlink:href="'+uri(buf.getvalue(),'image/webp')+'"'
   except Exception:return m.group(0)
  svg=re.sub(r'xlink:href="data:image/(png|jpeg);base64,([^"]+)"',compress_image,svg)
  svg=svg_scope(svg,n)
  art='<div class="source-art" aria-hidden="true">'+svg+'</div>'+''.join(native)
  if n==13:art+='<div class="route-note editable" data-edit="routes-subtitle">4 types of STLG bioprinting methods</div>'
 if n==8:art=render_publication_slide()
 if n==9:art=render_organ_slide()
 if n==1:
  art='''<div class="lattice" aria-hidden="true"></div><div class="hero"><p class="eyebrow editable" data-edit="cover-event">SOFE · BERLIN · 2026</p><h1><span class="editable" data-edit="cover-title">Stereolithographic</span><br><em class="editable gradient" data-edit="cover-subtitle">Bioprinting</em></h1><p class="hero-sub editable" data-edit="cover-tagline">3D bioprinting using light</p></div><p class="signature editable" data-edit="cover-author">Florence Mei Kuan Wong</p>'''
 if n==3:
  art='<div class="contents-heading"><p class="eyebrow">THE TALK</p><h1 class="editable" data-edit="contents-title">Contents</h1></div><div class="contents-list">'
  for k,(label,start) in enumerate([('Introduction',4),('Printing methods',10),('Applications',16),('Conclusion and discussion',21)]):
   art+=f'<button class="chapter" data-goto="{start}"><span class="chapter-no">0{k+1}</span><span>{label}</span><small>{start:02d} →</small></button>'
  art+='</div>'
 if n==4:
  art='''<div class="lattice" aria-hidden="true"></div><div class="poster"><p class="eyebrow">A QUESTION TO BEGIN</p><h1 class="editable" data-edit="opening-question">What comes to<br>your mind?</h1><p class="poster-sub editable" data-edit="opening-detail">When we mention additive manufacturing,<br>or 3D-printing?</p></div>'''
 if n==16:
  art='''<div class="poster half"><p class="eyebrow">APPLICATIONS</p><h1 class="editable" data-edit="precision">Precision<br>is a <em class="gradient">beginning.</em></h1></div>'''
 if n in [22,23,29]:
  copy={22:'Engineering<br>tomorrow’s<br><em class="gradient">possibilities.</em>',23:'Thank you.<br><em class="gradient">Questions?</em>',29:'Behind<br>the <em class="gradient">science.</em>'}[n]
  eyebrow={22:'LAYERS TO LIVING TISSUE',23:'STEREOLITHOGRAPHIC BIOPRINTING',29:'TECHNICAL BACKUP'}[n]
  art=f'<div class="lattice" aria-hidden="true"></div><div class="poster"><p class="eyebrow">{eyebrow}</p><h1 class="editable" data-edit="poster-{n}">{copy}</h1></div>'
  if n==29:art+='<p class="backup-original editable" data-edit="backup-label">Back up</p>'
 if 24<=n<=28:
  body=src[0];parts=re.split(r'(?=\[\d+\])',body);refs=[s.strip() for s in parts if re.match(r'\[\d+\]',s)]
  heading=body.split('\n')[0]
  art=f'<div class="references"><p class="eyebrow">SOURCES · {n-23:02d} / 05</p><h1>{H(heading)}</h1><div class="reference-list">'
  for k,ref in enumerate(refs):
   safe=H(ref);safe=re.sub(r'(https?://[^\s&lt;]+)',r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>',safe)
   art+=f'<p class="editable" data-edit="ref-{n}-{k}">{safe}</p>'
  art+='</div></div>'
 # Embedded MP4s retain native browser playback. Each is embedded once in the HTML.
 videos=[]
 for sh in slide.shapes:
  if sh.shape_type!=16:continue
  links=sh._element.xpath('.//a:videoFile')
  if not links:continue
  rid=links[0].get(R+'link');rel=slide.part.rels[rid]
  if rel.is_external:continue
  blob=rel.target_part.blob
  mime='video/mp4';video_src=uri(blob,mime)
  x=sh.left/prs.slide_width*1920;y=sh.top/prs.slide_height*1080;w=sh.width/prs.slide_width*1920;h=sh.height/prs.slide_height*1080
  if n==16:x,y,w,h=1000,270,810,540
  # Saved poster art is a genuine source frame, where available.
  blips=sh._element.xpath('.//a:blip');poster=''
  if blips:
   rid=blips[0].get(R+'embed')
   if rid:
    part=slide.part.related_part(rid);poster=uri(part.blob,part.content_type)
  videos.append(f'<video controls playsinline preload="metadata" aria-label="{H(sh.name)}" poster="{poster}" style="left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px" src="{video_src}"></video>')
  manifest.append({'slide':display_number(n),'media':sh.name,'bytes':len(blob)})
 if n==16:art+='<p class="media-credit">Source: Readily3D · Tomolite Bioprinter · accessed 14 October 2026</p>'
 section='Introduction' if n<10 else 'Printing methods' if n<16 else 'Applications' if n<21 else 'Conclusion' if n<24 else 'References' if n<29 else 'Technical backup'
 nav=''
 if n!=1:
  nav='<nav class="section-nav" aria-label="Talk sections">'+''.join(f'<button data-goto="{start}" class="{"current" if label==section else ""}">{label}</button>' for label,start in [('Introduction',4),('Printing methods',10),('Applications',16),('Conclusion',21)])+f'<span>{"REFERENCES" if 24<=n<29 else "BACKUP" if n>=29 else ""}</span></nav>'
 footer=f'<footer><span>15 October 2026</span><span>Florence Mei Kuan Wong</span><span>{n:02d} / 51</span></footer>' if n!=1 else ''
 comment=notes.replace('--','—').replace('<','&lt;')
 sections.append(web_section(f'<section class="slide {"active visible" if n==1 else ""} {"poster-slide" if special else ""}" id="slide-{n}" aria-label="{n}. {H(title)}" aria-hidden="{str(n!=1).lower()}">{nav}{art}{"".join(videos)}{footer}<div class="sr-only">{H(chr(10).join(src))}</div><!-- Speaker notes: {comment} --></section>',n))
(BUILD/'deck-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
(BUILD/'media-manifest.json').write_text(json.dumps(manifest,indent=2))
# A readable transcript is a separate artifact, while presentation notes remain embedded.
write_transcript(OUT/'transcript.md',data)
css=(Path(__file__).parent/'deck.css').read_text()+'\n'+(Path(__file__).parent/'publication-chart.css').read_text()+'\n'+(Path(__file__).parent/'organ-chart.css').read_text();js=(Path(__file__).parent/'deck.js').read_text()+'\n'+(Path(__file__).parent/'publication-chart.js').read_text()+'\n'+(Path(__file__).parent/'organ-chart.js').read_text()
shell=(Path(__file__).parent/'shell.html').read_text()
result=shell.replace('FONT_CSS',(Path(__file__).parent/'fonts.css').read_text()).replace('BASE_CSS',base).replace('DECK_CSS',css).replace('SLIDE_SECTIONS','\n'.join(sections)).replace('SOURCE_DATA',json.dumps(data,ensure_ascii=False).replace('</','<\\/')).replace('DECK_JS',js)
(OUT/'index.html').write_text('\n'.join(line.rstrip() for line in result.splitlines()).rstrip()+'\n')
print(json.dumps({'slides':len(data),'native_text_lines':sum(s.count('class="textline') for s in sections),'videos':manifest,'html_bytes':len(result.encode()),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()},indent=2))
