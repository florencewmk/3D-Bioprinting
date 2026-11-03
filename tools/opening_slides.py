"""Editable opening slides and shared event/navigation settings."""
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def settings():
    return json.loads((ROOT / 'presentation/settings.json').read_text())


def image_uri(path):
    mime = 'image/png' if path.endswith('.png') else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode((ROOT / path).read_bytes()).decode()


def footer(number):
    c = settings()
    return (f'<footer><span>{html.escape(c["event"]["date"])}</span>'
            f'<span>{html.escape(c["presenter"])}</span><span>{number:02d} / 51</span></footer>')


def navigation(number):
    c = settings()
    active = 'Introduction' if number < 10 else 'Printing methods' if number < 21 else 'Conclusion' if number < 24 else ''
    buttons = ''.join(f'<button data-goto="{s["slide"]}" class="{"current" if s["label"] == active else ""}">{html.escape(s["label"])}</button>' for s in c['sections'])
    label = 'REFERENCES' if 24 <= number < 29 else 'BACKUP' if number >= 29 else ''
    return f'<nav class="section-nav" aria-label="Talk sections">{buttons}<span>{label}</span></nav>'


def render_introduction():
    c = settings()
    # Photo retains the source PowerPoint crop and position.
    points = ''.join(f'<li class="editable" data-edit="profile-point-{i}">{html.escape(text)}</li>' for i, text in enumerate(c['introduction']['points'], 1))
    return (f'<div class="profile-glow" aria-hidden="true"></div>'
            f'<h1 class="profile-name editable" data-edit="profile-name">{html.escape(c["presenter"])}</h1>'
            f'<ul class="profile-points">{points}</ul>'
            f'<figure class="profile-photo"><img src="{image_uri(c["portrait"]["path"])}" alt="Florence Mei Kuan Wong standing in a snowy alpine village"></figure>')


def render_contents():
    c = settings()
    cards = ''.join(f'<button class="chapter" data-goto="{s["slide"]}"><span class="chapter-no">{i:02d}</span><span>{html.escape(s["label"])}</span><small>{s["slide"]:02d} →</small></button>' for i, s in enumerate(c['sections'], 1))
    return ('<div class="contents-heading"><p class="eyebrow">THE TALK</p>'
            '<h1 class="editable" data-edit="contents-title">Contents</h1></div>'
            f'<div class="contents-list">{cards}</div>')


def render_question():
    c = settings()
    lines = '<br>'.join(html.escape(line) for line in c['opening_question'])
    return (f'<div class="question-background" aria-hidden="true"><img src="{image_uri(c["opening_background"]["path"])}" alt=""></div>'
            '<div class="question-shade" aria-hidden="true"></div>'
            f'<div class="question-center"><h1 class="editable" data-edit="opening-centered-question">{lines}</h1></div>'
            f'<a class="question-credit" href="{html.escape(c["opening_background"]["source_url"])}" target="_blank" rel="noopener noreferrer">Background source · YouTube</a>')
