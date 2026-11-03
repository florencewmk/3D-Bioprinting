"""Render the cover using the archived, user-supplied lung photograph."""
import base64
import html
from opening_slides import settings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LUNG = ROOT / 'materials/images/9d7286d75b51d262d1a1e6fa60fa9596a1a3df095bcac5aca852fd1692f96222.png'


def render_cover():
    c = settings()
    event = html.escape(f'{c["event"]["name"]} · {c["event"]["city"].upper()} · {c["event"]["date"].upper()}')
    image = 'data:image/png;base64,' + base64.b64encode(LUNG.read_bytes()).decode()
    return (
        '<figure class="cover-lung">'
        f'<img src="{image}" width="1064" height="859" '
        'alt="Blue and cream branching 3D-printed lung anatomical model in a transparent display case">'
        '</figure><div class="hero">'
        f'<p class="eyebrow editable" data-edit="cover-event-nov5">{event}</p>'
        '<h1><span class="editable cover-descriptor" data-edit="cover-title">Stereolithographic</span>'
        '<em class="editable gradient cover-focus" data-edit="cover-subtitle">Bioprinting</em></h1>'
        f'<p class="hero-sub editable" data-edit="cover-tagline-medicine">{html.escape(c["cover_tagline"])}</p>'
        f'</div><p class="signature editable" data-edit="cover-author">{html.escape(c["presenter"])}</p>'
    )
