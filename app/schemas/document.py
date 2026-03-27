from pydantic import BaseModel


class UploadedDocumentSummary(BaseModel):
    document_id: str
    filename: str
    page_count: int
    chunk_count: int