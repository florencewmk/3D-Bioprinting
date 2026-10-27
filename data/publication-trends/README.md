# Publication trends used by presentation slide 7

The 96 historical values (24 years × 4 techniques) match both native charts in slide 8 of `SoFe Competition.pptx`, including the 2019–2023 inset. Comparison was performed directly against the PowerPoint chart series; no image digitization or estimated values are used.

## Files

- `annual_counts_2000_2023.csv`: unchanged original annual data, retrieved 14 October 2026.
- `annual_counts_2000_2026.csv`: presentation-ready table, with empty numeric cells for unverified 2024–2026.
- `annual_counts.json`: authoritative machine-readable presentation data; unverified counts are `null`.
- `wos_queries_2000_2023.json`: exact executed historical queries.
- `wos_queries_2024_2026.json`: same query definitions with the requested new year range. These are prepared queries, not executed results.
- `original-method.md`: original detailed counting method and coverage limitations.

## Historical snapshot

Source: Web of Science Core Collection, available institutional editions, English Article or Review. Query intersection uses the broad topic search from the Santoni et al. supplement and the technique keyword groups documented in the query JSON. This is a new keyword analysis inspired by Fig. 3b, not a reproduction of the original paper's classifier.

| Technique | Sum, 2000–2023 |
| --- | ---: |
| Laser-assisted | 152 |
| Inkjet | 309 |
| Stereolithography | 769 |
| Extrusion | 1,385 |

These sums are category matches. A publication may match more than one technique; the stacked total is not a unique-paper count. Stereolithography includes DLP, vat photopolymerization and two-photon polymerization/lithography terms.

The institutional collection used previously was explicitly frozen and no longer updated. Its recent years may be incomplete. Displaying 2023 does not establish complete 2023 calendar-year coverage.

## Requested 2024–2026 extension

Status on 17 October 2026: **not yet verified**. A fresh TU Berlin institution login is required before updated Web of Science access can be checked. Do not treat missing counts as zero, extrapolate them, or silently append numbers from another database.

Preferred update: rerun all four historical queries with `PY=(2000-2026)` in an updated Core Collection, retain the same language/document filters, and export the Publication Years facet for every year. Preserve this original snapshot separately. A minimum comparability check would rerun 2019–2023 alongside the new years and document changed coverage. A full rerun is preferable because the frozen snapshot may undercount recent years.

Keep the year convention explicit. In WoS, the default year facet may use the early-access year where it differs from final publication year. The animation uses the saved original facet rather than reassigning records to final year. [Clarivate year-field documentation](https://webofscience.zendesk.com/hc/en-us/articles/26916258216209-Web-of-Science-Core-Collection-Search-Fields).

For 2026, mark the actual retrieval date and **year to date**; it must not be presented as a complete calendar year. If an alternative source is used, rerun the full period under a documented consistent method and keep that series separate from this WoS snapshot.

The presentation shows unavailable years as a separate shaded region with “Not verified”, never as zero-height observed bars. The timeline accepts future verified rows without changing the chart code.

## New Scopus series

[Scopus 2000–2026](scopus/) contains a fresh all-years Elsevier dataset retrieved 27 October 2026, original filter-count exports, exact queries, provenance and an updated chart. 2026 is year-to-date. It is kept separate from this historical WoS snapshot; the presentation has not yet been switched to the new series.
