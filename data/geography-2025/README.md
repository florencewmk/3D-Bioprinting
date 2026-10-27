# Bioprinting geography through 2025

[Download the Excel workbook](Bioprinting-Geography-through-2025.xlsx) · [Top 20, 2000–2025](top20_countries_2000_2025.csv) · [Top 20, 2021–2025](top20_countries.csv) · [Company register](companies.csv)

This dataset supports a future interactive map for the SOFE bioprinting presentation.
The research window is **2000–2025**, with a separate **2021–2025 ranking** to show
recent activity. Sources were retrieved on **27 October 2026**. This is a retrospective
database snapshot, not data captured on 31 December 2025.

## Results and coverage

The archived research corpus contains **11,071 distinct works**, including **7,503 in
2021–2025** and **2,186 in 2025**. It identifies **112 country/region codes**, **5,343
institution IDs** and **35,300 author IDs**. These are database identifiers, not a
manually verified census of independent laboratories or individual researchers.

The company research contains **40 records across 21 countries**, including suppliers,
bioink businesses, tissue developers and historical brands. **19 records have explicit
2025 activity evidence.** Other records expose older, undated or incomplete evidence
rather than assuming 2025 operation. Company counts describe this researched sample,
not all companies worldwide, sales, installed printers or market share.

### Top 20 countries by recent research output

Each work counts once per distinct institution country. International papers can count
in multiple countries. Ties share a rank. The cumulative ranking differs from the
recent ranking: for example, the United States leads the cumulative 2000–2025 view.

| Recent rank | Country | Works 2021–2025 | Works 2000–2025 |
| ---: | --- | ---: | ---: |
| 1 | China | 1,580 | 2,106 |
| 2 | United States | 1,425 | 2,555 |
| 3 | India | 728 | 838 |
| 4 | South Korea | 454 | 655 |
| 5 | Germany | 406 | 637 |
| 6 | Italy | 348 | 456 |
| 7 | United Kingdom | 347 | 552 |
| 8 | Canada | 261 | 379 |
| 9 | Australia | 249 | 358 |
| 10 | Iran | 222 | 281 |
| 11 | Spain | 210 | 286 |
| 12 | Türkiye | 194 | 253 |
| 13 | Netherlands | 178 | 294 |
| 14 | Brazil | 167 | 213 |
| 15 | France | 141 | 230 |
| 15 | Poland | 141 | 169 |
| 17 | Russia | 139 | 205 |
| 18 | Portugal | 123 | 168 |
| 19 | Singapore | 122 | 235 |
| 20 | Switzerland | 113 | 183 |

The complete country table also includes author and affiliation counts, 2025-only
output, fractional publication credit and company-sample fields. Research and company
measures are **not added into a composite score**.

## Files

| File | Contents |
| --- | --- |
| `Bioprinting-Geography-through-2025.xlsx` | Seven filterable sheets: Countries, Companies, Company countries, Affiliations, Authors, Annual corpus and Methods. All country/company rows and the first 200 affiliation/author rows by recent output. |
| `top20_countries.csv` | First 20 country rows in recent-output order. |
| `top20_countries_2000_2025.csv` | First 20 country rows in cumulative 2000–2025 publication order. |
| `countries.csv` | All country/region rows, research counts and clearly labelled company-sample counts. |
| `companies.csv` / `company_research.json` | The 40 researched company records, country/city, role, products, status, evidence period, source URLs and qualifications. |
| `company_countries.csv` | Counts within the researched company sample, with explicit 2025-evidence columns. |
| `affiliations.csv` | All 5,343 affiliation IDs, counts, country/city, institution coordinates, ROR and source links. |
| `authors.csv` | All 35,300 author IDs, counts, ORCID where available, and last observed institutional affiliations through 2025. |
| `author_locations.csv` | One row per author–last-observed-institution link, with institution coordinates and evidence work IDs. An author can have several rows. |
| `works.csv` | Included work IDs, DOI, title, date, type and author/institution/country links used to calculate the tables. |
| `annual_corpus_counts.csv` | Year totals for the exact delivered corpus. This is an OpenAlex series, separate from the presentation's earlier WoS analysis. |
| `excluded_records.csv` | Thirty retrieved records outside the defined 2000–2025 window, including suspect historical metadata dates. No dates silently corrected. |
| `raw/` | Compressed public OpenAlex responses, independent aggregate controls, and the old map's 70-company historical seed list. |
| `requests.jsonl` | Exact successful API request URLs, retrieval date and saved response paths. Initial country query is also preserved in its response's `meta.x_query`. |
| `company-search-notes.md` | Company search approach, exact example queries used, source interpretation and remaining verification. |
| `verification.json` | Corpus size, missing geography, deduplication, annual reconciliation, entity counts and other checks. |
| `checksums.sha256` | Integrity hashes for the snapshot files, excluding this checksum file itself. |

`workbook_data.json` is the reproducible input for the Excel builder, not a second
independent source of counts.

## Research method

The main source is [OpenAlex](https://help.openalex.org/api/), using exact
**title-and-abstract text search**, rather than a broad full-text mention search:

```text
bioprint* OR "bio printing" OR "bio printed" OR "bio printer" OR "bio printers"
```

API parameter: `search.title_and_abstract.exact`. Filters: `type:article|review`,
`is_retracted:false`, and publication date through `2025-12-31`. Retrieval uses disjoint
pre-2021 and 2021–2025 windows with ordinary public page pagination. A local date screen
retains publication years **2000–2025**. No language restriction was imposed. Records
are deduplicated by OpenAlex work ID; DOI/title duplicates across separate OpenAlex IDs
were not manually adjudicated.

OpenAlex's `article` class can include conference-related records. This analysis does
not assert that every record is a peer-reviewed journal experiment. The wildcard also
retrieves inflections such as bioprinted, bioprinter and bioprinting. It can include
peripheral studies and miss relevant works using other language or terminology.
The corpus has not undergone full manual relevance screening.

### Counting and localization

- **Countries:** union of matched institution country codes on each work. Count a
  work once per country. CSV also preserves fractional credit `1 / known countries`.
  Fractional counts sum to the number of works with a known institution country,
  not the full corpus.
- **Affiliations:** distinct OpenAlex institution IDs on each work, including records
  with a matched institution but no resolved author ID. Systems, parent universities,
  hospitals and child institutes remain distinct. Do not interpret their sum as the
  number of independent labs.
- **Authors:** distinct resolved author IDs on each work. A name is not used as a
  unique key. ORCID is preserved when present. Disambiguation can split or merge people.
- **Author geography:** use the author's own institutions on their latest dated
  corpus work(s) **with matched institutions**, up to 2025. The last affiliation
  observation date and latest publication date are separate fields. If several works
  share the latest affiliation date, retain the union of that author's institutions.
  Do not substitute all coauthors' affiliations, current OpenAlex author-profile
  affiliations, nationality, residence or a current employment claim.
- **Coordinates:** current OpenAlex institution geography, retrieved in 2026. They
  locate an institution, not a person, and do not establish a specific historical
  laboratory/campus. Company city/site fields have source-specific dates and have not
  been assigned precise office coordinates.
- **Names and territories:** preserve source country/region codes, including separate
  Hong Kong and Taiwan codes; use the display name Türkiye for `TR`. These are source
  geography categories, not an independent political classification.

### Missing data and checks

**1,453 works lack an institution country**, including **791 in 2021–2025**. These
works remain in the corpus totals and are not assigned to countries. **3,779 author
IDs lack any matched last-observed institution.** One institution ID,
`I4210133110`, was unavailable from the current institution endpoint; its work-level
stub is preserved, with absent coordinates left blank. Missing values are not zeros.

The archive contained one repeated page row, removed by work ID. Every annual total
for 2000–2025 reconciles to the separately downloaded year aggregation. Fractional
country credit reconciles to works with known countries. No truncated authorship
lists were found in the exported work responses.

The first live country aggregation reported 11,103 records; the independent year
aggregation and deduplicated export reported 11,101 before the 30-record date screen.
This reflects a changing API and/or live query state. **All delivered rankings are
computed from the archived export**, not assembled from inconsistent live aggregates.
Re-running later may change the results through indexing, date correction,
disambiguation and retraction updates. A 2025 cutoff does not freeze metadata as it
existed in 2025.

API references: [search syntax](https://help.openalex.org/api/searching/),
[grouping/counts](https://help.openalex.org/api/grouping/),
[authorship and affiliation resolution](https://help.openalex.org/data/authorships/).

## Company method and limitations

Companies were sought worldwide, including beyond the research top 20. Official
product pages, company announcements, filings, institutional partners and government
company profiles were preferred. Every curated row carries activity and location
sources. A company need not sell a printer: its role explicitly separates hardware,
bioinks, tissue therapeutics, tissue-model services and platform development.

`documented_2025_activity` means an explicit 2025 source or 2025 company record was
found. It does **not** mean an audited 2025 instrument sale, year-end solvency or
clinical approval. `supplier_sample_included` identifies a researched supplier
candidate with a pre-2025 product and live source; it does not silently turn older
evidence into a verified 2025 operating status. `independent_sample_included` excludes
the two explicitly grouped/historical brand rows. Neither field establishes a complete
population or common ultimate-parent corporate ownership census.

Specific corrections include:

- **Allevi:** official notice dates printer-production cessation to 27 July 2023.
  Excluded from active-supplier sample counts; do not interpret this as closure of
  all 3D Systems businesses.
- **Allegro 3D:** acquired brand grouped under CELLINK in the independent sample.
- **VivoSim/Organovo:** the April 2025 name-change announcement is tracked as one
  lineage rather than two unrelated companies.
- **Axolotl Biosystems:** Turkish equipment company, distinct from Canada's Axolotl
  Biosciences. The old map associated its URL with a Swiss company.
- **TissueLabs:** current official Swiss address differs from the old Brazilian map
  label. Do not backdate that address without a dated source.
- **Brinter:** distinguish the Finnish equipment business from the US therapeutic
  business. Current legal structure and 2025 headquarters were not fully reconciled.
- **PhosPrint:** first external GEN1 installation is described as March 2026 on the
  current site, and is not backdated into a 2025 seller claim.

The original [Bioprinting World Map](https://www.google.com/maps/d/u/0/viewer?mid=1AO84VH2CJ_TBndoVirj7yFfcitTXe0K3)
states its content was last updated in 2021. Its 70-company list is an audit seed,
not a verified current census. This register does not claim that all remaining old-map
entries are still operating or relevant. Unrepresented companies/countries are
**not evidence of no commercial activity**.

## Reproduce the saved snapshot

From the repository root, without network access:

```sh
python3 tools/build_company_register.py
python3 tools/build_geography.py
python3 tools/check_geography.py
```

Rebuild the workbook using the bundled workspace Node.js and `@oai/artifact-tool`.
Set `BIOPRINT_RUNTIME_DIR` to a writable build directory with a `node_modules` symlink
to the workspace dependency packages, then run `tools/build_geography_workbook.mjs`.
The builder exports the workbook to that directory and copies it into this data folder.
The package is an external build dependency, not bundled into this repository.

For a new retrieval, preserve this snapshot and use a new version/directory. The
fetcher reuses existing response files and does not silently refresh them. A fresh
network retrieval may require a free OpenAlex key or be limited by its public budget;
no credentials are included here. This work did not change the presentation or splice
these OpenAlex counts into its existing Web of Science charts.

## Rights

OpenAlex metadata is [CC0](https://help.openalex.org/api/). This repository's analysis
and concise company research notes are provided with its existing license. Third-party
company pages, brochures, institutional publications and logos retain their respective
rights. Source URLs and factual summaries do not relicense those works.
