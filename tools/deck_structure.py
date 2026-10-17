"""Map the source PPTX to the web deck, which omits the personal introduction."""
import re


def display_number(source_number):
    if source_number == 2:
        raise ValueError('The personal introduction is excluded from the web deck')
    return source_number - (source_number > 2)


def web_section(section, source_number):
    number = display_number(source_number)
    section = section.replace(f'id="slide-{source_number}"', f'id="slide-{number}"', 1)
    section = section.replace(f'aria-label="{source_number}. ', f'aria-label="{number}. ', 1)
    section = re.sub(r'data-goto="(\d+)"',
                     lambda m: f'data-goto="{display_number(int(m[1]))}"', section)
    section = section.replace(f'<span>{source_number:02d} / 51</span>',
                              f'<span>{number:02d} / 50</span>')
    if source_number == 3:
        section = re.sub(r'<small>(\d+) →</small>',
                         lambda m: f'<small>{display_number(int(m[1])):02d} →</small>', section)
        section = re.sub(r'Page (\d+)',
                         lambda m: f'Page {display_number(int(m[1])):02d}', section)
    return section


def write_transcript(path, data):
    text = '# Stereolithographic Bioprinting\n\n50 slides · 15 October 2026\n\n'
    for slide in data:
        text += f'## {slide["number"]:02d}. {slide["title"]}\n\n{slide["text"]}\n\n'
        if slide['notes']:
            text += '### Speaker notes\n\n' + slide['notes'] + '\n\n'
    path.write_text('\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n')
