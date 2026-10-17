# Bioprinting publication trends 2000–2023

Retrieved 14 October 2026 from the user's TU Berlin Web of Science Core Collection session, all available editions. This reruns all years; it does not splice the original chart's historical counts into a new series. The original broad topic search is from Santoni et al., https://doi.org/10.1007/s42242-021-00165-0, supplementary information. Exact executed queries are in queries.json.

## Counting method

Each technique query intersects the original broad search with English, Article or Review, PY=2000–2023, and documented technique keywords. Annual values are transcribed from the complete Publication Years refinement list, with Show Final Publication Year off. Missing years are zero. Annual sums were checked against each search total: extrusion 1,385; stereolithography 769; inkjet 309; laser-assisted 152.

These are keyword-matched publications, not manually confirmed experimental applications. TS searches titles, abstracts and keyword fields. Each record is counted once within a technique, but a record matching several techniques appears in several segments. The stacked total therefore measures category matches, not unique papers. Reviews comparing several methods are included. Some records may be irrelevant or missed by the chosen terms. No record-level screening or overlap count was performed.

Stereolithography includes digital light processing, vat photopolymerization and two-photon polymerization/lithography keywords. Laser-assisted terms target laser-assisted deposition/transfer; the generic laser-assisted phrase can introduce cross-category matches. Modern volumetric methods are not comprehensively represented unless they match these terms. The original paper's exact technique classifier was not provided in the supplement, so this is a new, reproducible analysis inspired by Fig. 3b, not an exact replication. Original broad-query exclusions, including “paper” and spectroscopy terms, were retained.

## Coverage limits

The institutional session explicitly reports static content that is no longer updated (“Cancelled Customer Experience”). Its broad diagnostic bioprinting query's year facet ends in 2023. Inclusion of 2023 does not demonstrate complete calendar-year coverage; all recent-year counts must be treated as counts within this frozen collection. PY can include early-access or final-year matches; the plotted year follows the database's default Publication Years facet and may differ from final publication year. Original study combined Scopus with multiple WoS-platform databases; this chart uses Core Collection only.

## Outputs

publication_trends_2000_2023.png: high-resolution chart without inset.
publication_trends_2000_2023.svg: editable vector chart.
publication_trends_2000_2023.pdf: vector PDF chart.
annual_counts.csv: 24 annual rows and four technique columns.
plot.py: plotting script with transcribed data and total checks.
