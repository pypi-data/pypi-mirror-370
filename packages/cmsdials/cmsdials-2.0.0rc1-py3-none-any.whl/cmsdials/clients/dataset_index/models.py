from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ...utils.base_model import PaginatedBaseFilters, PaginatedBaseModel


class DatasetIndex(BaseModel):
    dataset_id: int
    dataset: str = Field(..., max_length=255)
    era: str = Field(..., max_length=255)
    data_tier: str = Field(..., max_length=255)
    primary_ds_name: str = Field(..., max_length=255)
    processed_ds_name: str = Field(..., max_length=255)
    processing_version: int
    last_modification_date: datetime


class PaginatedDatasetIndexList(PaginatedBaseModel[DatasetIndex]):
    pass


class DatasetIndexFilters(PaginatedBaseFilters):
    dataset: Optional[str] = None
    dataset__regex: Optional[str] = None
