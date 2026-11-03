"""Render the cover using the reconstructed lung turntable."""
import base64
import html
from opening_slides import settings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LUNG_ANIMATION = ROOT / 'materials/images/1786970f76a9a466241c8f1d73348d20887c56f67d4135e133495fb97bac3c88.webp'
LUNG_POSTER = ROOT / 'materials/images/973f5492d7238e8f5907aca8d6e188cb20872926dfc460ed4d77ea6f84cfd15e.webp'
COVER_TITLE = '3D-Bioprinting'
COVER_NOTES = ('Welcome to the world of 3D printing, a technology that is shaping our future.\n\n'
               'On the right is a 3D reconstruction of a branching anatomical model displayed in Yiwu in 2015.')


def render_cover():
    c = settings()
    event = html.escape(f'{c["event"]["name"]} · {c["event"]["city"].upper()} · {c["event"]["date"].upper()}')
    animation = 'data:image/webp;base64,' + base64.b64encode(LUNG_ANIMATION.read_bytes()).decode()
    poster = 'data:image/webp;base64,' + base64.b64encode(LUNG_POSTER.read_bytes()).decode()
    return (
        '<figure class="cover-lung">'
        f'<img class="cover-turntable" src="{poster}" data-turntable-src="{animation}" '
        'width="1200" height="967" alt="Rotating blue and cream branching lung model">'
        '</figure><div class="hero">'
        f'<p class="eyebrow editable" data-edit="cover-event-nov5">{event}</p>'
        f'<h1><em class="editable gradient cover-focus" data-edit="cover-title-3d">{COVER_TITLE}</em></h1>'
        f'<p class="hero-sub editable" data-edit="cover-tagline-medicine">{html.escape(c["cover_tagline"])}</p>'
        f'</div><p class="signature editable" data-edit="cover-author">{html.escape(c["presenter"])}</p>'
    )
