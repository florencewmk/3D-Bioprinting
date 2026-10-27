# Papers and full-text sources

Available project-local full texts are preserved unchanged. This archive contains **19 PDFs**: 4 numbered main references and 15 supporting papers/chapters. Titles and DOIs were checked against PDF metadata and opening pages; the cited book was checked on its title/copyright pages. No new online downloads were performed.

- `cited/`: exact matches to numbered scientific references on slides 23-24.
- `supporting/`: relevant existing literature; exact slide/figure use has not been audited.
- [`catalog.json`](catalog.json): titles, DOIs, original filenames, archive dates, paths, page counts, SHA-256 hashes, and reference coverage.

Third-party copyright and license notices remain in each PDF. These documents are not relicensed under the repository MIT license. The archive includes a cited book and two book chapters, distinguished in the catalog.

## Main reference coverage

| Reference | Full text | DOI |
| --- | --- | --- |
| [1] | **Missing** | [10.1002/adem.202100477](https://doi.org/10.1002/adem.202100477) |
| [2] | **Missing** | [10.1039/D2PY01466A](https://doi.org/10.1039/D2PY01466A) |
| [3] | [PDF](cited/Bartolo-Mitchell-2003-Stereo-thermal-lithography.pdf) | [10.1108/13552540310477454](https://doi.org/10.1108/13552540310477454) |
| [4] | [PDF](cited/Bartolo-2011-Stereolithography-Materials-Processes-Applications.pdf) | [10.1007/978-0-387-92904-0](https://doi.org/10.1007/978-0-387-92904-0) |
| [5] | **Missing** | [10.1002/advs.202204072](https://doi.org/10.1002/advs.202204072) |
| [6] | [PDF](cited/Chen-2020-Advanced-NIR-Light-Cell-Functions.pdf) | [10.1002/advs.201903783](https://doi.org/10.1002/advs.201903783) |
| [7] | [PDF](cited/Santoni-2022-3D-Bioprinting-Current-Status-Trends.pdf) | [10.1007/s42242-021-00165-0](https://doi.org/10.1007/s42242-021-00165-0) |
| [8] | **Missing** | [10.1002/adhm.202300443](https://doi.org/10.1002/adhm.202300443) |
| [9] | **Missing** | [10.1371/journal.pone.0245350](https://doi.org/10.1371/journal.pone.0245350) |
| [10] | **Missing** | [10.1126/science.aav9750](https://doi.org/10.1126/science.aav9750) |

**6 full texts are still missing.** Their citations and DOI links are retained in the catalog. A reference link is not an archived full text. Supplements have not been imported in this pass.

## Archived documents

| Title | Role | Full text |
| --- | --- | --- |
| 3-D bioprinting technologies in tissue engineering and regenerative medicine: Current and future trends | Supporting reading | [PDF](supporting/3-D-bioprinting-technologies-in-tissue-engineering-and-regenerative-medicine-Current-and-future-trends.pdf) |
| 3D printing by stereolithography using thermal initiators | Supporting reading | [PDF](supporting/3D-printing-by-stereolithography-using-thermal-initiators.pdf) |
| 3D printing of new biobased unsaturated polyesters by microstereo-thermal-lithography | Supporting reading | [PDF](supporting/3D-printing-of-new-biobased-unsaturated-polyesters-by-microstereo-thermal-lithography.pdf) |
| 3D printing preview for stereo-lithography based on photopolymerization kinetic models | Supporting reading | [PDF](supporting/3D-printing-preview-for-stereo-lithography-based-on-photopolymerization-kinetic-models.pdf) |
| Advanced Near‐Infrared Light for Monitoring and Modulating the Spatiotemporal Dynamics of Cell Functions in Living Systems | Reference 6 | [PDF](cited/Chen-2020-Advanced-NIR-Light-Cell-Functions.pdf) |
| Imaging‐Guided Microscale Photothermal Stereolithography Bioprinting | Supporting reading | [PDF](supporting/ImagingGuided-Microscale-Photothermal-Stereolithography-Bioprinting.pdf) |
| Photocrosslinkable Materials for the Fabrication of Tissue-Engineered Constructs by Stereolithography | Supporting reading | [PDF](supporting/Photocrosslinkable-Materials-for-the-Fabrication-of-Tissue-Engineered-Constructs-by-Stereolithography.pdf) |
| Polyethylene Glycol and Polyethylene Glycol/Hydroxyapatite Constructs Produced through Stereo-Thermal Lithography | Supporting reading | [PDF](supporting/Polyethylene-Glycol-and-Polyethylene-Glycol-hydroxyapatite-Constructs-Produced-through-Stereo-thermal-lithogra.pdf) |
| Printing biological solutions through laser-induced forward transfer | Supporting reading | [PDF](supporting/Printing-biological-solutions-through-laser-induced-forward-transfer.pdf) |
| Recent advances in the development of stereolithography-based additive manufacturing processes: A review of applications and challenges | Supporting reading | [PDF](supporting/Recent-advances-in-the-development-of-stereolithography-based-additive-manufacturing-processes-A-review-of-app.pdf) |
| Stereo-thermallithography- a new principle for rapid prototyping | Reference 3 | [PDF](cited/Bartolo-Mitchell-2003-Stereo-thermal-lithography.pdf) |
| Stereolithographic 3D Bioprinting for Biomedical Applications | Supporting reading | [PDF](supporting/Stereolithographic-3D-Bioprinting-for-Biomedical-Applications.pdf) |
| Stereolithography 3D printing upon near-infrared photopolymerization | Supporting reading | [PDF](supporting/Stereolithography-3D-printing-upon-near-infrared-photopolymerization.pdf) |
| Stereolithography apparatus and digital light processing-based 3D bioprinting for tissue fabrication | Supporting reading | [PDF](supporting/Stereolithography-apparatus-and-digital-light-processing-based-3D-bioprinting-for-tissue-fabrication.pdf) |
| Stereolithography in tissue engineering | Supporting reading | [PDF](supporting/Stereolithography-in-tissue-engineering.pdf) |
| Stereolithography: Materials, Processes and Applications | Reference 4 | [PDF](cited/Bartolo-2011-Stereolithography-Materials-Processes-Applications.pdf) |
| The potential of unsaturated polyesters in biomedicine and tissue engineering: Synthesis, structure-properties relationships and additive manufacturing | Supporting reading | [PDF](supporting/The-potential-of-unsaturated-polyesters-in-biomedicine-and-tissue-engineering-Synthesis-structure-properties-r.pdf) |
| mSLAb – An open-source masked stereolithography (mSLA) bioprinter | Supporting reading | [PDF](supporting/mSLAb-An-open-source-masked-stereolithography-mSLA-bioprinter.pdf) |
| 3D bioprinting: current status and trends—a guide to the literature and industrial practice | Reference 7 | [PDF](cited/Santoni-2022-3D-Bioprinting-Current-Status-Trends.pdf) |

## Maintain

When adding a paper, keep the PDF and any supplements in this directory, update the catalog and inventory, and verify the files:

```sh
python3 tools/check_papers.py
```

Current reference numbers follow the web deck after removal of the personal introduction. Recheck mappings if references or slide order change.

## Paper supplements

[The Santoni et al. supplement](supplements/Santoni-2022-Supplement.docx) is archived unchanged with its parent reference 7. It provides the original Scopus broad search reused for the [2026 Scopus publication dataset](../data/publication-trends/scopus/). Retrieval, archive date and hash are listed under `supplements` in catalog.json.
