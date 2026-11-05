# 3D Bioprinting

**where engineering revolutionizes medicine**

Florence Mei Kuan Wong · SOfE Düsseldorf · 5 November 2026

![Presentation cover](presentation/cover.jpg)

## View the slides

Open [the presentation](presentation/index.html) in a browser. The web deck loads large media as you approach the relevant slides. Use **Help → Download HTML** or **Ctrl/Cmd+S** to save a portable copy with the fonts, videos, lung animation and interactive map included. No installation is required.

The deck contains **59 slides**:

| Slides | Content |
| --- | --- |
| 1–24 | Main talk |
| 25–29 | References and image credits |
| 30–59 | Technical backup (31–36: earlier technology overview slides) |

[Transcript and speaker notes](presentation/transcript.md)

## Controls

| Key | Action |
| --- | --- |
| ← / → | Previous / next slide |
| ↑ / ↓ | Previous / next reveal or chart year |
| Space / Page Up / Page Down | Navigate |
| O | Slide overview |
| N | Speaker notes |
| F | Fullscreen |
| Home / End | First / last slide |
| Esc | Close panels |
| E | Edit slide text; changes save in your browser |
| Ctrl/Cmd + S | Download an HTML copy with your edits |

Slides 10–16 (printing with light) reveal their points one by one with Down/Up or a click; edit them in `tools/light-slides.html` and run `python3 tools/light_slides.py`. On slide 24, press Down to reveal the GitHub link and QR code. Press Up to return to the centered thank-you message.

Horizontal swipes and the mouse wheel also navigate. Link to a specific slide with a hash, such as `presentation/index.html#7`. Text inside figure images is not editable; browser edits do not update the transcript.

Every slide has content-aware entrance animations and a gentle 620 ms transition.
Comparisons reveal in reading order; technical figures stay aligned as they fade
in. Slide advancement remains presenter controlled. Reduced-motion preferences
are respected. [Animation maintenance and timing](tools/MOTION.md).

## Data and sources

- **[Worldwide bioprinting geography through 2025](data/geography-2025/):** Excel workbook and CSV files with top-20 country rankings, full author/affiliation tables, institutional coordinates, and a sourced company register with historical and unconfirmed status flags.
- **[Publication trends · slide 8](data/publication-trends/):** Scopus (Elsevier) counts for 2000–2026, with a roughly six-second continuous left-to-right reveal. 2026 is partial as of 27 October 2026; [CSV and methods](data/publication-trends/scopus/).
- **[Organ-transplant timeline](data/organ-transplants/):** reported2015–2025 activity;2025 six-organ total183,879 and49,169 deceased donors. Right callouts sum reported2025 organ-list entries:532,905 waiting;40,019 deaths. Source: archived EDQM–ONT Newsletter Transplant2026. No2026forecast.

The publication chart reveals automatically without buttons inside the chart; the bottom toolbar provides Replay and arrows for year selection. On the chart, Up/Down select years and R replays. The organ chart has playback controls. Their data directories include raw values, sources and coverage limitations.

Slide images, SVG artwork, both videos, and fonts are also available separately
in [materials/](materials/), with a slide-to-file inventory and SHA-256 hashes.
Repository maintenance rules are in [AGENTS.md](AGENTS.md).

Available full-text papers, cited books/chapters, and supporting reading are
stored in [papers/](papers/), with a DOI/file inventory and an explicit list of
references whose full texts are still missing.

## Maintain the presentation

Edit `presentation/offline.html` and regenerate the web deck at `presentation/index.html`. Theme, controller and conversion scripts are in `tools/`. The original PowerPoint is kept outside this repository. The presenter introduction is slide 1, before the cover on slide 2. It starts with the name/photo and reveals the three points one per click. [Editing guide](EDITING.md); [opening-slide settings](presentation/settings.json).

After changing chart data, run the corresponding updater from the repository root:

```sh
python3 tools/update_publication_slide.py
python3 tools/update_organ_slide.py
```

Each updater preserves the other 50 slide sections. Check the data with `tools/check_publication_data.py` and `tools/check_organ_data.py`. Full conversion requires Python with `python-pptx`, Pillow and PyMuPDF, plus LibreOffice; see `tools/render_source.py` and `tools/build_deck.py` for their command-line arguments.

## Credits

Scientific sources and image credits are retained in the deck and transcript. Third-party figures, photographs and videos retain their respective rights. Jost is bundled under the [SIL Open Font License](presentation/Jost-OFL.txt).
