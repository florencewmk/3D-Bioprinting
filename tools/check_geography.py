"""Validate the delivered geography tables against their explicit work-ID links."""
import csv
import json
import math
from collections import Counter,defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'data/geography-2025'

def rows(name):
    with (B/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def check():
    v=json.loads((B/'verification.json').read_text())
    works=rows('works.csv');countries=rows('countries.csv');inst=rows('affiliations.csv');authors=rows('authors.csv')
    assert len(works)==v['included_works']==len({w['work_id'] for w in works})
    assert len(inst)==v['distinct_affiliation_ids']==len({i['id'] for i in inst})
    assert len(authors)==v['distinct_author_ids']==len({a['id'] for a in authors})
    cc=Counter();recent=Counter();ic=Counter();ac=Counter();annual=Counter();missing=0
    all_i=set();all_a=set();country_inst=defaultdict(set);country_auth=defaultdict(set)
    for w in works:
        y=int(w['publication_year']);assert 2000<=y<=2025
        annual[y]+=1
        c=set(filter(None,w['institution_country_codes'].split(';')))
        if not c:missing+=1
        cc.update(c)
        if y>=2021:recent.update(c)
        ii=set(filter(None,w['institution_ids'].split(';')));aa=set(filter(None,w['author_ids'].split(';')))
        ic.update(ii);ac.update(aa);all_i.update(ii);all_a.update(aa)
    assert all_i=={i['id'] for i in inst}
    assert all_a=={a['id'] for a in authors}
    for c in countries:
        assert int(c['works_2000_2025'])==cc[c['country_code']]
        assert int(c['works_2021_2025'])==recent[c['country_code']]
    for i in inst:
        assert int(i['works_2000_2025'])==ic[i['id']]
        for key,lo,hi in [('latitude',-90,90),('longitude',-180,180)]:
            if i[key]:assert lo<=float(i[key])<=hi
    for a in authors:
        assert int(a['works_2000_2025'])==ac[a['id']]
        assert not a['last_observed_affiliation_date'] or a['last_observed_affiliation_date']<=a['last_observed_publication_date']<='2025-12-31'
    assert annual==Counter({int(r['year']):int(r['works']) for r in rows('annual_corpus_counts.csv')})
    assert missing==v['works_without_institution_country']
    assert abs(sum(float(c['fractional_works_2000_2025']) for c in countries)-(len(works)-missing))<0.0001
    top=rows('top20_countries.csv');assert top==countries[:20]
    assert rows('top20_countries_2000_2025.csv')==sorted(countries,key=lambda c:(-int(c['works_2000_2025']),c['country']))[:20]
    # Keep the human-readable GitHub summary synchronized with data.
    table=[line.split('|') for line in (B/'README.md').read_text().splitlines() if line.startswith('| ') and len(line.split('|'))==6]
    table=[r for r in table if r[1].strip().isdigit()]
    assert len(table)==20
    for r,c in zip(table,top):
        assert r[2].strip()==c['country']
        assert int(r[3].strip().replace(',',''))==int(c['works_2021_2025'])
        assert int(r[4].strip().replace(',',''))==int(c['works_2000_2025'])
    companies=json.loads((B/'company_research.json').read_text())
    assert len(companies)==40==len({c['company_id'] for c in companies})
    assert sum(c['documented_2025_activity'] for c in companies)==v['company_records_2025_activity_documented']
    assert len({c['country_code'] for c in companies})==v['company_countries']
    for c in companies:
        assert c['activity_source_url'].startswith('https://') and c['location_source_url'].startswith('https://')
        assert c['evidence_year']<=2025
        if c['status_at_2025_cutoff'].startswith(('Production ended','Acquired')):assert not c['supplier_sample_included']
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    xlsx=B/'Bioprinting-Geography-through-2025.xlsx'
    if xlsx.exists():
        with zipfile.ZipFile(xlsx) as z:
            assert z.testzip() is None
            book=ET.fromstring(z.read('xl/workbook.xml'))
            names=[s.get('name') for s in book.findall('s:sheets/s:sheet',ns)]
            assert names==['Countries','Companies','Company countries','Affiliations','Authors','Annual corpus','Methods']
            for file in z.namelist():
                if file.startswith('xl/worksheets/sheet') and file.endswith('.xml'):
                    sheet=ET.fromstring(z.read(file))
                    assert not sheet.findall('.//s:c[@t="e"]',ns),file
                    assert sheet.find('s:sheetViews/s:sheetView/s:pane',ns) is not None
            assert len([n for n in z.namelist() if n.startswith('xl/tables/table') and n.endswith('.xml')])==7
    print(f'PASS: {len(works):,} works, {len(countries)} countries/regions, {len(inst):,} affiliations, {len(authors):,} author IDs, 40 company records; country/entity/annual links reconcile.')
    print('Workbook: seven sheets, filterable tables, frozen panes, ZIP/XML and cell-error checks passed.' if xlsx.exists() else 'Workbook not yet built.')

if __name__=='__main__':check()
