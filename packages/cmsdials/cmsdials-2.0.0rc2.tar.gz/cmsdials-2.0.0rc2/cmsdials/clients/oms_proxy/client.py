from typing import Optional

from requests.adapters import DEFAULT_RETRIES
from requests.exceptions import HTTPError

from ...auth._base import BaseCredentials
from ...utils.api_client import BaseAPIClient
from ...utils.logger import logger
from .models import OMSFilter, OMSPage


class OMSProxyClient(BaseAPIClient):
    default_timeout = 30
    lookup_url = "oms-proxy/"

    def __init__(
        self,
        creds: BaseCredentials,
        *args: str,
        **kwargs: str,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.creds = creds

    def _build_headers(self) -> dict:
        base = {"Accept": "application/json", "User-Agent": self._build_user_agent()}
        self.creds.before_request(base)
        return base

    def query(
        self, endpoint: str, filters: list[OMSFilter], pages: Optional[list[OMSPage]] = None, retries=DEFAULT_RETRIES
    ):
        headers = self._build_headers()
        endpoint_url = self.api_url + self.lookup_url

        # Format filters
        _filters = {f"filter[{_filter.attribute_name}][{_filter.operator}]": _filter.value for _filter in filters}
        _pages = {f"page[{page.attribute_name}]": page.value for page in pages} if pages and len(pages) > 0 else {}
        params = {"endpoint": endpoint, **_filters, **_pages}

        response = self._requests_get_retriable(
            endpoint_url,
            headers=headers,
            params=params,
            timeout=self.default_timeout,
            retries=retries,
        )
        try:
            response.raise_for_status()
        except HTTPError as err:
            logger.info(f"Api raw response: {response.text}")
            raise err

        return response.json()
