"""Render the three-image reveal and the transition into bioprinting."""
import base64
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = (
    ("Everyday life", "My Christmas vase", "I printed this at home for my Christmas decoration."),
    ("Engineering", "SpaceX Raptor 3", "Additive manufacturing helps integrate components into a more compact engine."),
    ("Built environment", "A printed house", "3D-printed concrete house, Eindhoven. The Dutch have printed bridges, too."),
    ("Bioprinting", "What if we could print organs?", ""),
)
NOTES = """When people think of 3D printing, they often picture a hobby printer making something for the home. I printed this vase to hold my Christmas decoration.

Engineers use the same idea at a very different scale. Take SpaceX’s Raptor 3. Additive manufacturing helps integrate components into a more compact engine.

The Dutch have even printed houses and bridges. This concrete house is in Eindhoven, and there’s a printed steel bridge in Amsterdam.

So far, we’ve been talking about objects you can see and hold. What if we could print organs?"""
RECORD = {"title": "From everyday objects to living tissue",
          "text": "\n\n".join("\n".join(filter(None, step)) for step in STEPS),
          "notes": NOTES}
# Archived copies of the supplied SoFe vase and house crops and Raptor comparison.
ASSETS = (
    ("materials/images/f57b43b39b836d36d617921a54afb0db5dfed1fed51b609d890ba2bcf20d940b.png", "3D-printed vase holding a Christmas decoration", (234, 362, 291)),
    ("materials/images/560031c0eb10f61fe391070f5078c20337ee5e64132bc1978bed4265289d1b7b.jpg", "SpaceX Raptor 1, 2 and 3 engines side by side", None),
    ("materials/images/34248b5bbbbac2b04f18392475b11deda1c6c1846db2deb6d3bfbcc263a81293.png", "Curved 3D-printed concrete house in Eindhoven", (454, 394, 260)),
)

def render_examples(section):
    """Keep the source section's number and deck navigation and footer."""
    start = section.split(">", 1)[0].replace('class="slide', 'class="slide examples-slide', 1)
    nav = re.search(r"<nav\b.*?</nav>", section, re.S)
    footer = re.search(r'<footer(?:\s[^>]*)?>.*?</footer>', section, re.S)
    cards = []
    for i, (path, alt, crop) in enumerate(ASSETS):
        blob = base64.b64encode((ROOT / path).read_bytes()).decode()
        mime = "png" if crop else "jpeg"
        src = f"data:image/{mime};base64,{blob}"
        if crop:
            w, h, cut = crop
            image = (f'<svg viewBox="0 0 {w} {cut}" role="img" aria-label="{alt}">'
                     f'<defs><clipPath id="examples-crop-{i}"><rect width="{w}" height="{cut}"/></clipPath></defs>'
                     f'<image width="{w}" height="{h}" clip-path="url(#examples-crop-{i})" href="{src}"/></svg>')
        else:
            image = f'<img alt="{alt}" src="{src}">'
        cards.append(f'<figure class="examples-card" data-card="{i}">{image}</figure>')
    copy = []
    for i, (category, title, detail) in enumerate(STEPS):
        reveal = f' data-reveal-step="{i}" aria-hidden="true" inert' if i else ""
        copy.append(f'<div class="examples-copy" data-example="{i}"{reveal}>'
                    f'<p>{category}</p><h2>{title}</h2><p>{detail}</p></div>')
    return (start + ">" + (nav[0] if nav else "") + '<div class="examples-layout">'
            + "".join(copy) + '<div class="examples-stack">' + "".join(cards) + "</div></div>"
            + (footer[0] if footer else "") + f'<!-- Speaker notes: {html.escape(NOTES)} --></section>')
