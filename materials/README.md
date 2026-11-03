# Slide materials

This directory contains separately accessible copies of the media and SVG
artwork used in the current 51-slide HTML presentation. The offline HTML keeps
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

## Cover turntable

Slide 2 shows a Blender reconstruction of the branching anatomical model
photographed by Lü Bin/Xinhua at the 2015 Yiwu equipment expo. The reference
photograph remains archived under `images/9d7286d75b51d262d1a1e6fa60fa9596a1a3df095bcac5aca852fd1692f96222.png`.
The transparent WebP loop and first-frame poster are archived separately and
embedded in the offline presentation. `tools/cover_slide.py` identifies both by SHA-256.

## Restored presenter and question background

The user requested the presenter slide back on 3 November 2026. The original
portrait is stored unchanged as `images/5e80ebede67629c0d01ce604baa50b3d5a3a240d3ffbced5e30d467d00c5fd8b.jpg`;
The user-supplied IMG_6938.JPG matches these original bytes; the full 4:3 image is now shown without cropping or stretching. The aerial background is the unchanged
user-supplied still `images/7e594d8a3443bf14af0d2ef00cbc3b56943530c380f6e9e52c0da59b1195cbf3.png`,
credited to the [YouTube source supplied by the user](https://www.youtube.com/watch?v=ONBHkzimRbg).
Only a CSS zoom is applied; the video itself is not downloaded or embedded.
Source paths and provenance are also recorded in `presentation/settings.json`.

### Selected presenter illustration

Slide 1 uses the user-selected `florence-hello.svg`, with a looping wave, archived as
`materials/diagrams/7e0f67a1a4811036feb21f44a4969593043df6fb87763b59460a6bf72bfce55d.svg`. The SVG is embedded for offline playback.
