"""Extract the six 2025 organ lists from Newsletter Transplant2026, PDF pp66–74.
Normalize sideways pages, group digit glyphs by source row/column, preserve blanks.
"""
from pathlib import Path
from pypdf import PdfReader,PdfWriter
from io import BytesIO
import pdfplumber,json,csv,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/organ-transplants';src=OUT/'sources/NEWSLETTER-2026_alta.pdf'
r=PdfReader(src);w=PdfWriter()
for i in range(65,74):
 p=r.pages[i];p.rotate(90);p.transfer_rotation_to_content();w.add_page(p)
b=BytesIO();w.write(b);b.seek(0);records=[]
organs=['Kidney','Liver','Heart','Lung','Pancreas','Small bowel']
with pdfplumber.open(b) as d:
 for page_index,page in enumerate(d.pages):
  words=page.extract_words();centres=sorted([a for a in words if a['text']=='CENTRES' and a['x0']<200],key=lambda a:a['top']);assert len(centres)==6
  first_y=centres[0]['top'];digits=sorted([a for a in page.chars if a['text'].isdigit() and 295<a['x0']<page.width-35 and abs(a['top']-first_y)<.6],key=lambda a:a['x0'])
  groups=[]
  for a in digits:
   if not groups or a['x0']-groups[-1][-1]['x1']>15:groups.append([])
   groups[-1].append(a)
  xs=[sum((a['x0']+a['x1'])/2 for a in g)/len(g) for g in groups];assert len(xs) in [8,9,12,13],xs
  bounds=[295]+[(a+b)/2 for a,b in zip(xs,xs[1:])]+[page.width-30]
  included=next(a for a in words if a['text']=='included' and first_y<a['top']<first_y+20);step=included['top']-first_y
  for org,cen in zip(organs,centres):
   for metric,delta in [('waiting_year_end',3),('deaths_during_year',4)]:
    y=cen['top']+delta*step
    for col in range(len(xs)):
     chars=sorted([a for a in page.chars if bounds[col]<=a['x0']<bounds[col+1] and abs(a['top']-y)<.6 and a['text'].isdigit()],key=lambda a:a['x0'])
     raw=''.join(a['text'] for a in chars);value=int(raw) if raw else None
     records.append({'pdf_page':page_index+66,'country_column':col+1,'organ':org,'metric':metric,'value':value,'source_row_top':round(y,3),'raw_digits':raw})
summary={o:{m:sum(x['value'] for x in records if x['organ']==o and x['metric']==m and x['value'] is not None) for m in ['waiting_year_end','deaths_during_year']} for o in organs}
summary['Total']={m:sum(summary[o][m] for o in organs) for m in ['waiting_year_end','deaths_during_year']}
with (OUT/'waiting_lists_2025_cells.csv').open('w') as f:
 cw=csv.DictWriter(f,fieldnames=list(records[0]));cw.writeheader();cw.writerows(records)
(OUT/'waiting_lists_2025_summary.json').write_text(json.dumps({'year':2025,'source':'https://www.transplant-observatory.org/wp-content/uploads/2026/10/NEWSLETTER-2026_alta.pdf','pdf_pages':[66,74],'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'counting_unit':'sum of reported organ-list entries; not deduplicated patients','summary':summary},indent=2)+'\n')
print(json.dumps(summary,indent=2));print('cells',len(records),'missing',sum(x['value'] is None for x in records))
