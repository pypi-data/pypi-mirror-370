from typing import Optional

from pydantic import BaseModel, Field

from ...utils.base_model import CleanableBaseModel


class MonitoringElement(BaseModel):
    me_id: int
    me: str = Field(..., max_length=255)
    count: int
    dim: int


class MEFilters(CleanableBaseModel):
    me: Optional[str] = None
    me__regex: Optional[str] = None
    dim: Optional[int] = None
