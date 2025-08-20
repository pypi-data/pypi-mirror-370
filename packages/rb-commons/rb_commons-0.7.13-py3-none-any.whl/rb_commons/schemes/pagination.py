from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Pagination parameters for querying."""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=10, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", description="Sort order (asc/desc)")

class PaginationMeta(BaseModel):
    """Metadata for paginated responses."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: list[T] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        per_page: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response with calculated metadata."""
        total_pages = (total + per_page - 1) // per_page
        return cls(
            items=items,
            meta=PaginationMeta(
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1
            )
        )