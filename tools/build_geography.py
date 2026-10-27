"""Reproduce geography tables from repository-local OpenAlex and company sources."""
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/geography-2025'
RAW=BASE/'raw'
DATE='2026-10-27'

def read_json(p):
    with (gzip.open(p,'rt',encoding='utf-8') if p.suffix=='.gz' else p.open(encoding='utf-8')) as f:return json.load(f)

def write_csv(name,rows,fields=None):
    if not fields:fields=list(rows[0])
    with (BASE/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def ranked(rows,field,rank_field):
    rows.sort(key=lambda r:(-r[field],str(r.get('name',r.get('country',''))),str(r.get('id',''))))
    prev=None
    for i,r in enumerate(rows,1):
        if r[field]!=prev:rank=i
        r[rank_field]=rank;prev=r[field]
    return rows

def build():
    pages=sorted(RAW.glob('historical-*.gz'))+sorted(RAW.glob('recent-*.gz'))
    allw={};seen=Counter();page_meta=[]
    for p in pages:
        d=read_json(p);page_meta.append({'file':p.name,'count':d['meta']['count'],'rows':len(d['results'])})
        for w in d['results']:allw[w['id']]=w;seen[w['id']]+=1
    excluded=[{'work_id':w['id'],'title':w['title'],'publication_year':w['publication_year'],
        'reason':'Outside defined 2000–2025 publication window; metadata dates not manually corrected'}
        for w in allw.values() if not 2000<=w['publication_year']<=2025]
    works={k:v for k,v in allw.items() if 2000<=v['publication_year']<=2025}
    assert all(not w['is_retracted'] for w in works.values())
    assert all(not w.get('is_authors_truncated') for w in works.values())
    metadata={}
    for p in sorted(RAW.glob('institutions-*.gz')):
        metadata.update({i['id']:i for i in read_json(p)['results']})
    names={x['key'].rsplit('/',1)[-1]:x['key_display_name'] for x in read_json(RAW/'countries-api.json')['group_by']}
    names['TR']='Türkiye'
    countries=defaultdict(lambda:{'works':set(),'recent':set(),'year2025':set(),'inst':set(),'authors':set(),'fractional':0.0})
    institutions=defaultdict(lambda:{'works':set(),'recent':set(),'year2025':set(),'authors':set(),'stub':{},'countries':set()})
    authors=defaultdict(lambda:{'works':set(),'recent':set(),'year2025':set(),'last_date':'','aff_date':'','latest':{},'latest_works':set(),'stub':{},'all_countries':set()})
    years=Counter();unknown_country=Counter();unknown_inst=Counter();work_rows=[]
    for wid,w in sorted(works.items(),key=lambda t:(t[1]['publication_date'],t[0])):
        year=w['publication_year'];recent=year>=2021;years[year]+=1
        cs={i['country_code'] for a in w['authorships'] for i in a['institutions'] if i.get('country_code')}
        if not cs:unknown_country['all']+=1;unknown_country['recent']+=int(recent)
        if not any(a['institutions'] for a in w['authorships']):unknown_inst['all']+=1
        for code in cs:
            c=countries[code];c['works'].add(wid);c['fractional']+=1/len(cs)
            if recent:c['recent'].add(wid)
            if year==2025:c['year2025'].add(wid)
        for a in w['authorships']:
            aid=a['author']['id']
            if aid:
                au=authors[aid];au['stub']=a['author'];au['works'].add(wid)
                if recent:au['recent'].add(wid)
                if year==2025:au['year2025'].add(wid)
                date=w['publication_date']
                if date>au['last_date']:au['last_date']=date
                if a['institutions'] and date>au['aff_date']:au['aff_date']=date;au['latest']={};au['latest_works']=set()
                if a['institutions'] and date==au['aff_date']:
                    au['latest_works'].add(wid)
                    for i in a['institutions']:au['latest'][i['id']]=i
            for i in a['institutions']:
                iid=i['id'];ins=institutions[iid];ins['stub']=i;ins['works'].add(wid)
                if aid:ins['authors'].add(aid)
                if recent:ins['recent'].add(wid)
                if year==2025:ins['year2025'].add(wid)
                code=i.get('country_code')
                if code:
                    ins['countries'].add(code)
                    if aid:au['all_countries'].add(code)
                    if recent:
                        countries[code]['inst'].add(iid)
                        if aid:countries[code]['authors'].add(aid)
        work_rows.append({'work_id':wid,'doi':w.get('doi') or '', 'title':w['title'],
            'publication_date':w['publication_date'],'publication_year':year,'work_type':w['type'],
            'institution_country_codes':';'.join(sorted(cs)),
            'institution_ids':';'.join(sorted({i['id'] for a in w['authorships'] for i in a['institutions']})),
            'author_ids':';'.join(sorted({a['author']['id'] for a in w['authorships'] if a['author']['id']}))})
    companies=read_json(BASE/'company_research.json')
    company_countries=defaultdict(lambda:Counter())
    for c in companies:
        cc=company_countries[c['country_code']]
        cc['records']+=1
        if c['independent_sample_included']:cc['independent_sample']+=1
        if c['supplier_sample_included']:cc['supplier_sample']+=1
        if c['documented_2025_activity']:
            cc['documented2025']+=1
            if c['supplier_sample_included']:cc['supplier2025']+=1
    country_rows=[]
    for code in set(countries)|set(company_countries):
        c=countries[code];cc=company_countries.get(code,Counter())
        country_rows.append({'country_code':code,'country':names.get(code,code),
            'works_2021_2025':len(c['recent']),'works_2000_2025':len(c['works']),
            'works_2025':len(c['year2025']),'fractional_works_2000_2025':round(c['fractional'],6),
            'distinct_affiliation_ids_2021_2025':len(c['inst']),
            'distinct_author_ids_2021_2025':len(c['authors']),
            'researched_company_records':cc['records'],
            'independent_company_sample':cc['independent_sample'],
            'bioprinter_supplier_sample':cc['supplier_sample'],
            'companies_with_2025_activity_evidence':cc['documented2025'],
            'suppliers_with_2025_activity_evidence':cc['supplier2025'],
            'company_count_scope':'Curated sample, not a census; locations have source-specific dates',
            'research_source':'OpenAlex archived work metadata; title/abstract query, 2000–2025',
            'retrieved_date':DATE})
    ranked(country_rows,'works_2000_2025','rank_2000_2025')
    ranked(country_rows,'works_2021_2025','rank_2021_2025')
    # Rank tied publication totals equally; alphabetic display order only breaks ties visually.
    country_rows.sort(key=lambda r:(-r['works_2021_2025'],r['country']))
    institution_rows=[]
    for iid,v in institutions.items():
        m=metadata.get(iid,{})
        g=m.get('geo') or {};stub=v['stub'];code=stub.get('country_code') or m.get('country_code') or ''
        institution_rows.append({'id':iid,'name':m.get('display_name') or stub.get('display_name',''),
            'country_code':code,'country':names.get(code,code),'city':g.get('city') or '',
            'latitude':g.get('latitude'),'longitude':g.get('longitude'),
            'works_2021_2025':len(v['recent']),'works_2000_2025':len(v['works']),
            'works_2025':len(v['year2025']),'distinct_author_ids':len(v['authors']),
            'type':m.get('type') or stub.get('type',''),'ror':m.get('ror') or stub.get('ror') or '',
            'homepage_url':m.get('homepage_url') or '',
            'geo_time_basis':'Current OpenAlex institution metadata retrieved 2026-10-27; not a historical campus audit',
            'source_url':iid.replace('https://openalex.org/','https://api.openalex.org/institutions/'),
            'retrieved_date':DATE})
    ranked(institution_rows,'works_2021_2025','rank_2021_2025')
    author_rows=[];location_rows=[]
    for aid,v in authors.items():
        latest=list(v['latest'].values());latest_codes=sorted({i['country_code'] for i in latest if i.get('country_code')})
        name=v['stub'].get('display_name','')
        row={'id':aid,'name':name,'orcid':v['stub'].get('orcid') or '',
            'works_2021_2025':len(v['recent']),'works_2000_2025':len(v['works']),'works_2025':len(v['year2025']),
            'last_observed_publication_date':v['last_date'],'last_observed_affiliation_date':v['aff_date'],
            'last_observed_country_codes':';'.join(latest_codes),
            'last_observed_affiliation_ids':';'.join(sorted(v['latest'])),
            'last_observed_affiliations':'; '.join(sorted(i['display_name'] for i in latest)),
            'location_source_work_ids':';'.join(sorted(v['latest_works'])),
            'location_basis':'Own affiliations on latest dated work(s) with matched institutions in this corpus; not current employment or nationality',
            'retrieved_date':DATE}
        author_rows.append(row)
        for i in latest or [{}]:
            iid=i.get('id','');g=(metadata.get(iid,{}).get('geo') or {})
            location_rows.append({'author_id':aid,'author_name':name,'institution_id':iid,
                'institution_name':i.get('display_name',''),'country_code':i.get('country_code') or '',
                'city':g.get('city') or '', 'latitude':g.get('latitude'),'longitude':g.get('longitude'),
                'last_observed_publication_date':v['last_date'],'last_observed_affiliation_date':v['aff_date'],
                'works_2021_2025':len(v['recent']),
                'location_source_work_ids':';'.join(sorted(v['latest_works'])),
                'coordinate_basis':'Affiliated institution location; not a person location',
                'retrieved_date':DATE})
    ranked(author_rows,'works_2021_2025','rank_2021_2025')
    write_csv('countries.csv',country_rows)
    write_csv('top20_countries.csv',country_rows[:20])
    write_csv('top20_countries_2000_2025.csv',sorted(country_rows,key=lambda r:(-r['works_2000_2025'],r['country']))[:20])
    write_csv('affiliations.csv',institution_rows)
    write_csv('authors.csv',author_rows)
    write_csv('author_locations.csv',location_rows)
    write_csv('works.csv',work_rows)
    write_csv('excluded_records.csv',excluded)
    write_csv('annual_corpus_counts.csv',[{'year':y,'works':years[y]} for y in sorted(years)])
    company_country_rows=[{'country_code':code,'country':names.get(code,code),
        'researched_records':c['records'],'independent_company_sample':c['independent_sample'],
        'supplier_sample':c['supplier_sample'],'companies_with_2025_activity_evidence':c['documented2025'],
        'suppliers_with_2025_activity_evidence':c['supplier2025'],
        'scope':'Research sample only; unlisted companies are not zeros in the global population'}
        for code,c in sorted(company_countries.items(),key=lambda x:(-x[1]['supplier_sample'],x[0]))]
    write_csv('company_countries.csv',company_country_rows)
    # Independent per-year control, downloaded by the API before page retrieval.
    controls={int(x['key']):x['count'] for x in read_json(RAW/'years-api.json')['group_by'] if 2000<=int(x['key'])<=2025}
    assert dict(years)==controls, (years,controls)
    assert sum(years.values())==len(works)
    assert abs(sum(c['fractional'] for c in countries.values())-(len(works)-unknown_country['all']))<1e-6
    missing_inst_ids=sorted(set(institutions)-set(metadata))
    verification={'retrieved_date':DATE,'publication_window':['2000-01-01','2025-12-31'],
        'recent_window':['2021-01-01','2025-12-31'],
        'retrieved_rows':sum(seen.values()),'retrieved_unique_ids_before_date_screen':len(allw),
        'duplicate_rows_removed':sum(n-1 for n in seen.values()),
        'duplicate_ids':[k for k,v in seen.items() if v>1],
        'excluded_before_2000':len(excluded),'included_works':len(works),
        'included_works_2021_2025':sum(n for y,n in years.items() if y>=2021),
        'included_works_2025':years[2025],
        'distinct_country_region_codes':sum(bool(v['works']) for v in countries.values()),
        'distinct_affiliation_ids':len(institutions),'distinct_author_ids':len(authors),
        'works_without_institution_country':unknown_country['all'],
        'works_without_institution_country_2021_2025':unknown_country['recent'],
        'works_without_any_institution':unknown_inst['all'],
        'author_ids_without_last_observed_institution':sum(not a['last_observed_affiliation_ids'] for a in author_rows),
        'institution_ids_without_current_metadata':missing_inst_ids,
        'truncated_authorship_work_count':0,
        'annual_api_reconciliation':'PASS: all 2000–2025 annual totals match separately archived year aggregation',
        'fractional_country_reconciliation':'PASS: sums to works with at least one known institution country',
        'initial_country_api_total':read_json(RAW/'countries-api.json')['meta']['count'],
        'initial_year_api_total':read_json(RAW/'years-api.json')['meta']['count'],
        'api_live_update_note':'Initial country query count differs from year/export control; use archived deduplicated corpus, not a splice of live aggregate calls.',
        'company_records':len(companies),'company_countries':len(company_countries),
        'company_records_2025_activity_documented':sum(c['documented_2025_activity'] for c in companies),
        'supplier_sample':sum(c['supplier_sample_included'] for c in companies),
        'top20_recent_codes':[r['country_code'] for r in country_rows[:20]],
        'page_metadata':page_meta}
    (BASE/'verification.json').write_text(json.dumps(verification,indent=2,ensure_ascii=False)+'\n')
    # Small workbook input includes complete country/company data and top 200 entities.
    bundle={'countries':country_rows,'companies':companies,'company_countries':company_country_rows,
        'affiliations':institution_rows[:200],'authors':author_rows[:200],
        'annual_counts':[{'year':y,'works':years[y]} for y in sorted(years)],'verification':verification}
    (BASE/'workbook_data.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in verification.items() if k not in ['page_metadata','duplicate_ids']},ensure_ascii=False,indent=2))
    print('Top 20:',[(r['country'],r['works_2021_2025']) for r in country_rows[:20]])

if __name__=='__main__':build()
