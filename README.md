# 3D Bioprinting

**Stereolithographic Bioprinting — 3D bioprinting using light**
Florence Mei Kuan Wong · SOFE Berlin · 15 October 2026

## Open the presentation

Open [`presentation/index.html`](presentation/index.html) in a browser, or download that file and double-click it. It is a single self-contained HTML file (approximately 25 MB), including Jost fonts, scientific artwork and two MP4 videos. No installation, build step or internet connection is needed for viewing.

The selected design uses a black background, lavender/pink/cyan typography, and a restrained layer motif. All slides keep a fixed 1920 × 1080 stage, scaled uniformly to any screen.

![Cover](presentation/cover.jpg)

## Contents

| Slides | Content |
| --- | --- |
| 1–23 | Main talk |
| 24–28 | References and image credits |
| 29–51 | Technical backup |

The 51 source slides remain in their original order. Scientific diagrams and chart geometry are vector artwork where possible; source photographs and paper figures remain images. Most slide text is editable HTML. Text embedded in scientific figures is preserved within the artwork. Source PowerPoint object animations are replaced with web transitions; both embedded videos retain manual playback controls.

## Controls

- **Arrow keys / Space / Page Up / Page Down**: navigate; horizontal swipes and mouse wheel also work.
- **O**: overview. **N**: original speaker notes and source transcript. **F**: fullscreen.
- **Home / End**: first or last slide. **Esc**: close panels.
- **E**: enable text editing, then click text. Edits autosave in this browser.
- **Ctrl/Cmd + S**: download an HTML copy containing your edits.
- Slide hashes such as `presentation/index.html#15` open a specific slide.

A readable [source transcript and speaker notes](presentation/transcript.md) accompany the deck. Text edits in the HTML do not rewrite this original-source transcript or speaker notes.

## Rebuild

The original PPTX is kept outside this repository. The conversion source was `SoFe Competition.pptx`, SHA-256 `c40db77325caf103a88d7b2fdfc6cfc97601140c86f5c9bd071ff266d2756407`.

The conversion uses Python 3 with `python-pptx`, `Pillow`, and `pymupdf`, plus LibreOffice for intermediate rendering. Run `python tools/render_source.py /path/to/SoFe-Competition.pptx /tmp/sofe-render`, then:

```sh
python tools/build_deck.py /path/to/SoFe-Competition.pptx /tmp/sofe-render/render-source.pdf
```

`tools/deck.css`, `tools/deck.js` and `tools/shell.html` contain the presentation theme and controller. `tools/viewport-base.css` contains the fixed stage rules. `tools/fonts.css` embeds the font data. Temporary PDF/render files and the original PPTX are not required to view the final deck.

## Verification

All 51 slides were browser-rendered at 1280 × 720 and visually reviewed. Browser checks cover navigation, notes, overview, editing/autosave, video playback and fixed 16:9 scaling at 390 × 844. Historical data and scientific claims are carried over from the source; this conversion is not a new literature review.

## Credits

Scientific sources and image credits are retained on the slides and in the transcript. Third-party photographs, figures and videos retain their respective rights; the repository license does not relicense those materials. Jost is bundled under the [SIL Open Font License](presentation/Jost-OFL.txt).
