from typing import Any, List, Optional

from pydantic import BaseModel


class QueryResponse(BaseModel):
    items: List[Any]
    limit: Optional[int] = None
    offset: Optional[int] = None
