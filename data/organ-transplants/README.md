# Organ donation and transplantation

Updated3November2026. `annual_counts.json` drives the animated slide and is embedded for offline use.

## 2025 verified source

[EDQM–ONT Newsletter Transplant2026, international figures2025](https://www.transplant-observatory.org/wp-content/uploads/2026/10/NEWSLETTER-2026_alta.pdf), linked from WHO–ONT GODT homepage. Original unchanged PDF is archived in sources/.

PDFp37 / printedp35 lists kidney116775, liver45556, heart10748, lung8472, pancreas2148, smallbowel180. Their sum is **183879 organ transplant procedures**. It also reports **49169 actual deceased donors**. The full report's liver45556 supersedes the homepage45554; the earlier “>183800” remains valid but is no longer the best available precision. No2026forecast is used.

## 2025 waiting-list sums

From PDFpp66–74 / printedpp64–72 (94country columns):

|Organ|Waiting at31December2025|Deaths on waiting lists during2025|
|---|---:|---:|
|Kidney|446153|30825|
|Liver|58198|6427|
|Heart|16147|1585|
|Lung|6487|812|
|Pancreas|5613|340|
|Small bowel|307|30|
|Sum|532905|40019|

These are **reported organ-list entries**, not deduplicated people. A multi-organ candidate may appear in more than one category. Report blanks remain missing, not zero; no imputation or complete-world-census claim. Cells including the large Republic of Korea kidney waiting-list death figure17392 were checked against the rendered source; these totals reproduce published entries and are not a clinical validation of national submissions.

`waiting_lists_2025_cells.csv` preserves each table cell by PDFpage/countrycolumn/organ/metric with nulls as blanks. `waiting_lists_2025_summary.json` records sums and sourceSHA256. `tools/extract_2025_waiting_lists.py` normalizes sideways pages for text extraction and groups digit glyphs by source rows and country columns, preserving spaced thousands.

## Earlier snapshots

2015–2024 use archived source URLs in report_sources.json; country coverage and data vintages vary. Older method notes are in historical-method-notes.md. The legacy kidney_waiting_list2024 object remains for provenance but is no longer displayed. Transplants count organ procedures rather than unique recipients and include living donation. Deceased donors exclude living donors and registered potential donors.

## Rebuild

Run `python3 tools/update_organ_slide.py` for a targeted update; its section-level guard protects other slides. Use `python3 tools/check_organ_data.py` for data/HTML validation.
