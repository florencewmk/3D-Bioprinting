# Bioprinting publication trends from Scopus

Fresh Scopus (Elsevier) searches for **2000–2026**, retrieved **27 October 2026** through TU Berlin institutional access. This series is independent of the earlier frozen Web of Science dataset. No WoS counts or estimates are used here.

## Files

- [annual_counts_2000_2026.csv](annual_counts_2000_2026.csv): 27 annual rows, four technique counts, coverage, retrieval date and database.
- [queries.json](queries.json): exact executed queries recorded by Scopus in its raw exports.
- [raw/](raw/): unchanged Scopus “Export filter counts” CSVs, one per technique. They contain year counts and other public bibliographic facet summaries, not full-text papers or record-level exports.
- [provenance.json](provenance.json): raw-file SHA-256 hashes, totals and document-type checks.
- [publication_trends_2000_2026.png](publication_trends_2000_2026.png), [SVG](publication_trends_2000_2026.svg), [PDF](publication_trends_2000_2026.pdf): stacked bars and five-year inset using the approved palette. Hatching and dashed lines mark 2026.

| Year | Laser-assisted | Inkjet | Stereolithography | Extrusion |
| --- | ---: | ---: | ---: | ---: |
| 2023 | 39 | 62 | 188 | 296 |
| 2024 | 23 | 56 | 193 | 285 |
| 2025 | 31 | 49 | 201 | 345 |
| 2026* | 39 | 62 | 232 | 419 |

*2026 is year-to-date / indexed as of 27 October 2026. It is not a complete calendar-year total. Scopus can index advance/assigned publication years; values describe records available at retrieval, not papers proven published before that date. Earlier years are calendar-year snapshots at the same retrieval date and can change through later indexing/corrections.

## Search and classification

The broad query is the original Scopus query from Santoni et al., *3D bioprinting: current status and trends—a guide to the literature and industrial practice*, DOI [10.1007/s42242-021-00165-0](https://doi.org/10.1007/s42242-021-00165-0), supplementary information. The supplement is [archived in this repository](../../../papers/supplements/Santoni-2022-Supplement.docx). Original supplementary source: [Springer DOCX](https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs42242-021-00165-0/MediaObjects/42242_2021_165_MOESM1_ESM.docx).

It is intersected with `PUBYEAR > 1999 AND PUBYEAR < 2027`, English language, journal source type, and Article or Review document type. Each technique uses the same keyword group as the earlier analysis, translated to Scopus `TITLE-ABS-KEY`:

- Extrusion: extrusion, microextrusion, micro-extrusion.
- Inkjet: inkjet and separated/hyphenated ink-jet variants.
- Stereolithography: stereolithography, digital light processing, vat photopolymerization, two-photon polymerization/lithography variants.
- Laser-assisted: laser-assisted, laser-induced forward transfer, laser direct writing, laser bioprinting, laser-based bioprinting, and laser printing variants.

Full syntax and original exclusions are preserved in queries.json, including the original broad exclusions for “paper” and spectroscopy terms. These exclusions can remove relevant work and were retained for methodological continuity. Scopus proximity syntax (`PRE/1`, `W/2`), keyword coverage and indexing differ from WoS; identical classification terms do not imply comparable absolute counts across databases.

A paper can match several techniques, especially reviews: stacked totals are **technique matches, not unique papers**. Keyword matches indicate mentions in title/abstract/keyword fields, not manually verified experimental use. The original paper does not supply an explicit Fig. 3b classifier; this is a reproducible new analysis inspired by that chart. New methods not matching these four groups may be missed. No manual screening or overlap deduplication was performed across techniques.

Scopus indexes multiple publishers. ScienceDirect primarily hosts Elsevier full text and would have a narrower publisher population; see [Elsevier's database comparison](https://www.elsevier.support/dataasaservice/answer/what-is-the-difference-between-sciencedirect-and-scopus-data).

## Verification and rebuild

All annual counts come directly from raw Scopus exports. Missing year rows in a successfully retrieved complete facet are filled with zero. Annual sums and Article/Review facet sums independently match the visible result totals:

- Laser-assisted: **334**
- Inkjet: **595**
- Stereolithography: **1,497**
- Extrusion: **2,515**

From the repository root, run `python3 tools/build_scopus_publication_counts.py`. It uses the Python standard library, checks sums and document types, and rebuilds the CSV, exact query JSON and provenance manifest. `tools/plot_scopus_publication_counts.py` renders the chart and requires Matplotlib/NumPy. Source exports and scripts are repository-local.

The existing presentation and WoS files are preserved; this task adds an independent Scopus dataset and chart rather than silently replacing the deck's historical source.
