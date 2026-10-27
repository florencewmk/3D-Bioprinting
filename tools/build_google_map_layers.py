"""Prepare Google My Maps layers from the saved geography snapshot.

KML contains only name/description attributes to stay within My Maps cell limits.
Company/country CSVs use Google place-name geocoding at city/country precision.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/geography-2025'
OUT=DATA/'google-map'
SOURCE='https://github.com/florencewmk/3D-Bioprinting/tree/main/data/geography-2025'
NS='http://www.opengis.net/kml/2.2'
ET.register_namespace('',NS)

def read(name):
    with (DATA/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def coords(r):
    try:
        lat,lon=float(r['latitude']),float(r['longitude'])
        if not math.isfinite(lat+lon) or not(-90<=lat<=90 and -180<=lon<=180) or (lat==0 and lon==0):return None
        return lat,lon
    except (ValueError,KeyError,TypeError):return None

def elem(parent,tag,text=None):
    e=ET.SubElement(parent,'{'+NS+'}'+tag)
    if text is not None:e.text=str(text)
    return e

def kml(name,title,records,color):
    root=ET.Element('{'+NS+'}kml');d=elem(root,'Document');elem(d,'name',title)
    s=elem(d,'Style');s.set('id','marker');ic=elem(s,'IconStyle')
    elem(ic,'color','ff'+color[4:6]+color[2:4]+color[0:2]);elem(ic,'scale','1.0')
    for label,description,lat,lon in records:
        pm=elem(d,'Placemark');elem(pm,'name',label);elem(pm,'description',description);elem(pm,'styleUrl','#marker')
        elem(elem(pm,'Point'),'coordinates',f'{lon},{lat},0')
    ET.indent(root)
    dest=OUT/name;ET.ElementTree(root).write(dest,encoding='utf-8',xml_declaration=True)
    assert len(records)<=2000 and dest.stat().st_size<5_000_000
    return {'file':name,'layer_title':title,'features':len(records),'geometry':'Institution coordinates','color':'#'+color}

def write_csv(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    institutions=read('affiliations.csv');authors=read('authors.csv');locations=read('author_locations.csv')
    countries={r['country_code']:r['country'] for r in read('countries.csv')}
    companies=json.loads((DATA/'company_research.json').read_text())
    manifest=[];missing=[]
    for name,title,subset,color in [
        ('03-affiliations-top100.kml','Research affiliations — top 100','top','8158BA'),
        ('04-affiliations-other-1.kml','Other affiliations — part 1','part1','A894C1'),
        ('05-affiliations-other-2.kml','Other affiliations — part 2','part2','A894C1'),
        ('06-affiliations-other-3.kml','Other affiliations — part 3','part3','A894C1')]:
        selected={'top':institutions[:100],'part1':institutions[100:2000],'part2':institutions[2000:4000],'part3':institutions[4000:]}[subset]
        records=[]
        for r in selected:
            xy=coords(r)
            if xy is None:missing.append({'type':'affiliation','id':r['id'],'name':r['name'],'reason':'No valid institution coordinates'});continue
            desc=(f"Country: {r['country']}\nCity: {r['city']}\nRecent publication rank: {r['rank_2021_2025']}\n"
                f"Works 2021–2025: {r['works_2021_2025']}\nWorks 2000–2025: {r['works_2000_2025']}\n"
                f"Works 2025: {r['works_2025']}\nInstitution: {r['id']}\nROR: {r['ror']}\n"
                "Institution point from OpenAlex metadata retrieved 27 October 2026; not a historical campus audit.\n"
                "Keyword-defined articles/reviews; institution IDs can include parent/child organizations.\n"+SOURCE)
            records.append((r['name'],desc,*xy))
        manifest.append(kml(name,title,records,color))
    chosen={r['id']:r for r in authors[:100]};records=[];located=set()
    for r in locations:
        if r['author_id'] not in chosen:continue
        xy=coords(r)
        if xy is None:continue
        located.add(r['author_id']);a=chosen[r['author_id']]
        desc=(f"Recent publication rank: {a['rank_2021_2025']}\nWorks 2021–2025: {a['works_2021_2025']}\n"
            f"Works 2000–2025: {a['works_2000_2025']}\nInstitution: {r['institution_name']}\n"
            f"Country: {countries.get(r['country_code'],r['country_code'])}\nCity: {r['city']}\n"
            f"Last observed affiliation date: {r['last_observed_affiliation_date']}\nAuthor ID: {a['id']}\n"
            f"ORCID: {a['orcid']}\nEvidence work IDs: {r['location_source_work_ids']}\n"
            "Point locates an affiliated institution, not a person. Not current employment or nationality. "
            "Multiple markers can represent one author's multiple affiliations.\n"+SOURCE)
        records.append((a['name']+' — '+r['institution_name'],desc,*xy))
    for aid in set(chosen)-located:missing.append({'type':'author','id':aid,'name':chosen[aid]['name'],'reason':'No valid coordinates on last-observed institution links'})
    manifest.append(kml('07-authors-top100.kml','Authors — top 100, institutional locations',records,'E57A35'))
    file='01-companies.csv';title='Companies'
    rows=[]
    for c in companies:
        if not c['independent_sample_included']:continue
        city=c['city_or_site'].split(' / ')[0].replace(' (Zwijnaarde)','').replace(' (Agia Paraskevi)','').replace(' area','')
        country=countries.get(c['country_code'],c['country_code'])
        rows.append({'Name':c['company_name'],'Location':f'{city}, {country}',
            'Role':c['role'],'Product':c['product_or_platform'],'2025 status':c['status_at_2025_cutoff'],
            'Evidence and sources':f"Activity: {c['activity_source_url']}\nLocation: {c['location_source_url']}\n{c['notes']}\nCity-level approximation, not a precise office. Location dates are source-specific; current sources retrieved 27 October 2026.\n{SOURCE}"})
    write_csv(file,rows);manifest.append({'file':file,'layer_title':title,'features':len(rows),
        'geometry':'Google geocodes city/country, approximate','position_column':'Location','title_column':'Name'})
    rows=[]
    for r in read('top20_countries_2000_2025.csv'):
        rows.append({'Name':f"{r['rank_2000_2025']}. {r['country']} — {int(r['works_2000_2025']):,} works",
            'Location':r['country'],'Works 2000–2025':r['works_2000_2025'],'Works 2021–2025':r['works_2021_2025'],
            'Recent rank':r['rank_2021_2025'],'Source and scope':'Country-level summary marker, not a laboratory or office. Full counting of institution countries; international papers count in multiple countries. '+SOURCE})
    write_csv('08-top20-countries.csv',rows);manifest.append({'file':'08-top20-countries.csv',
        'layer_title':'Top 20 countries — publications 2000–2025','features':20,'geometry':'Google country place-name geocoding',
        'position_column':'Location','title_column':'Name'})
    if missing:write_csv('unmapped.csv',missing)
    manifest.sort(key=lambda r:r['file'])
    for r in manifest:r['sha256']=hashlib.sha256((OUT/r['file']).read_bytes()).hexdigest()
    summary={'source_retrieval_date':'2026-10-27','source_dataset':SOURCE,'map_title':'Bioprinting World Map — Research & Companies through 2025',
        'layers':manifest,'total_features':sum(r['features'] for r in manifest),
        'affiliation_records':len(institutions),'mapped_authors':len(located),'selected_authors':len(chosen),
        'unmapped_records':len(missing),'excluded_company_records':['Allevi — production ended 2023','Allegro 3D — grouped under CELLINK'],
        'default_visible':['01-companies.csv','03-affiliations-top100.kml'],
        'company_precision':'City-level Google geocoding, not office coordinates',
        'author_precision':'Last observed institutional affiliation through 2025; not current person location'}
    assert summary['total_features']<10000
    (OUT/'layer-manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
