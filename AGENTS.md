# Repository instructions

## Scope

This repository maintains the SOFE stereolithographic bioprinting presentation,
its data, papers, and the materials used in its slides. Read `README.md` and the relevant
data README before editing. Preserve other contributors' changes.

## Keep data and slide materials in this repository

- Store raw data, processed CSV/JSON, exact queries, methods, source URLs,
  retrieval dates, and coverage limitations in `data/<topic>/`.
- Store full-text papers, cited books/chapters, and paper supplements in
  `papers/`, alongside `papers/catalog.json` and a readable inventory. A DOI or
  reference entry alone does not count as an archived full text. Record title,
  DOI/source when available, repository path, SHA-256, archive date, and matched
  reference numbers. Distinguish cited sources from supporting reading; never
  infer exact figure/slide provenance from a topic match.
- Keep missing full texts explicitly listed. Archive available PDFs unchanged,
  preserve their copyright/license notices, and retain supplements with their
  parent paper. Third-party papers are not relicensed under the repo's MIT
  license. Do not bundle unrelated libraries or reintroduce personal material.
- Store the images, scientific diagrams, video clips, fonts, and other materials
  actually used by the slides in `materials/`. Embedded HTML assets must also
  have separately accessible repository copies; embedding alone is insufficient.
- Keep editable vector artwork and generation scripts when available. Preserve
  attribution, licenses, and the distinction between original and adapted work.
  Do not describe rendered/compressed assets as original source files.
- Record the slide number, repository path, source, and SHA-256 in the material
  inventory. Unresolved provenance must be marked unresolved, never invented.
- Use repository-relative paths. Required inputs must not exist only in a
  personal Downloads folder, an external project directory, a temporary folder,
  a browser session, or a remote URL. If an input cannot be archived, document
  the exact missing input and reason rather than claiming a complete rebuild.
- Do not commit credentials, browser/session exports, private personal files,
  or unused reference libraries. Preserve the removal of the personal
  introduction; do not reintroduce it through an unreviewed source deck.

## Presentation maintenance

- `presentation/index.html` is the current self-contained, offline presentation;
  `presentation/transcript.md` contains its transcript and speaker notes.
- Keep theme/controller/chart code and reproducible maintenance scripts in
  `tools/`. Retain embedded media for single-file offline playback.
- After changing the presentation, run
  `python3 tools/archive_materials.py` to refresh `materials/manifest.json` and
  the separately accessible material files. Review obsolete files before
  deleting them; the archiver does not delete existing files.
- Update transcript, source credits, README, and inventories when their content
  changes. Prefer targeted updates that preserve unrelated slides.
- Full PowerPoint conversion currently requires an external source PPTX and
  rendered PDF. The material archive preserves the current web assets; it does
  not replace those conversion inputs or establish full build reproducibility.

## Data integrity and verification

- Preserve verified snapshots and distinguish missing values from zero.
  Publication counts for 2024–2026 remain unverified until supported by exports;
  record an actual retrieval date and year-to-date status for 2026.
- Preserve the 2025 transplant lower bound as a lower bound, and retain the
  2024 kidney-only scope of waiting-list callouts. Do not merge incompatible
  populations, databases, or reporting periods without documenting the method.
- After relevant data edits, run `python3 tools/check_publication_data.py` and
  `python3 tools/check_organ_data.py`, then the corresponding chart updater.
- After material changes, run `python3 tools/archive_materials.py --check`.
  Check presentation changes in a browser, including affected layouts,
  animation, media, and offline behavior. Report checks actually performed.
- After archiving or changing paper files, run `python3 tools/check_papers.py`.
- Review `git diff --check` and keep task changes focused. A local commit is
  not a remote push; report remote publication only after it succeeds.
