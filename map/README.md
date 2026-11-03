# Bioprinting World Map

Custom interface requested on 3 November 2026. It uses the same 5,572 research/company records as the Google My Maps dataset, with five categories: Companies (38), Affiliations (100), Other affiliations (5,242), Authors (172 institutional locations for 100 authors), and Top 20 countries (20).

## Controls

- The category checkbox selects or clears **all countries and records** in that category. Partial selections display a dash.
- The category arrow independently opens or closes its country menu. It works while the category is unselected and never changes the map selection.
- A country checkbox selects or clears its points.
- Each country's **List** checkbox independently opens or closes its list of names. Lists start closed.
- Individual records have selection checkboxes; clicking a name opens its marker and source details.
- **Sort countries** offers Name A–Z, Name Z–A, Most entries first, and Fewest entries first. It changes country order in every category without changing selected points or open name lists. Counts follow search matches while search is active.
- Search filters names/countries among the selected map points. It does not silently select hidden categories. Selection controls still apply to the full category/country, even while search is active.
- **Collapse lists** closes every menu without changing selection. **Fit selection** frames the currently shown points.

All countries are individually available; there is no 20-country grouping cap. The old Other affiliations parts are combined. Marker clusters retain coincident locations and expand as you zoom or click them. Only names for an explicitly opened country are rendered; long lists have a Show more control.

## Sources and geometry

The research/company snapshot remains [the archived geography dataset](../data/geography-2025/README.md), retrieved 27 October 2026, with publication cutoff 2025. Research counts, names, descriptions, evidence qualifications, and institutional coordinates are retained. One institution lacks coordinates and is excluded as before. Institutions can include parent/child organization IDs; company records are a curated sample, not a global census.

The My Maps export preserved addresses but omitted coordinates for company and country-summary markers. The custom interface therefore uses **GeoNames city points** for the same 38 company cities and **Natural Earth country label anchors** for the 20 country summaries. These are approximate city/country locations, not precise offices. The 5,514 institution/author points retain the original coordinates. See [custom map provenance](../data/geography-2025/custom-map/provenance.json) and the [city match audit](../data/geography-2025/custom-map/company-city-matches.json).

`python3 tools/build_interactive_map.py` rebuilds `data.json` from repository-local inputs. It checks the original export's 5,572 records, exact company/country name sets, geometry ranges, category totals and IDs. Serve this directory with a static HTTP server; all application libraries are local. The OpenStreetMap base tiles need internet access. There is no API key, backend, analytics, or tracking code.

## Licenses

- Leaflet 1.9.4: BSD 2-Clause, `vendor/leaflet-LICENSE`.
- Leaflet.markercluster 1.5.3: MIT, `vendor/markercluster-LICENSE`.
- GeoNames: CC BY 4.0, https://www.geonames.org/; archived city gazetteer from https://download.geonames.org/export/dump/cities500.zip.
- Natural Earth: public domain, https://www.naturalearthdata.com/; archived `ne_50m_admin_0_countries.geojson` from the project's official GitHub repository.
- OpenStreetMap base map: © OpenStreetMap contributors, https://www.openstreetmap.org/copyright.

The original Google map is retained and its sharing settings are unchanged. The custom Site deployment identity lives in the separate project workspace, not in the research repository.

## English-default map labels

The background uses CARTO Positron vector tiles, rendered through MapLibre GL JS 5.6.1 and the MapLibre Leaflet adapter 0.1.3. The existing Leaflet markers, filters and layout are retained. `basemap-english.json` prefers `name:en` / `name_en` for place labels, with a single proper-name fallback where the geographic source has no English variant. Official company, author and institution names remain unchanged. This replaces the former raster background whose local-language names were baked into images. No Google API key or Google Cloud project is used.

MapLibre is BSD 3-Clause (`vendor/maplibre-LICENSE`); the adapter license is in `vendor/leaflet-maplibre-LICENSE`. Style source: https://basemaps.cartocdn.com/gl/positron-gl-style/style.json; English label rules are saved locally rather than depending on a changing remote style. CARTO attribution is visible on the map.
