"""Source and web slide numbers match; introduction restored at user request."""
from opening_slides import settings


def display_number(source_number):
    return source_number


def web_section(section, source_number):
    return section


def write_transcript(path, data):
    text = '# Stereolithographic Bioprinting\n\n51 slides · ' + settings()['event']['date'] + '\n\n'
    for slide in data:
        text += f'## {slide["number"]:02d}. {slide["title"]}\n\n{slide["text"]}\n\n'
        if slide['notes']:
            text += '### Speaker notes\n\n' + slide['notes'] + '\n\n'
    path.write_text('\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n')
