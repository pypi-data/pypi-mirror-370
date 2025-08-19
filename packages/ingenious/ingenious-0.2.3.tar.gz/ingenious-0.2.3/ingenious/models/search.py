from typing import Any, Dict, List

from pydantic import BaseModel


class SearchQuery(BaseModel):
    query: str
    top: int


class SearchResult(BaseModel):
    results: List[Dict[str, Any]]
