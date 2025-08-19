import warnings
from typing import Union

from requests.adapters import DEFAULT_RETRIES
from urllib3.util import Retry

from ...utils.api_client import BaseAuthorizedNonPaginatedAPIClient
from .models import MEFilters, MonitoringElement


class MonitoringElementClient(
    BaseAuthorizedNonPaginatedAPIClient[
        MonitoringElement,
        MEFilters,
    ]
):
    data_model = MonitoringElement
    filter_class = MEFilters
    lookup_url = "mes/"

    def get(self, id: int, **kwargs):  # noqa: A002
        edp = f"{id}/"
        return super()._get(edp, **kwargs)

    def list_all(self, filters: MEFilters, retries: Union[int, Retry] = DEFAULT_RETRIES, **kwargs):
        """
        This method is here just for the sake of compatibility.
        In the past, this class and other paginated classes used to inherit from the same class.
        """
        warnings.warn(
            "The `list_all` method is deprecated and will be removed in the future for non-paginated classes. "
            "Please use the `list` method instead.",
            DeprecationWarning,
            stacklevel=2,  # Important: ensures the warning points to the caller
        )
        return super().list(filters, retries=retries, **kwargs)
