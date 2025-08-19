from ...utils.api_client import BaseAuthorizedPaginatedAPIClient
from .models import LumisectionHistogram1D, LumisectionHistogram1DFilters, PaginatedLumisectionHistogram1DList


class LumisectionHistogram1DClient(
    BaseAuthorizedPaginatedAPIClient[
        LumisectionHistogram1D,
        PaginatedLumisectionHistogram1DList,
        LumisectionHistogram1DFilters,
    ]
):
    data_model = LumisectionHistogram1D
    pagination_model = PaginatedLumisectionHistogram1DList
    filter_class = LumisectionHistogram1DFilters
    lookup_url = "th1/"

    def get(self, dataset_id: int, run_number: int, ls_number: int, me_id: int, **kwargs):
        edp = f"{dataset_id}/{run_number}/{ls_number}/{me_id}/"
        return super()._get(edp, **kwargs)
