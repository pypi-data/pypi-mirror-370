from typing import List, TypeVar, Generic

from pydantic import BaseModel
# from pydantic.generics import GenericModel

T = TypeVar("T", bound=BaseModel)

class PaginationResponseDto(BaseModel, Generic[T]):
    data: List[T]
    total_items: int
    page_size: int
    current_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

