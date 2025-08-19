from ...utils.api_client import BaseAuthorizedPaginatedAPIClient
from .models import PaginatedRunList, Run, RunFilters


class RunClient(
    BaseAuthorizedPaginatedAPIClient[
        Run,
        PaginatedRunList,
        RunFilters,
    ]
):
    data_model = Run
    pagination_model = PaginatedRunList
    filter_class = RunFilters
    lookup_url = "run/"

    def get(self, dataset_id: int, run_number: int, **kwargs):
        edp = f"{dataset_id}/{run_number}/"
        return super()._get(edp, **kwargs)
