"""Source and web slide numbers match; introduction restored at user request."""
from opening_slides import settings


def display_number(source_number):
    return 3 - source_number if source_number <= 2 else source_number


def web_section(section, source_number):
    number = display_number(source_number)
    return section.replace(f'id="slide-{source_number}"', f'id="slide-{number}"', 1).replace(f'aria-label="{source_number}. ', f'aria-label="{number}. ', 1)


def write_transcript(path, data):
    text = f'# 3D Bioprinting\n\n{len(data)} slides · ' + settings()['event']['date'] + '\n\n'
    for slide in data:
        text += f'## {slide["number"]:02d}. {slide["title"]}\n\n{slide["text"]}\n\n'
        if slide['notes']:
            text += '### Speaker notes\n\n' + slide['notes'] + '\n\n'
    path.write_text('\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n')
