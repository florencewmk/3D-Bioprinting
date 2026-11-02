"""Render the cover using the archived, user-supplied lung photograph."""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LUNG = ROOT / 'materials/images/9d7286d75b51d262d1a1e6fa60fa9596a1a3df095bcac5aca852fd1692f96222.png'


def render_cover():
    image = 'data:image/png;base64,' + base64.b64encode(LUNG.read_bytes()).decode()
    return (
        '<figure class="cover-lung">'
        f'<img src="{image}" width="1064" height="859" '
        'alt="Blue and cream branching 3D-printed lung anatomical model in a transparent display case">'
        '</figure><div class="hero">'
        '<p class="eyebrow editable" data-edit="cover-event-brand">SOfE · BERLIN · 2026</p>'
        '<h1><span class="editable cover-descriptor" data-edit="cover-title">Stereolithographic</span>'
        '<em class="editable gradient cover-focus" data-edit="cover-subtitle">Bioprinting</em></h1>'
        '<p class="hero-sub editable" data-edit="cover-tagline">3D bioprinting using light</p>'
        '</div><p class="signature editable" data-edit="cover-author">Florence Mei Kuan Wong</p>'
    )
