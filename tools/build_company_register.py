"""Build a curated company register and keep the 2021 map as an audit baseline.

The source tuples are research notes, not a claim of an exhaustive company census.
"""
import csv
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/geography-2025'
DATE = '2026-10-27'
MAP = 'https://www.google.com/maps/d/u/0/viewer?mid=1AO84VH2CJ_TBndoVirj7yFfcitTXe0K3'
# name, ISO2, city/site, role, product/platform, technology, evidence period,
# cutoff status, activity source, location source, qualifications
ROWS = [
('CELLINK','SE','Gothenburg','Bioprinter supplier','BIO X; BIO X6; LUMEN X','Extrusion; DLP',2025,'2025 documented',
 'https://www.cellink.com/wp-content/uploads/2025/05/BIO-X-Series-Brochure_31.03.25_DIGITAL.pdf',
 'https://www.cellink.com/about-cellink/','Count CELLINK once. Overseas sales offices are not extra companies.'),
('Fluicell','SE','Mölndal / Gothenburg area','Bioprinter supplier','Biopixlar; Biopixlar AER','Microfluidic single-cell deposition',2025,'2025 documented',
 'https://mfn.se/a/fluicell/fluicell-erhaller-koporder-gallande-biopixlar-fran-the-francis-crick-institute.iframe',
 'https://storage.mfn.se/db1c3bd0-e121-4ece-aa52-9fd9aaba3e49/fluicell-q2-2025.pdf','2025 issuer release documents a Biopixlar order. Nexocyte is the tissue-therapeutics platform.'),
('Nanoscribe','DE','Eggenstein-Leopoldshafen','Bioprinter supplier','Quantum X bio','Two-photon polymerization',2021,'Pre-2025 product; live site',
 'https://www.nanoscribe.com/en/news-insights/news/nanoscribe-and-cellink-introduce-quantum-x-bio/',
 'https://www.nanoscribe.com/en/products/high-resolution-3d-bioprinter-quantum-x-bio/','Product jointly developed with CELLINK. Separate German operating company, not a second Swedish location. 2025 sales of this particular model not independently counted.'),
('UpNano','AT','Vienna','Bioprinter supplier','NanoOne Bio','Two-photon polymerization',2021,'Pre-2025 product; live site',
 'https://www.upnano.com/exceptional-versatile-innovative-printing-system-successfully-established-in-both-industry-and-academia/',
 'https://www.upnano.com/about/','Current Bio package: https://www.upnano.com/3d-printers/nanoone-bio/ . Historical source proves NanoOne sales, not a 2025 Bio-package sale.'),
('GeSiM','DE','Radeberg','Bioprinter supplier','BioScaffolder','Extrusion; dispensing',2018,'Pre-2025 product; live site',
 'https://gesim.de/wp-content/uploads/2019/01/GeSiM_BS-Tools_2018_web.pdf',
 'https://gesim.de/kontakt/','Official product brochure supports product and German location. Live site checked in 2026.'),
('Axolotl Biosystems','TR','Istanbul','Bioprinter supplier','Axo A3; Axo A6','Extrusion; melt electrowriting',2021,'Pre-2025 product; live site',
 'https://www.axolotlbio.com/',
 'https://www.axolotlbio.com/','Pre-2025 presence also in legacy map. Not the Canadian bioink company Axolotl Biosciences. Old map incorrectly associated its URL with CELLnTEC in Switzerland.'),
('REGENHU','CH','Villaz-St-Pierre','Bioprinter supplier','R-GEN series','Extrusion; jetting; electrowriting',2020,'Pre-2025 product; live site',
 'https://www.regenhu.com/community/news/regenhu-launches-r-gen-series-and-shaper/',
 'https://www.regenhu.com/contact/','Current Swiss office and product page checked. A product launch is not annual sales volume.'),
('Readily3D','CH','Epalinges / Lausanne area','Bioprinter supplier','Tomolite','Tomographic volumetric printing',2024,'2024 documented; 2025 unconfirmed',
 'https://bioinx.com/news/bio-inx-and-readily3d-announce-collaboration-advance-volumetric-bioprinting-cutting-edge-gel',
 'https://www.biopole.ch/company/readily3d-sa/','2024 joint announcement documents a commercial platform. City is current company listing; 2025 street address not independently established.'),
('TissueLabs','CH','Bellinzona','Bioprinter supplier','TissueStart; TissueRay','Extrusion; light-based',2021,'Pre-2025 product; live site',
 'https://www.tissuelabs.com/',
 'https://www.tissuelabs.com/company','Legacy map used Brazil. Current official site lists TissueLabs SA in Switzerland. Do not backdate the current Swiss location to 2025 without a dated address source.'),
('Poietis / Poietis Biosystems','FR','Pessac','Bioprinter supplier','NGB-R; NGB-C','Laser-assisted; multimodal',2025,'2025 documented',
 'https://www.poietis.com/sitemap/',
 'https://www.poietis.com/','Official event archive lists ISBF and TERMIS EU 2025. Current site announces NGB Biosystems name. Treat this as one brand lineage; legal restructuring is not independently reconciled.'),
('REGEMAT 3D','ES','Granada','Bioprinter supplier','BIO-series systems','Extrusion',2025,'2025 documented',
 'https://www.regemat3d.com/regemat-3d-announces-the-4th-edition-of-its-onsite-course-on-3d-bioprinting-cellculture/',
 'https://www.regemat3d.com/regemat-3d-announces-the-4th-edition-of-its-onsite-course-on-3d-bioprinting-cellculture/','21 March 2025 announcement identifies headquarters in Granada and bioprinting training. Not an instrument-sales count.'),
('Brinter equipment business','FI','Turku','Bioprinter supplier','Brinter ONE','Extrusion; multimaterial',2024,'2024 documented; 2025 unconfirmed',
 'https://www.utupub.fi/bitstream/handle/10024/185101/Adv%20Funct%20Materials%20-%202024%20-%20Wang%20-%20Bioprinting%20Macroporous%20Hydrogel%20with%20Aqueous%20Two%E2%80%90Phase%20Emulsion%E2%80%90Based%20Bioink%20In%20Vitro%20%282%29.pdf?isAllowed=y&sequence=1',
 'https://www.suomenbioteollisuus.fi/fi/biotech-companies-1/brinter-ltd','Finnish equipment business now uses brinteram.com. Brinter Inc therapeutic business lists a US HQ. Do not combine their current headquarters or assume an unchanged 2025 legal structure.'),
('Inventia Life Science','AU','Sydney','Bioprinter supplier','RASTRUM Allegro','Droplet-based',2025,'2025 documented',
 'https://inventialifescience.com/resources/press-release/inventia-life-science-launches-rastrum-allegro-to-revolutionize-high-throughput-3d-cell-culture-for-drug-discovery-and-disease-research',
 'https://inventialifescience.com/rastrum-user-group-meeting-sydney-2025','27 January 2025 launch; June 2025 meeting identifies Sydney headquarters.'),
('Cyfuse Biomedical','JP','Tokyo','Bioprinter supplier','Regenova; S-PIKE','Scaffold-free spheroid assembly',2025,'2025 documented',
 'https://en.cyfusebio.com/about/company/',
 'https://en.cyfusebio.com/about/company/','Official history documents printer sales since 2012/2019; company record includes December 2025 financial reference. Current office address may postdate the cutoff.'),
('CLECELL','KR','Seongnam','Bioprinter supplier','U-FAB ACTIVO; U-FAB MASTER','Dispensing; multimaterial',2022,'Pre-2025 product; live site',
 'https://clecell.wixsite.com/main/business-areas',
 'https://clecell.wixsite.com/main/business-areas','Official page dates launches to 2020 and 2022; Seongnam HQ and separate Seoul R&D site. Count one company.'),
('ROKIT Healthcare','KR','Seoul','Bioprinter supplier','Dr. INVIVO; APLICOR 3D','Extrusion; tissue processing',2025,'2025 documented',
 'https://exhibits.plasticsurgerythemeeting.com/pstm25/public/eBooth.aspx?BoothID=147169&FromPage=Exhibitors.aspx&IndexInList=163&ListByBooth=true&Nav=False&ParentBoothID=',
 'https://rokithealthcare.com/en/business','2025 exhibitor profile and vendor press release document activity. Regulatory efficacy claims were not evaluated or adopted.'),
('Avay Biosciences','IN','Bengaluru','Bioprinter supplier','MITO series','Extrusion',2025,'2025 documented',
 'https://frontiertech.niti.gov.in/story/building-indias-first-homegrown-bio-3d-printer-the-vision-of-avay-biosciences/',
 'https://www.avay.tech/','Government first-party company story mentions early-2025 activity and sales; no country market share inferred.'),
('Next Big Innovation Labs','IN','Bengaluru','Bioprinter supplier','Trivima','Extrusion',2023,'Pre-2025 product; live site',
 'https://nextbiginnovationlabs.com/about-us/',
 'https://nextbiginnovationlabs.com/trivima-pro-bioprinter/','Official history gives 2019 launch and 2023 installations. 2025 activity not independently documented.'),
('3D Biotechnology Solutions (3DBS)','BR','Campinas','Bioprinter supplier','Octopus; Genesis; Starter','Multimaterial deposition',2025,'2025 documented',
 'https://www.3dbiotechnologiessolutions.com/',
 'https://www.linkedin.com/company/3dbiotechnologysolutions','Official site lists printers and a March 2025 post. Company-authored location listing says Campinas; location retrieval is 2026.'),
('3D Bioprinting Solutions','RU','Moscow','Bioprinter supplier','FABION','Extrusion; spheroid placement',2021,'Pre-2025 product; live site',
 'https://www.bioprinting.ru/products-services/fabion/',
 MAP,'Official product verified. Moscow location derives from legacy map and remains unconfirmed for 2025. Do not confuse with Brazilian 3DBS.'),
('Advanced Solutions Life Sciences','US','Louisville','Bioprinter supplier','BioAssemblyBot','Robotic extrusion / assembly',2021,'Pre-2025 product; live site',
 'https://www.advancedsolutions.com/bioassemblybots',
 'https://www.advancedsolutions.com/about-us','Louisville headquarters and Manchester R&D operations are distinct sites. Pre-2025 presence supported by legacy map.'),
('nScrypt','US','Orlando','Bioprinter supplier','BAT / BioFabrication systems','Precision microdispensing',2021,'Historical bioprinter; 2025 unconfirmed',
 MAP,
 'https://www.nscrypt.com/','Current site verifies company and HQ. Historical bioprinter product from map is not proof of a current commercial BAT offering.'),
('Regenovo','CN','Hangzhou','Bioprinter supplier','Regenovo-WS','Extrusion',2018,'Historical product; 2025 unconfirmed',
 'https://stbrain.kjt.zj.gov.cn/webcontent/advsearch/serviceinfo.aspx?id=39be1020-e695-41cf-b931-76c5c9230d3c&search_channel=%E8%AE%BE%E5%A4%87',
 MAP,'Government equipment inventory verifies Chinese-made product in use since 2018. Vendor site timed out; HQ locality remains legacy-map evidence.'),
('Aspect Biosystems','CA','Vancouver','Tissue therapeutics','Bioprinted tissue therapeutics','Microfluidic bioprinting',2025,'2025 documented',
 'https://www.aspectbiosystems.com/news-resources',
 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/initiatives-plans-strategies/technology-industry/life-sciences-biomanufacturing/bc-jedi_lsbm-2024progreport_web.pdf','2025 company news documents therapeutic development. Legacy RX1 instrument offer is not treated as a verified current printer sale.'),
('Cellbricks','DE','Berlin','Tissue therapeutics','Light-based tissue fabrication','Light-based',2025,'2025 documented',
 'https://www.bihealth.org/en/notices/the-bih-center-for-regenerative-therapies-expands-its-tissue-engineering-capabilities',
 MAP,'January 2025 collaborator report verifies bioprinter installation. Open-market hardware sales not established; do not count as a confirmed seller.'),
('CollPlant','IL','Rehovot','Bioink supplier','Collink.3D','Collagen bioinks',2025,'2025 documented',
 'https://ir.collplant.com/news-events/press-releases/detail/187/collplants-rhcollagen-based-bioink-demonstrates-strong-performance-compared-to-matrigel-in-study-conducted-by-technion---israel-institute-of-technology',
 'https://www.sec.gov/Archives/edgar/data/1631487/000121390025100133/ea0261778-6k_collplant.htm','October 2025 release and filing identify product and Rehovot office. Bioink supplier, not a bioprinter manufacturer.'),
('BIO INX','BE','Ghent (Zwijnaarde)','Bioink supplier','READYGEL INX; high-resolution bioinks','Extrusion; photopolymerization materials',2024,'2024 documented; 2025 unconfirmed',
 'https://bioinx.com/news/bio-inx-and-readily3d-announce-collaboration-advance-volumetric-bioprinting-cutting-edge-gel',
 'https://bioinx.com/about-us','Commercial bioink portfolio confirmed. Do not count as hardware seller.'),
('Axolotl Biosciences','CA','Victoria','Bioink supplier','TissuePrint','Fibrin bioinks',2025,'2025 documented',
 'https://www.axolotlbiosciences.com/blog',
 'https://www.axolotlbiosciences.com/our-story','2025 company science posts and company history. Separate from Axolotl Biosystems in Türkiye.'),
('Systemic Bio','US','Houston','Tissue models / services','h-VIOS','Bioprinted vascularized tissue models',2025,'2025 documented',
 'https://www.3dsystems.com/press-releases/systemic-bio-named-top-10-finalist-slas-2025-innovation-award',
 'https://www.3dsystems.com/press-releases/systemic-bio-named-top-10-finalist-slas-2025-innovation-award','3D Systems subsidiary. Count operating company once; do not add parent as another tissue-model company.'),
('FluidForm Bio','US','Waltham','Tissue therapeutics','FRESH','Embedded extrusion',2025,'2025 documented',
 'https://www.fluidformbio.com/news-events/fluidform-bio-announced-issued-patent',
 'https://www.fluidformbio.com/','April 2025 company release documents platform and location. Not classified as an open-market hardware supplier.'),
('VivoSim / Organovo lineage','US','San Diego','Tissue models / services','Bioprinted human tissue models','Extrusion',2025,'2025 documented',
 'https://ir.organovo.com/static-files/36ec35c9-2654-4741-9815-66471e4a2186',
 'https://ir.organovo.com/static-files/36ec35c9-2654-4741-9815-66471e4a2186','April 2025 announcement changes Organovo Holdings name to VivoSim Labs. One lineage here; subsidiary and parent are not independent counts.'),
('VoxCell BioInnovation','CA','Victoria','Tissue models / services','Vascularized tissue models','High-resolution bioprinting',2025,'2025 documented',
 'https://www.britishcolumbia.ca/news-stories/engineering-the-future-of-medicine/',
 'https://voxcell.com/contact','August 2025 government economic-development profile identifies company and Victoria. Instrument commercialization not established here.'),
('Carcinotech','GB','Edinburgh / Roslin','Tissue models / services','Carcino3D','Tumour bioprinting',2024,'2024 documented; 2025 unconfirmed',
 'https://edinburgh-innovations.ed.ac.uk/news/carcinotech-raises-4.2m',
 'https://www.carcinotech.com/company-overview-2/','Patient-derived tumour models; no hardware-selling claim. 2025 leadership update appears on university follow-up.'),
('mimiX Biotherapeutics','CH','Biel/Bienne','Tissue therapeutics','SIM; FastSkin','Acoustic bioassembly',2025,'2025 documented',
 'https://www.swissbiotech.org/wp-content/uploads/2025/05/Swiss-Biotech-Directory-2025.pdf',
 'https://www.mimixbio.com/','Acoustic bioassembly is included as adjacent biofabrication, explicitly distinct from extrusion or light-based printing.'),
('PhosPrint','GR','Athens (Agia Paraskevi)','Platform developer','PhosDB I','Laser-induced forward transfer',2021,'Pre-2025 platform; sales unconfirmed',
 'https://www.phosprint.eu/',
 'https://www.phosprint.eu/','Company site reports first external GEN1 installation in March 2026. Do not backdate that installation or count a confirmed 2025 hardware sale.'),
('Precise Bio','US','Winston-Salem','Tissue therapeutics','Biofabricated corneal tissues','Proprietary bioprinting',2025,'2025 documented',
 'https://www.precise-bio.com/',
 'https://www.precise-bio.com/','2025 news listed on official site; US office listed. Israel R&D affiliation does not make this a second company.'),
('CTIBIOTECH','FR','Lyon area','Tissue models / services','Human tissue models','3D tissue printing',2021,'Pre-2025 company; live site',
 'https://ctibiotech.com/',
 'https://ctibiotech.com/','Official page lists Lyon and Philadelphia. One company in sample, localized to French base. 2025 site distribution not independently established.'),
('Prellis Biologics','US','Berkeley / San Francisco Bay Area','Tissue models / services','EXIS; lymph-node organoids','Two-photon laser bioprinting',2021,'Pre-2025 company; live site',
 'https://prellisbio.com/',
 MAP,'Bioprinted organoid application verified. Locality remains approximate legacy Bay Area attribution; not a precise office coordinate.'),
('Allevi','US','Philadelphia','Historical bioprinter brand','Allevi 1; Allevi 2; Allevi 3','Extrusion',2023,'Production ended 2023-07-27',
 'https://www.allevi3d.com/allevi-announcement-discontinued-products/',
 MAP,'Exclude from active-supplier counts. 2026-updated official notice explicitly gives historical 2023 end of production; support continued to 2026.'),
('Allegro 3D','US','San Diego','Acquired bioprinter brand','STEMAKER / DLP portfolio','DLP',2022,'Acquired; count under CELLINK',
 'https://bico.com/bico-acquires-allegro-3d/',
 'https://bico.com/bico-acquires-allegro-3d/','Exclude from independent company counts in this register to avoid duplicating CELLINK portfolio.'),
]

def build():
    rows = []
    for row in ROWS:
        name, code, city, role, product, tech, year, status, source, loc, note = row
        rows.append(dict(company_id=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-'),
            company_name=name,country_code=code,city_or_site=city,role=role,product_or_platform=product,
            technology=tech,evidence_year=year,status_at_2025_cutoff=status,
            documented_2025_activity=status=='2025 documented',
            supplier_sample_included=role=='Bioprinter supplier' and not status.startswith('Historical'),
            independent_sample_included=role not in ['Historical bioprinter brand','Acquired bioprinter brand'],
            activity_source_url=source,location_source_url=loc,
            location_time_basis='Source-specific; current sites retrieved 2026-10-27 unless dated in notes',
            retrieved_date=DATE,notes=note))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'company_research.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    with (OUT/'companies.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    print('Curated company records:', len(rows))

def import_legacy(path):
    ns={'k':'http://www.opengis.net/kml/2.2'}
    records=[]
    for folder in ET.parse(path).findall('.//k:Folder',ns):
        if folder.findtext('k:name',namespaces=ns)!='Companies':continue
        for p in folder.findall('k:Placemark',ns):
            name=p.findtext('k:name',namespaces=ns).strip()
            desc=p.findtext('k:description',default='',namespaces=ns)
            fields=dict(line.split(': ',1) for line in re.split(r'<br\s*/?>',desc) if ': ' in line)
            records.append({'name':name,'legacy_country':fields.get('Country',''),
                'legacy_website':fields.get('Website',''),'legacy_business':fields.get('Business',''),
                'legacy_technology':fields.get('Technique',''),'legacy_product':fields.get('Model',''),
                'source_update_year':2021,'source_url':MAP,
                'status':'Historical seed; not evidence of 2025 operation or location'})
    out=OUT/'raw/legacy-map-companies.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({'source_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        'source_url':MAP,'source_update_year':2021,'records':records},ensure_ascii=False,indent=2)+'\n')
    print('Historical map seeds:',len(records))

if __name__=='__main__':
    if len(sys.argv)>1:import_legacy(sys.argv[1])
    build()
