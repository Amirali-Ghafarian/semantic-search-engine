import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

from app.ingestion.chunker import TextChunk


@dataclass(slots=True)
class ChunkMetadata:
    chunk_id: int
    document_id: str
    filename: str
    page_number: int
    chunk_order: int
    text: str


class MetadataStore:
    def __init__(self, records: list[ChunkMetadata] | None = None) -> None:
        self.records = records or []

    def add_chunks(self, chunks: Sequence[TextChunk]) -> None:
        start_id = len(self.records)
        for offset, chunk in enumerate(chunks):
            self.records.append(
                ChunkMetadata(
                    chunk_id=start_id + offset,
                    document_id=chunk.document_id,
                    filename=chunk.filename,
                    page_number=chunk.page_number,
                    chunk_order=chunk.chunk_order,
                    text=chunk.text,
                )
            )

    def get(self, chunk_id: int) -> ChunkMetadata | None:
        if 0 <= chunk_id < len(self.records):
            return self.records[chunk_id]
        return None

    def save(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as file:
            json.dump([asdict(record) for record in self.records], file, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, source: Path) -> "MetadataStore":
        if not source.exists():
            return cls()

        with source.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        records = [ChunkMetadata(**item) for item in payload]
        return cls(records=records)