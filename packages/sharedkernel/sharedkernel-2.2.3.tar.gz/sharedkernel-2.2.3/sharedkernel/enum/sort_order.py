from enum import Enum


class SortOrder(str, Enum):
    Descending = "desc"
    Ascending = "asc"