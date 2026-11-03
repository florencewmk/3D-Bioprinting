"""Render the three-image reveal and the transition into bioprinting."""
import base64
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = (
    ("Everyday life", "My Christmas vase", ""),
    ("Engineering", "SpaceX Raptor 3", "Additive manufacturing helps integrate components into a more compact engine."),
    ("Built environment", "A printed house", "Eindhoven concrete house (illustration). The Dutch have printed bridges, too."),
    ("Bioprinting", "What if we could print organs?", ""),
)
NOTES = """When people think of 3D printing, they often picture a hobby printer making something for the home.

Engineers use the same idea at a very different scale. Take SpaceX’s Raptor 3. Additive manufacturing helps integrate components into a more compact engine.

The Dutch have even printed houses and bridges. This concrete house is in Eindhoven, and there’s a printed steel bridge in Amsterdam.

So far, we’ve been talking about objects you can see and hold. What if we could print organs?"""
RECORD = {"title": "From everyday objects to living tissue",
          "text": "\n\n".join("\n".join(filter(None, step)) for step in STEPS),
          "notes": NOTES}
# Archived ImageGen cutouts and supplied Raptor comparison.
ASSETS = (
    ("materials/images/7b1ce1f737590ff915b1e8ed64000c73d767ea1c363cd6a54d6117dd88d58bfb.png", "3D-printed vase holding a Christmas decoration", "png"),
    ("materials/images/560031c0eb10f61fe391070f5078c20337ee5e64132bc1978bed4265289d1b7b.jpg", "SpaceX Raptor 1, 2 and 3 engines side by side", "jpeg"),
    ("materials/images/45ce8684cee3a64960e394d3b57d499b1e356e1bfe8dc75db5ef9b88f6b6d4ed.png", "Illustration of the curved 3D-printed concrete house in Eindhoven", "png"),
)

def render_examples(section):
    """Keep the source section's number and deck navigation and footer."""
    start = section.split(">", 1)[0].replace('class="slide', 'class="slide examples-slide', 1)
    start = start.replace('examples-slide examples-slide', 'examples-slide', 1)
    nav = re.search(r"<nav\b.*?</nav>", section, re.S)
    footer = re.search(r'<footer(?:\s[^>]*)?>.*?</footer>', section, re.S)
    cards = []
    for i, (path, alt, format) in enumerate(ASSETS):
        blob = base64.b64encode((ROOT / path).read_bytes()).decode()
        image = f'<img alt="{alt}" src="data:image/{format};base64,{blob}">'
        cards.append(f'<figure class="examples-card" data-card="{i}">{image}</figure>')
    copy = []
    for i, (category, title, detail) in enumerate(STEPS):
        reveal = f' data-reveal-step="{i}" aria-hidden="true" inert' if i else ""
        copy.append(f'<div class="examples-copy" data-example="{i}"{reveal}>'
                    f'<p>{category}</p><h2>{title}</h2><p>{detail}</p></div>')
    return (start + ">" + (nav[0] if nav else "") + '<div class="examples-layout">'
            + "".join(copy) + '<div class="examples-stack">' + "".join(cards) + "</div></div>"
            + (footer[0] if footer else "") + f'<!-- Speaker notes: {html.escape(NOTES)} --></section>')
