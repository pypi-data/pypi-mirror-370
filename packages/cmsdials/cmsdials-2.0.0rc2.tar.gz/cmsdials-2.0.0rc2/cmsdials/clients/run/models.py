from typing import Optional

from pydantic import BaseModel, Field

from ...utils.base_model import PaginatedBaseFilters, PaginatedBaseModel


class Run(BaseModel):
    dataset_id: int
    dataset: str = Field(..., max_length=255)
    run_number: int
    ls_count: int


class PaginatedRunList(PaginatedBaseModel[Run]):
    pass


class RunFilters(PaginatedBaseFilters):
    dataset_id: Optional[int] = None
    run_number: Optional[int] = None
    run_number__lte: Optional[int] = None
    run_number__gte: Optional[int] = None
    dataset: Optional[str] = None
    dataset__regex: Optional[str] = None
