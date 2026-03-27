from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    query: str = Field(min_length=1, description="The search phrase or keyword.")
    top_k: int | None = Field(default=None, ge=1, le=20, description="How many results to return.")