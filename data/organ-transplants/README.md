# Organ donation and transplantation

Retrieved/checked 17 October 2026. `annual_counts.json` is the source for presentation slide 8 and is embedded into the HTML for offline use.

- 2015–2024: WHO–ONT GODT annual report snapshots; source URL accompanies every row. Original report links also in `report_sources.json`.
- 2025: [GODT homepage highlights](https://data.transplant-observatory.org/): **more than 183,800 solid organ transplant procedures**, 49,169 actual deceased donors, 54,600 living-donor transplant procedures, 96 reporting countries. This is a homepage snapshot, not a verified full annual report. The page also has zero-valued counters and inconsistent year fields.
- 2025 transplant exact count is deliberately `null`; `transplants_lower_bound_exclusive: 183800` encodes the published bound. Do not replace this with an exact 183,800. Slide uses dashed continuation and an open marker at the bound; visible label is “>183,800”.
- Waiting-list callouts remain **kidney-only, 2024**: 377,902 waiting at year-end and 19,936 deaths during the year (2024 PDF p65). No 2025 waiting-list values have been verified.

Counts are not interchangeable: one deceased donor can provide multiple organs; transplant totals include living donation and count procedures rather than unique people. Country coverage changes; these snapshots are not a fixed-country trend. Deaths among people never waitlisted are missing.

2016 procedure total is summed from six organ categories (PDF p2). Updated February 2025 version of the 2023 report is used (172,409). Historical figures may be revised in later reports. The original full methodological notes are retained in `historical-method-notes.md`.

## Rebuild

Run `python3 tools/update_organ_slide.py` from the repo root after editing data/CSS/controller. This changes slide 8 only and asserts the other 49 sections are byte-identical. `tools/build_deck.py` also includes the chart for full source builds.
