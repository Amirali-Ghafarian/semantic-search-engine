from pydantic import BaseModel


class SearchResult(BaseModel):
    rank: int
    score: float
    filename: str
    page_number: int
    excerpt: str


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[SearchResult]