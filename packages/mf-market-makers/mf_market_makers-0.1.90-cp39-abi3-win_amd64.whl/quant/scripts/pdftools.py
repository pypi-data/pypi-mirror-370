from pypdf import PdfReader
from pathlib import Path

def pdf_to_txt(pdf_in: Path, txt_out: Path):
    reader = PdfReader(pdf_in)
    with open(txt_out, "wb") as out:
        for page in reader.pages:
            txt = page.extract_text(extraction_mode="layout", layout_mode_vertically = False)
            out.write(txt.encode("utf-8"))
