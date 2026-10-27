import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL, fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const runtimeDir=process.env.BIOPRINT_RUNTIME_DIR;
if(!runtimeDir) throw new Error('Set BIOPRINT_RUNTIME_DIR to a writable directory with a node_modules symlink to the bundled workspace dependencies.');
const dependencyRequire=createRequire(path.join(runtimeDir,'entry.mjs'));
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(dependencyRequire.resolve('@oai/artifact-tool')));
const base=path.join(root,'data/geography-2025');
const outputDir=process.env.BIOPRINT_OUTPUT_DIR || runtimeDir;
const data=JSON.parse(await fs.readFile(path.join(base,'workbook_data.json'),'utf8'));
const wb=Workbook.create();
await fs.mkdir(outputDir,{recursive:true});
const previews=[];

function col(i){let s='';for(i++;i;i=Math.floor((i-1)/26))s=String.fromCharCode(65+(i-1)%26)+s;return s;}
function sheet(name,columns,rows,{title='',context='',widths=[],heights=30,previewCols=7}={}){
 const sh=wb.worksheets.add(name);sh.showGridLines=false;
 const header=title?5:1, end=header+rows.length,last=col(columns.length-1);
 const matrix=[columns.map(c=>c[0]),...rows.map(r=>columns.map(c=>{
  const value=r[c[1]]??null;
  return c[1].endsWith('_date') && typeof value==='string' && /^\d{4}-\d{2}-\d{2}$/.test(value)?new Date(value+'T00:00:00Z'):value;
 }))];
 const region=sh.getRange(`A${header}:${last}${end}`);region.values=matrix;
 region.format.font={name:'Arial',size:10,color:'#242435'};
 region.format.rowHeight=heights;region.format.verticalAlignment='center';
 for(let i=0;i<columns.length;i++){
  const rng=sh.getRange(`${col(i)}${header}:${col(i)}${end}`);
  rng.format.columnWidth=widths[i] || 22;
  const field=columns[i][1];
  if(field.endsWith('_date'))sh.getRange(`${col(i)}${header+1}:${col(i)}${end}`).setNumberFormat('yyyy-mm-dd');
  if(rows.some(r=>typeof r[field]==='number')){
   sh.getRange(`${col(i)}${header+1}:${col(i)}${end}`).setNumberFormat(field==='year'?'0':field==='latitude'||field==='longitude'?'0.0000':'#,##0');
   sh.getRange(`${col(i)}${header+1}:${col(i)}${end}`).format.horizontalAlignment='right';
  }
 }
 const hdr=sh.getRange(`A${header}:${last}${header}`);
 hdr.format.fill='#39304F';hdr.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};
 hdr.format.wrapText=true;hdr.format.rowHeight=42;hdr.format.horizontalAlignment='center';
 const table=sh.tables.add(`A${header}:${last}${end}`,true,name.replace(/[^a-zA-Z]/g,'')+'Table');
 table.style='TableStyleLight1';
 for(let r=header+1;r<=end;r++)if((r-header)%2===1)sh.getRange(`A${r}:${last}${r}`).format.fill='#F3F0F7';
 sh.freezePanes.freezeRows(header);sh.freezePanes.freezeColumns(name==='Companies'?1:2);
 if(title){
  sh.getRange('A2').values=[[title]];sh.getRange('A2').format.font={name:'Arial',size:14,bold:true,color:'#292238'};
  sh.getRange('A3').values=[[context]];sh.getRange('A3').format.font={name:'Arial',size:10,italic:true,color:'#5B526A'};
  sh.getRange(`A4:${last}4`).format.borders={bottom:{style:'thin',color:'#B49AD8'}};
 }
 previews.push({name,range:`A1:${col(Math.min(previewCols,columns.length)-1)}${Math.min(end,title?15:10)}`});
 return sh;
}

const countries=sheet('Countries',[
 ['Rank 2021–25','rank_2021_2025'],['Country / region','country'],['ISO2','country_code'],
 ['Works 2021–25','works_2021_2025'],['Works 2000–25','works_2000_2025'],['Works 2025','works_2025'],
 ['Affiliation IDs 2021–25','distinct_affiliation_ids_2021_2025'],['Author IDs 2021–25','distinct_author_ids_2021_2025']
],data.countries,{title:'Bioprinting research geography',context:'Publication window: 2000–2025. Ranked by 2021–2025 output. OpenAlex retrieved 27 October 2026.',widths:[12,25,8,16,16,14,20,20],previewCols:8});
countries.tabColor='#39304F';

const co=sheet('Companies',[
 ['Company','company_name'],['Country code','country_code'],['City / site','city_or_site'],['Business role','role'],
 ['Product / platform','product_or_platform'],['Status at 2025 cutoff','status_at_2025_cutoff'],
 ['2025 activity documented','documented_2025_activity'],['Activity source URL','activity_source_url'],
 ['Location source URL','location_source_url'],['Location time basis','location_time_basis'],['Qualifications','notes']
],data.companies,{widths:[34,12,30,27,36,36,15,65,65,65,90],heights:62});
co.getRange(`A2:K${data.companies.length+1}`).format.wrapText=true;
co.getRange(`A2:K${data.companies.length+1}`).format.autofitRows();
co.getRange(`F2:F${data.companies.length+1}`).conditionalFormats.add('containsText',{text:'unconfirmed',format:{fill:'#FFF0CC',font:{color:'#835008'}}});
co.getRange(`F2:F${data.companies.length+1}`).conditionalFormats.add('containsText',{text:'Pre-2025',format:{fill:'#FFF0CC',font:{color:'#835008'}}});
co.getRange(`F2:F${data.companies.length+1}`).conditionalFormats.add('containsText',{text:'ended',format:{fill:'#FCE0E0',font:{color:'#8C2424'}}});

sheet('Company countries',[
 ['Country / region','country'],['ISO2','country_code'],['Researched records','researched_records'],
 ['Independent company sample','independent_company_sample'],['Bioprinter supplier sample','supplier_sample'],
 ['Companies with 2025 evidence','companies_with_2025_activity_evidence'],['Suppliers with 2025 evidence','suppliers_with_2025_activity_evidence']
],data.company_countries,{title:'Company geography: researched sample',context:'Counts describe this register. Unlisted companies are not global zeros. See Companies for source dates and status.',widths:[26,9,18,23,23,23,23]});

sheet('Affiliations',[
 ['Rank 2021–25','rank_2021_2025'],['Institution','name'],['Country','country'],['City','city'],
 ['Works 2021–25','works_2021_2025'],['Works 2000–25','works_2000_2025'],['Works 2025','works_2025'],
 ['Latitude','latitude'],['Longitude','longitude'],['OpenAlex ID','id'],['ROR','ror'],['Homepage','homepage_url'],['Coordinate date basis','geo_time_basis']
],data.affiliations,{widths:[12,74,23,26,18,18,16,14,14,52,42,65,90],heights:28});

const au=sheet('Authors',[
 ['Rank 2021–25','rank_2021_2025'],['Author','name'],['Last observed countries','last_observed_country_codes'],
 ['Works 2021–25','works_2021_2025'],['Works 2000–25','works_2000_2025'],
 ['Latest affiliation date','last_observed_affiliation_date'],['Last observed affiliations','last_observed_affiliations'],
 ['Latest publication date','last_observed_publication_date'],['OpenAlex author ID','id'],['ORCID','orcid'],
 ['Affiliation evidence works','location_source_work_ids'],['Location meaning','location_basis']
],data.authors,{widths:[12,32,23,18,18,24,85,24,52,48,90,100],heights:33});
au.getRange('G2:G201').format.wrapText=true;

sheet('Annual corpus',[
 ['Publication year','year'],['Included works','works']
],data.annual_counts,{widths:[24,24],previewCols:2});

const v=data.verification;
const notes=[
 ['Purpose','Geographic research and company data for a future bioprinting competition map. No slides were changed.'],
 ['Cutoff','Publications from 1 January 2000 through 31 December 2025. Retrieval: 27 October 2026. This is a retrospective 2026 database snapshot.'],
 ['Main rank','Country and entity tables rank 2021–2025 publication output. Cumulative 2000–2025 and 2025-only counts are separate columns. Ties share a rank.'],
 ['Search scope','OpenAlex exact title-and-abstract query: bioprint* OR "bio printing" OR "bio printed" OR "bio printer" OR "bio printers". Articles and reviews; retractions excluded.'],
 ['Coverage',`${v.included_works.toLocaleString('en')} included works; ${v.included_works_2021_2025.toLocaleString('en')} in 2021–2025; ${v.distinct_country_region_codes} country/region codes; ${v.distinct_affiliation_ids.toLocaleString('en')} institution IDs; ${v.distinct_author_ids.toLocaleString('en')} author IDs.`],
 ['Country counting','Full count: each work counted once per distinct institution country on its byline. International collaborations appear in several countries. Country totals cannot be summed to a global paper total.'],
 ['Fractional counts','CSV additionally includes fractional country counts: 1 divided by the number of known countries on each work. Missing-country works are not reassigned.'],
 ['Author / affiliation counts','Counts are resolved OpenAlex IDs, not verified numbers of people or independent laboratories. Parent institutions and child institutes are not manually merged.'],
 ['Missing country',`${v.works_without_institution_country.toLocaleString('en')} works lack an institution country, including ${v.works_without_institution_country_2021_2025} in 2021–2025. Keep these missing; they are not a country with zero output.`],
 ['Author locations','Own institutions on latest dated corpus works with institution metadata, at or before 2025. Affiliation observation date is separate from latest publication date. Not present-day employment, residence or nationality.'],
 ['Institution coordinates','Coordinates come from current OpenAlex/ROR-derived institution records, retrieved in 2026. They locate the institution and may not represent the historical campus or laboratory.'],
 ['Workbook detail','All country/company records are included. Authors and Affiliations show the first 200 rows by recent output. Full author and affiliation tables and author-location links are in the CSV files.'],
 ['Company scope',`${v.company_records} researched records across ${v.company_countries} countries. This is a curated register, not a global census or a market-share ranking. ${v.company_records_2025_activity_documented} have explicit 2025 activity evidence; others expose older or undated evidence.`],
 ['Supplier sample','A marketed pre-2025 product plus a live source is a supplier candidate, not proof of annual 2025 sales. Explicit 2025 evidence is separately flagged. Historical/unconfirmed product-only entries are excluded from the supplier sample.'],
 ['Corporate counting','Allevi printer production ended in 2023. Allegro is grouped under CELLINK for independent sample counts. VivoSim/Organovo is one lineage. Corporate parents and overseas offices are not added as extra companies.'],
 ['Location dates','Company cities are source-specific. A site checked in 2026 does not prove the same office existed in 2025. TissueLabs and Brinter have explicit location/structure qualifications.'],
 ['Legacy map','The 70 old-map company entries are preserved separately as a 2021 seed list. They are not added to current company counts and were not blindly accepted.'],
 ['Date cleaning',`${v.excluded_before_2000} retrieved records outside 2000–2025 were excluded and logged, including visibly suspect historical dates. No dates were silently corrected.`],
 ['Deduplication',`${v.duplicate_rows_removed} duplicate page row removed by OpenAlex work ID. All 26 annual totals match a separately downloaded API year aggregation. No truncated authorship lists were found.`],
 ['Database drift','Initial live country aggregation returned 11,103 works; year control and deduplicated export returned 11,101 before date screening. All delivered rankings are calculated from the archived export, not mixed live totals.'],
 ['Limitations','Keyword-defined bibliographic activity is not a manually reviewed census of living-cell printing experiments. It may include peripheral studies and miss papers using other terminology. Author disambiguation and institution matching can contain errors.'],
 ['Research refresh','Run tools/fetch_geography.py, then --institutions to retrieve. Refresh in a new directory/version to preserve this snapshot. Rebuild locally with tools/build_company_register.py and tools/build_geography.py.'],
 ['OpenAlex data','https://help.openalex.org/api/searching/ ; https://help.openalex.org/api/grouping/ ; https://help.openalex.org/data/authorships/ . OpenAlex metadata is CC0. Third-party company material retains its rights.']
];
const methods=sheet('Methods', [['Field','field'],['Definition / limitation','definition']],notes.map(([field,definition])=>({field,definition})),{widths:[29,130],heights:48,previewCols:2});
methods.getRange(`A2:B${notes.length+1}`).format.wrapText=true;
methods.tabColor='#B8ADCB';

wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Countries!A5:H10',include:'values,formulas',tableMaxRows:6,tableMaxCols:8,maxChars:2200})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:20},summary:'Final error scan',maxChars:1200})).ndjson);
for(const p of previews){
 const preview=await wb.render({sheetName:p.name,range:p.range,scale:1.25,format:'png'});
 await fs.writeFile(path.join(outputDir,p.name.replaceAll(' ','-')+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
const output=await SpreadsheetFile.exportXlsx(wb);
await output.save(path.join(outputDir,'Bioprinting-Geography-through-2025.xlsx'));
await fs.copyFile(path.join(outputDir,'Bioprinting-Geography-through-2025.xlsx'),path.join(base,'Bioprinting-Geography-through-2025.xlsx'));
console.log('Exported workbook with',previews.length,'sheets');
