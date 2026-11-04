# Where to edit the presentation

Edit **`presentation/offline.html`**. GitHub Pages serves the lighter
**`presentation/index.html`**, generated from that file. Use **Download HTML**
in the Help panel to get a single portable file for offline use or printing.

## Change text directly in the browser

1. Open the presentation and press **E**.
2. Click text to change it.
3. Press **Cmd+S** to download your edited HTML.
4. To publish those edits, apply the text edits to `presentation/offline.html`, regenerate
   the web deck with the commands below, then commit and push the changes.

Browser edits save only in that browser until you download/publish them.
The Help panel’s **Reset browser edits** button removes local overrides.
Labels baked into scientific figures cannot be edited as text.

## Change event details and opening slides

Edit **`presentation/settings.json`**. It contains the city, competition date,
cover tagline, presenter name, three introduction points, opening question,
background source, and the three menu labels and destinations.

Then run this in the repository folder:

```sh
python3 tools/update_opening.py
python3 tools/archive_materials.py
python3 tools/build_online.py
```

This updates the first four slides, shared menu/date/footer, notes, and
transcript while preserving the scientific slide artwork. Refresh the browser
after saving. Keep JSON quotes and commas intact.

## Edit HTML, layout, or animations

| File | What to edit |
| --- | --- |
| `presentation/offline.html` | Editable deck; search `id="slide-4"` to reach a slide |
| `presentation/index.html` | Generated web deck; refresh with `python3 tools/build_online.py` |
| `tools/deck.css` | Fonts, sizes, positions, colors, presenter crop, and question zoom animation |
| `tools/deck.js` | Keyboard navigation, overview, browser text editing, saving |
| `tools/slide-motion.js` | Content-aware entrances and 620 ms slide transitions; refresh with `python3 tools/update_motion.py` |
| `tools/cover_slide.py` | Cover HTML structure and lung photo |
| `tools/opening_slides.py` | Introduction, contents, centered question, shared menu/footer |
| `presentation/transcript.md` | Readable slide text and speaker notes |

After editing the maintained CSS, controller, or opening templates, run the
commands above to embed them in the published HTML. For direct HTML changes, run just the archiver and online builder. Rerunning
the opening updater rebuilds slides 1–4 from settings.
The remaining scientific slide text can be edited directly in the HTML, using
`data-edit` labels or the per-slide comments to find it. Embedded image/font
data looks very long: leave those `data:...;base64,...` strings intact.

Restoring the introduction makes the order **Florence 1 → cover 2 → contents 3
→ opening question 4** in the source layout. In the published deck, organ shortages are on slide 7, publication trends on slide 8, the interactive globe on slide 9, the animated printing-with-light slides on 10–16, and Contents on slide 59. The former technology slides 10–15 are now backup slides 31–36.
The application slides remain under the Printing methods menu section.

For chart edits, use `tools/update_publication_slide.py` and
`tools/update_organ_slide.py`. They preserve the other 50 slide sections.

To preview locally:

```sh
python3 -m http.server 3000
```

Open `http://127.0.0.1:3000/presentation/index.html`. GitHub changes go live only
after a commit, push, and successful Pages deployment.

The presenter slide starts with only the name and full, undistorted photo.
Click the slide, press Space/Right, or use Next to reveal each of the three
points. After the third point, the next advance opens the cover. Left/Previous
hides a point; Home returns to the start with all points hidden. Press E to
show all points for editing. The photo uses the natural aspect ratio of the exact cropped portrait selected by the user.

## Animation pacing

Every slide has an entrance animation and a transition. New slides inherit the
same content-aware motion when the deck reloads. Transitions take 620 ms;
most entrances take 0.7–1.1 seconds, with short staggered delays for comparisons
and ordered explanations. Advancement stays under presenter control.

After editing `tools/slide-motion.js`, run `python3 tools/update_motion.py` and
`python3 tools/archive_materials.py`. A full build embeds motion automatically;
targeted updaters preserve it. See `tools/MOTION.md` for timing details.

The presenter starts with name/photo only. Click, Space/Right, or Next reveals one point; the fourth advance opens the cover. Left/Previous hides a point; Home resets the introduction. E shows all points for editing. The selected cropped portrait keeps its natural proportions.

## Printing-with-light slides (10–16)

The seven animated slides (Chuck Hull and SLA, patient to print, bottom-up vs
top-down, light sources, bioink and curing, obstacles, womb analogy) come from
`tools/light-slides.html` (markup, scoped CSS and animation script) and
`tools/light-slides-notes.json` (speaker notes). After editing either file run:

```sh
cd tools && python3 light_slides.py && cd ..
python3 tools/archive_materials.py
python3 tools/build_online.py
```

Each slide reveals one point per Down/click through hidden `.ls-step` markers
handled by the deck controller. Up hides the last point. Sources sit in one
“Source:” line above the footer; slides cite papers only.
