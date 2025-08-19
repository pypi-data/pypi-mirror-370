from pydantic import BaseModel, Field
from typing import Optional, Union, List


class VectorSearchInput(BaseModel):
    query_text: str
    top_k: Optional[int] = Field(
        default=5, 
        ge=1, 
        le=10, 
        description="Number of results to return (1-10, default: 5). Lower values prevent memory overload."
    )
    year_filter: Optional[Union[int, List[int]]] = Field(
        default=None,
        description="Filter by specific year(s). Can be a single year (e.g., 2023) or list of years (e.g., [2004, 2008, 2024])"
    )
    year_range_start: Optional[int] = Field(
        default=None,
        description="Start year for range filter (inclusive). Use with year_range_end."
    )
    year_range_end: Optional[int] = Field(
        default=None,
        description="End year for range filter (inclusive). Use with year_range_start."
    )
    category_filter: Optional[str] = Field(
        default=None,
        description="Filter by product category (e.g., 'liquido', 'otro', 'powder')"
    )
    study_type_filter: Optional[str] = Field(
        default=None,
        description="Filter by study type (e.g., 'estudio cualitativo', 'ad tracking', 'cuas', 'estudio de mercado','panel consumidores', 'brand tracking', 'otro')"
    )
