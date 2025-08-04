from PyPDF2 import PdfReader
import fitz
import logging
import tempfile
import requests
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

def load_doc(file_path, is_pdf):
    try:
        if not is_pdf:
            if file_path.startswith("http"):
                response = requests.get(file_path)
                response.raise_for_status()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name
            else:
                tmp_path = file_path
            doc = fitz.open(tmp_path)
        else:
            doc = fitz.open(file_path)
    except Exception as e:
        logger.error(f"Error loading document: {e}")
        return ""
    
    return doc

def load_text(doc):
    return "\n".join([page.get_text() for page in doc])


# --- not in use ---

def load_and_split_pages(source, is_pdf):
    doc = load_doc(source, is_pdf)
    return ""

def load_pdf_and_split_sections(file_path, is_pdf):
    
    doc = load_doc(file_path, is_pdf)

    sections = defaultdict(str)
    current_section = "Untitled"
    rolling_avg = 15
    alpha = 0.01

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for line in b["lines"]:
                line_text = ""
                font_sizes = []
                for span in line["spans"]:
                    text = span["text"].strip()
                    size = span["size"]
                    if text:
                        line_text += text + " "
                        font_sizes.append(size)

                if not font_sizes or not line_text.strip():
                    continue

                avg_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0
                rolling_avg = (1 - alpha) * rolling_avg + alpha * avg_size

                candidate = line_text.strip()
                if avg_size > rolling_avg and len(candidate) < 20:
                    if is_probably_section_title(candidate):
                        current_section = clean_title(candidate)
                        if current_section not in sections:
                            sections[current_section] = ""
                else:
                    if len(candidate) > 3:
                        sections[current_section] += candidate + "\n"

    doc.close()
    return dict(sections)
                        

def is_probably_section_title(text):
    # Reject if mostly numeric or matches patterns like "2", "2.1", "3.4.2"
    return not re.fullmatch(r"\d+(\.\d+)*", text.strip())

def clean_title(text):
    return re.sub(r'[^A-Za-z0-9\- ]+', '', text).strip().title()

def is_bold_font(span):
    return "bold" in span["font"].lower()
