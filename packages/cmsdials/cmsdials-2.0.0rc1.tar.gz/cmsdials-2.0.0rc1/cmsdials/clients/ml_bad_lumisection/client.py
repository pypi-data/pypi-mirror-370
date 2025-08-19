from ...utils.api_client import BaseAuthorizedPaginatedAPIClient
from .models import MLBadLumisection, MLBadLumisectionFilters, PaginatedMLBadLumisectionList


class MLBadLumisectionClient(
    BaseAuthorizedPaginatedAPIClient[
        MLBadLumisection,
        PaginatedMLBadLumisectionList,
        MLBadLumisectionFilters,
    ]
):
    data_model = MLBadLumisection
    pagination_model = PaginatedMLBadLumisectionList
    filter_class = MLBadLumisectionFilters
    lookup_url = "ml-bad-lumisection/"

    def get(self, model_id: int, dataset_id: int, run_number: int, ls_number: int, me_id: int, **kwargs):
        edp = f"{model_id}/{dataset_id}/{run_number}/{ls_number}/{me_id}/"
        return super()._get(edp, **kwargs)

    def __json_params_builder(
        self, model_id__in: list[int], dataset_id__in: list[int], run_number__in: list[int], **kwargs
    ):
        midin = ",".join(str(v) for v in model_id__in)
        didin = ",".join(str(v) for v in dataset_id__in)
        ridin = ",".join(str(v) for v in run_number__in)
        return {"model_id__in": midin, "dataset_id__in": didin, "run_number__in": ridin}

    def cert_json(self, model_id__in: list[int], dataset_id__in: list[int], run_number__in: list[int], **kwargs):
        edp = "cert-json/"
        params = self.__json_params_builder(
            model_id__in=model_id__in, dataset_id__in=dataset_id__in, run_number__in=run_number__in
        )
        return super()._get(edp, params=params, return_raw_json=True, **kwargs)

    def golden_json(self, model_id__in: list[int], dataset_id__in: list[int], run_number__in: list[int], **kwargs):
        edp = "golden-json/"
        params = self.__json_params_builder(
            model_id__in=model_id__in, dataset_id__in=dataset_id__in, run_number__in=run_number__in
        )
        return super()._get(edp, params=params, return_raw_json=True, **kwargs)
