"""Restyle the five reference slides as two-column cards (9 Nov 2026).

Reads the citations that tools/reference_slides.py rendered (the <p class="editable">
entries and group <h2> headings) and rebuilds each slide as: title "References",
page "n / 5", group pills (Scientific · Data & online · Images, clickable), and
cards with authors + year, title, venue and a short link. Rerun after
reference_slides.py; it is idempotent (it reads its own cards too).
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "presentation/offline.html"
SECTION = re.compile(r'<section\b[^>]*\bid="slide-(\d+)"[^>]*aria-label="\d+\. ([^"]*)"[^>]*>.*?</section>', re.S)
BLOCK = re.compile(r'<div class="(?:references|refx)">.*?</div></div>(?=<div class="sr-only">)', re.S)
GROUPS = [("Scientific", "Scientific references"), ("Data & online", "Data and online sources"), ("Images", "Image references")]

STYLE = """<style id="ref-cards-style">
.refx h1{position:absolute;left:110px;top:96px;margin:0;font-size:68px;font-weight:400;line-height:1.1;color:#F1F5F5}
.refx .rx-pg{position:absolute;right:110px;top:122px;font-size:22px;color:#84919D}
.refx .rx-tabs{position:absolute;left:110px;top:196px;display:flex;gap:10px;font-size:20px}
.refx .rx-tabs button{font:inherit;padding:7px 16px;border-radius:999px;border:1px solid #23262d;background:none;color:#84919D;cursor:pointer}
.refx .rx-tabs button:hover{color:#F1F5F5;border-color:#3a3f49}
.refx .rx-tabs button.cur{color:#050506;background:#B49AD8;border-color:#B49AD8;font-weight:500}
.refx .rx-grid{position:absolute;left:110px;right:90px;top:290px;bottom:110px;padding-right:20px;display:grid;grid-template-columns:1fr 1fr;column-gap:80px;row-gap:40px;align-content:start;overflow-y:auto;scrollbar-width:thin;scrollbar-color:#3a3f49 transparent}
.refx .rx-grid h2{grid-column:1/-1;margin:14px 0 -12px;font-size:24px;font-weight:500;color:#B49AD8}
.refx .rc{display:grid;grid-template-columns:52px 1fr;opacity:0;transform:translateY(14px)}
.slide.active .refx .rc{animation:rx-up .6s var(--d) forwards}
@keyframes rx-up{to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce),print{.refx .rc{opacity:1;transform:none;animation:none!important}}
.refx .rc .n{font-size:22px;color:#B49AD8;font-weight:500;padding-top:3px}
.refx .rc p{margin:0}
.refx .au{font-size:25px;font-weight:500;color:#F1F5F5;line-height:1.3}.refx .au b{font-weight:400;color:#64DFFF;margin-left:6px}
.refx .ti{font-size:21px;line-height:1.38;color:#c3c0cb;margin-top:6px!important}
.refx .ve{font-size:18px;color:#84919D;margin-top:6px!important;line-height:1.35}
.refx .lk{display:inline-block;margin-top:8px;font-size:17px;color:#64DFFF;text-decoration:none;border-bottom:1px solid rgba(100,223,255,.3);max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
</style>"""

CUR = ' class="cur"'
VE = '<p class="ve">{}</p>'
strip = lambda h: re.sub(r'<[^>]+>', '', h)


def parse(inner):
    m = re.match(r'\s*\[(\d+)\]\s*(.*)', inner, re.S)
    num, rest = m[1], m[2].strip()
    link = re.search(r'<a href="([^"]+)"[^>]*>(.*?)</a>', rest)
    url = link[1] if link else ""
    rest = re.sub(r'<a [^>]*>.*?</a>', '', rest)
    rest = re.sub(r'(?:https?://\S+)', '', rest)
    rest = re.sub(r'\s*Accessed:?\s*(?:[A-Z][a-z]+\.?\s*\d{1,2},?\s*\d{4}|\d{1,2}\s+[A-Z][a-z]+\s+\d{4})\.?', '', rest)
    rest = re.sub(r'\s*\(accessed [^)]*\)\.?', '', rest)
    rest = re.sub(r'\[Online(?: Video)?\]\.?|Available:?', '', rest).strip(' .,')
    year = re.search(r'\((\d{4})\)\.?', rest)
    if year:
        rest = rest.replace(year[0], '').replace('  ', ' ')
    t = re.search(r'“(.*?),?”', rest)
    if t:
        authors, title, venue = rest[:t.start()].strip(' ,'), t[1].strip(' ,.'), rest[t.end():].strip(' ,.')
    elif '<em>' in rest and re.match(r'[^<]*,\s*<em>', rest):
        mm = re.match(r'(.*?),\s*<em>(.*?)</em>\.?\s*(.*)', rest, re.S)
        authors, title, venue = mm[1], mm[2], mm[3].strip(' ,.')
    else:
        parts = re.split(r'\.\s+', rest, maxsplit=1)
        authors, title, venue = parts[0], (parts[1] if len(parts) > 1 else ""), ""
    yr = year[1] if year else (re.findall(r'(?:19|20)\d\d', strip(venue)) or [""])[-1]
    if url.startswith("https://doi.org/"):
        label = "doi " + url[len("https://doi.org/"):]
    elif url:
        label = re.sub(r'^https?://(www\.)?', '', url).rstrip('/')
    else:
        label = ""
    return num, authors, yr, title.strip(' .'), venue, url, label


def entries(block):
    """[(kind, payload)] from either the original <p>/<h2> list or our own cards."""
    out = []
    for m in re.finditer(r'<h2>(.*?)</h2>|<p class="editable" (data-edit="[^"]*")>(.*?)</p>|<article class="rc[^"]*"[^>]*(data-edit="[^"]*")[^>]*data-raw="([^"]*)"', block, re.S):
        if m[1] is not None:
            out.append(("h", m[1]))
        elif m[3] is not None:
            out.append(("p", (m[2], m[3])))
        else:
            out.append(("p", (m[4], html.unescape(m[5]))))
    return out


def render(title, page, total, items, firsts):
    group = next(i for i, (_, prefix) in enumerate(GROUPS) if title.startswith(prefix))
    tabs = "".join(f'<button type="button" data-goto="{firsts[i]}"{CUR if i == group else ""}>{html.escape(lbl)}</button>'
                   for i, (lbl, _) in enumerate(GROUPS))
    cards, k = "", 0
    for kind, val in items:
        if kind == "h":
            cards += f"<h2>{val}</h2>"
            continue
        edit, inner = val
        num, au, yr, ti, ve, url, label = parse(inner)
        link = f'<a class="lk" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(label)}</a>' if url else ""
        cards += (f'<article class="rc" {edit} data-raw="{html.escape(inner, quote=True)}" style="--d:{min(k, 10) * 0.07 + .15:.2f}s">'
                  f'<span class="n">{num}</span><div><p class="au">{au}{f" <b>{yr}</b>" if yr else ""}</p>'
                  f'<p class="ti">{ti}</p>{VE.format(ve) if ve else ""}{link}</div></article>')
        k += 1
    return (f'<div class="refx">{STYLE}<h1>References</h1><div class="rx-pg">{page} / {total}</div><div class="rx-tabs">{tabs}</div>'
            f'<div class="rx-grid reference-scroll" tabindex="0" role="region" aria-label="References">{cards}</div></div>')


def main():
    document = DECK.read_text()
    refs = [(int(m[1]), html.unescape(m[2])) for m in SECTION.finditer(document)
            if any(html.unescape(m[2]).startswith(p) for _, p in GROUPS)]
    firsts = [next(n for n, t in refs if t.startswith(p)) for _, p in GROUPS]
    pages = {n: (i + 1, t) for i, (n, t) in enumerate(refs)}

    def replace(m):
        n = int(m[1])
        if n not in pages:
            return m[0]
        page, title = pages[n]
        sec = m[0]
        block = BLOCK.search(sec)
        new = render(title, page, len(refs), entries(block[0]), firsts)
        return sec[:block.start()] + new + sec[block.end():]

    document = SECTION.sub(replace, document)
    DECK.write_text(document)
    print(f"Restyled {len(refs)} reference slides: {[n for n, _ in refs]}")


if __name__ == "__main__":
    main()
