# Slide materials

This directory contains separately accessible copies of the media and SVG
artwork used in the current 50-slide HTML presentation. The offline HTML keeps
its embedded copies. These files were exported from the current web deck and
can include compressed images, video posters, and rendered vector artwork;
they are not a claim to contain original publisher files or editable source
PowerPoint diagrams.

- `images/`: embedded photographs, figures, and video posters.
- `diagrams/`: inline SVG artwork, including chart snapshots at export time.
- `videos/`: both embedded MP4 clips.
- `fonts/`: embedded Jost font files; license in
  [`presentation/Jost-OFL.txt`](../presentation/Jost-OFL.txt).
- [`manifest.json`](manifest.json): file paths, SHA-256 hashes, byte sizes, MIME
  types, and current slide numbers. Fonts shared by the deck have no individual
  slide assignment.

Scientific references and image/video credits remain in the
[presentation](../presentation/index.html) and
[transcript](../presentation/transcript.md). The inventory identifies the web
asset's immediate source; individual original attribution has not been fully
resolved. Third-party assets retain their respective rights and are not
relicensed by this repository's license.

Chart values, queries, and methods are in [`data/`](../data/). The SVG chart
copies are static; the HTML uses the data and chart controllers for animation.

Refresh and verify from the repository root:

```sh
python3 tools/archive_materials.py
python3 tools/archive_materials.py --check
```

The archiver does not remove old files. Review and remove unused archived files
explicitly when retiring a material. The original PPTX and PDF conversion inputs
are not part of this archive; a full source conversion still requires them.
