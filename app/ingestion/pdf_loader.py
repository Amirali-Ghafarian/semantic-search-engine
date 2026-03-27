from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ExtractedPage:
    page_number: int
    text: str


def load_pdf(pdf_path: Path) -> list[ExtractedPage]:
    import fitz

    pages: list[ExtractedPage] = []
    with fitz.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = " ".join(page.get_text("text").split())
            if text:
                pages.append(ExtractedPage(page_number=page_number, text=text))
    return pages