from importlib import util as importlib_util
from typing import Generic, Optional, TypeVar

from pydantic import AnyUrl, BaseModel


if importlib_util.find_spec("pandas"):
    import pandas as pd

    PANDAS_NOT_INSTALLED = False
else:
    PANDAS_NOT_INSTALLED = True


TDataModel = TypeVar("TDataModel", bound=BaseModel)


class PaginatedBaseModel(BaseModel, Generic[TDataModel]):
    next: Optional[AnyUrl]
    previous: Optional[AnyUrl]
    results: list[TDataModel]
    exc_type: Optional[str] = None
    exc_formatted: Optional[str] = None

    def to_pandas(self):
        if PANDAS_NOT_INSTALLED:
            raise RuntimeError(
                "The 'pandas' package is not installed, you can re-install cmsdials specifying the pandas extra: pip install cmsdials[pandas]"
            )
        return pd.DataFrame([res.__dict__ for res in self.results])


class CleanableBaseModel(BaseModel):
    def cleandict(self):
        return {
            key: ",".join(str(v) for v in value) if isinstance(value, (list, tuple)) else value
            for key, value in self.model_dump().items()
            if value is not None
        }


class PaginatedBaseFilters(CleanableBaseModel):
    next_token: Optional[str] = None
    page_size: Optional[int] = None


TPaginationModel = TypeVar("TPaginationModel", bound=PaginatedBaseModel)
TCleanableFilterClass = TypeVar("TCleanableFilterClass", bound=CleanableBaseModel)
TPaginatedFilterClass = TypeVar("TPaginatedFilterClass", bound=PaginatedBaseFilters)
