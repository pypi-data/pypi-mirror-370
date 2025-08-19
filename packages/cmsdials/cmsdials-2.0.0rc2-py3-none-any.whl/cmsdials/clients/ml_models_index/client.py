from ...utils.api_client import BaseAuthorizedPaginatedAPIClient
from .models import MLModelsIndex, MLModelsIndexFilters, PaginatedMLModelsIndexList


class MLModelsIndexClient(
    BaseAuthorizedPaginatedAPIClient[
        MLModelsIndex,
        PaginatedMLModelsIndexList,
        MLModelsIndexFilters,
    ]
):
    data_model = MLModelsIndex
    pagination_model = PaginatedMLModelsIndexList
    filter_class = MLModelsIndexFilters
    lookup_url = "ml-models-index/"

    def get(self, model_id: int, **kwargs):
        edp = f"{model_id}/"
        return super()._get(edp, **kwargs)
