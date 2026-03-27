from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.query import SearchQuery
from app.schemas.result import SearchResponse
from app.services.search_service import SearchService, get_search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search_documents(
    payload: SearchQuery,
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    try:
        return search_service.search(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc