import re

def split_sections(text):

    sections = {}
    pattern = re.compile(
        r'(?i)(abstract|introduction|preliminaries|background|methods?|data?|datasets?|approach|experiment?|implementation?|results?|evaluation?|discussion|conclusion?|references?|figures|tables|images|videos|audio|other)',
          re.MULTILINE)
    
    lines = text.splitlines()
    current_section = "title"
    sections[current_section] = []

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        match = pattern.fullmatch(clean_line.lower())
        if match:
            current_section = match.group(0).capitalize()
            if current_section not in sections:
                sections[current_section] = []
        sections[current_section].append(clean_line)

    return {k: "\n".join(v) for k, v in sections.items()}

