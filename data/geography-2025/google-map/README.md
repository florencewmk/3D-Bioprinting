# Google My Maps: bioprinting through 2025

[Open the interactive map](https://www.google.com/maps/d/u/0/viewer?mid=1xMICGif7YhqVEFiDnPdq-cAFGzoo6v0&ll=0%2C10&z=1) · [Owner editor](https://www.google.com/maps/d/u/0/edit?mid=1xMICGif7YhqVEFiDnPdq-cAFGzoo6v0)

Created and checked in Google My Maps on 27 October 2026. Access depends on the owner's Google sharing settings; sharing permissions were not changed. The viewer link requests a world overview. Pan, zoom, click markers for details, and toggle layers in the sidebar.

| Layer | Features | Initially visible |
|---|---:|---|
| Companies | 38 | Yes |
| Research affiliations — top 100 | 100 | Yes |
| Other affiliations — part 1 | 1,900 | No |
| Other affiliations — part 2 | 2,000 | No |
| Other affiliations — part 3 | 1,342 | No |
| Authors — top 100, institutional locations | 172 | No |
| Top 20 countries — publications 2000–2025 | 20 | No |

The map contains 5,572 features: 5,342 institutions, 38 company lineages, 172 institutional locations for 100 authors, and 20 country summary points. Institution partitions do not overlap. One institution lacks valid coordinates and is listed in `unmapped.csv`. Company points use Google city/country geocoding and are approximate, not precise offices. Country markers represent country summaries. Author points represent last-observed institutional affiliations in the corpus through 2025, not residence, nationality, or current employment.

## Sources and scope

The map derives entirely from the [saved geography snapshot](../README.md), whose raw metadata, source URLs, queries, methods and limitations are archived in the parent directory. Research uses OpenAlex title/abstract keyword articles/reviews published in 2000–2025, retrieved 27 October 2026. Institutions and authors are selected by 2021–2025 publication counts. The country layer uses cumulative 2000–2025 counts. Company records combine official company/product/location pages, dated activity evidence and other documented sources; this is a curated shortlist, not a global company census. Nineteen lineages have explicit 2025 activity evidence; evidence status is retained in each marker. Historical Allevi and grouped Allegro records are excluded from the independent company count.

## Rebuild and import

Run `python3 tools/build_google_map_layers.py` from the repository root. Import the seven numbered files into separate My Maps layers. For CSV files choose `Location` for position and `Name` for the title. KML files already contain coordinates and descriptions. KML uses only name/description data columns to keep the map within My Maps data-cell limits; institution files are split below the 2,000-feature per-layer limit. Imported files total fewer than 10,000 features in seven layers. See `layer-manifest.json` for file hashes and geometry details.

In the saved map, all companies share one Companies layer and uniform style. All other layers also use uniform style. The colors recorded in the generated KML/manifest are requested input colors, which My Maps did not preserve; they do not describe the final map's styling. Google performs the company/country geocoding, so regeneration of input files does not guarantee identical Google positions or styles.

## Verification

All seven imported feature counts were checked in the native My Maps layer controls/data tables. The company table retained product, 2025 status, activity and location source URLs; the institution table retained publication counts, OpenAlex/ROR links and scope notes. The viewer showed all seven layer toggles and the two intended default layers. CSV/XML counts and SHA-256 values were independently checked against the manifest. No source dataset, presentation, or sharing settings were changed by the map build. `delivery.json` records the map identifier and verified counts.

On 27 October 2026, the two company layers were combined at the user’s request. All 38 company records remain; no Role or evidence-status subcategories appear in the legend. The Companies layer is initially visible. Historical split CSV files were replaced by `01-companies.csv`.
