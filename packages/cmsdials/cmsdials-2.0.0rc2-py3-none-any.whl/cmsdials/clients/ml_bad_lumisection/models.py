from typing import Optional

from pydantic import BaseModel

from ...utils.base_model import PaginatedBaseFilters, PaginatedBaseModel


class MLBadLumisection(BaseModel):
    model_id: int
    dataset_id: int
    file_id: int
    run_number: int
    ls_number: int
    metric_value: float


class PaginatedMLBadLumisectionList(PaginatedBaseModel[MLBadLumisection]):
    pass


class MLBadLumisectionFilters(PaginatedBaseFilters):
    model_id: Optional[int] = None
    model_id__in: Optional[list[int]] = None
    dataset_id: Optional[int] = None
    dataset_id__in: Optional[list[int]] = None
    dataset: Optional[str] = None
    dataset__regex: Optional[str] = None
    me_id: Optional[int] = None
    me: Optional[str] = None
    me__regex: Optional[str] = None
    run_number: Optional[int] = None
    run_number__in: Optional[list[int]] = None
    ls_number: Optional[int] = None
