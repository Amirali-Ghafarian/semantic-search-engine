from dataclasses import dataclass

from app.ingestion.pdf_loader import ExtractedPage


@dataclass(slots=True)
class TextChunk:
    document_id: str
    filename: str
    page_number: int
    chunk_order: int
    text: str


def chunk_pages(
    pages: list[ExtractedPage],
    *,
    document_id: str,
    filename: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be between 0 and chunk_size - 1.")

    step = chunk_size - chunk_overlap
    chunks: list[TextChunk] = []
    chunk_order = 0

    for page in pages:
        words = page.text.split()
        for start in range(0, len(words), step):
            window = words[start : start + chunk_size]
            if not window:
                continue
            chunk_order += 1
            chunks.append(
                TextChunk(
                    document_id=document_id,
                    filename=filename,
                    page_number=page.page_number,
                    chunk_order=chunk_order,
                    text=" ".join(window),
                )
            )
            if start + chunk_size >= len(words):
                break

    return chunks