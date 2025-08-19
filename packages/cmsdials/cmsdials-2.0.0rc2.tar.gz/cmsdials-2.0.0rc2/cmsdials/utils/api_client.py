import sys
from importlib import util as importlib_util
from traceback import format_exc
from typing import Any, Generic, Optional, Union
from warnings import warn

import requests
from pydantic import AnyUrl
from requests import Response, Session
from requests.adapters import DEFAULT_RETRIES, HTTPAdapter
from requests.exceptions import HTTPError
from urllib3.util import Retry

from .._version import __version__
from ..auth._base import BaseCredentials
from ..utils.logger import logger
from .base_model import TCleanableFilterClass, TDataModel, TPaginatedFilterClass, TPaginationModel


if importlib_util.find_spec("tqdm"):
    from tqdm.auto import tqdm

    TQDM_INSTALLED = True
else:
    TQDM_INSTALLED = False


class BaseAPIClient:
    PRODUCTION_BASE_URL = "https://cmsdials-api.web.cern.ch/"
    PRODUCTION_API_ROUTE = "api/"
    PRODUCTION_API_VERSION = "v1/"

    def __init__(
        self, base_url: Optional[str] = None, route: Optional[str] = None, version: Optional[str] = None
    ) -> None:
        self.base_url = self.__endswithslash(base_url or self.PRODUCTION_BASE_URL)
        self.route = self.__endswithslash(route or self.PRODUCTION_API_ROUTE)
        self.version = self.__endswithslash(version or self.PRODUCTION_API_VERSION)

    @staticmethod
    def __endswithslash(value: str) -> str:
        if value.endswith("/") is False:
            return value + "/"
        return value

    @classmethod
    def _requests_get_retriable(cls, *args, retries: Union[int, Retry] = DEFAULT_RETRIES, **kwargs) -> Response:
        """
        requests.get() with an additional `retries` parameter.

        Specify retries=<number of attempts - 1> for simple use cases.
        For advanced usage, see https://docs.python-requests.org/en/latest/user/advanced/
        """
        with Session() as s:
            s.mount(cls.PRODUCTION_BASE_URL, HTTPAdapter(max_retries=retries))
            ret = s.get(*args, **kwargs)
        return ret

    @staticmethod
    def _build_user_agent():
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        req_version = requests.__version__
        return f"dials-py/{__version__} (python/{py_version}, python-requests/{req_version})"

    @property
    def api_url(self):
        return self.base_url + self.route + self.version


class BaseAuthorizedAPIClient(BaseAPIClient, Generic[TDataModel]):
    data_model: type[TDataModel]
    lookup_url: str
    default_timeout = 30  # seconds

    def __init__(
        self,
        creds: BaseCredentials,
        workspace: Optional[str] = None,
        *args: str,
        **kwargs: str,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.creds = creds
        self.workspace = workspace

    def _build_headers(self) -> dict:
        """
        This is a base method and should not be accesed directly.
        """
        base = {"Accept": "application/json", "User-Agent": self._build_user_agent()}
        if self.workspace is not None:
            base["Workspace"] = self.workspace
        self.creds.before_request(base)
        return base

    def _authorized_get(
        self,
        url: str,
        params: Optional[dict] = None,
        retries: Union[int, Retry] = DEFAULT_RETRIES,
    ) -> Response:
        """
        This is a base method and should not be accesed directly.
        """
        headers = self._build_headers()
        response = self._requests_get_retriable(
            url,
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

        return response

    def _get(
        self,
        edp: str,
        params: Optional[dict[str, Any]] = None,
        retries: Union[int, Retry] = DEFAULT_RETRIES,
        return_raw_json: bool = False,
    ) -> TDataModel:
        """
        This is a base method and should not be accesed directly.
        Each client should define its own `get` method.
        """
        endpoint_url = self.api_url + self.lookup_url + edp
        response = self._authorized_get(url=endpoint_url, retries=retries, params=params)
        data = response.json()
        if return_raw_json:
            return data
        return self.data_model(**data)


class BaseAuthorizedNonPaginatedAPIClient(
    BaseAuthorizedAPIClient,
    Generic[TDataModel, TCleanableFilterClass],
):
    filter_class: type[TCleanableFilterClass]

    def list(
        self, filters: Optional[TCleanableFilterClass] = None, retries: Union[int, Retry] = DEFAULT_RETRIES
    ) -> list[TDataModel]:
        endpoint_url = self.api_url + self.lookup_url
        filters = filters or self.filter_class()
        response = self._authorized_get(url=endpoint_url, retries=retries, params=filters.cleandict())
        data = response.json()
        return [self.data_model(**res) for res in data]


class BaseAuthorizedPaginatedAPIClient(
    BaseAuthorizedAPIClient,
    Generic[TDataModel, TPaginationModel, TPaginatedFilterClass],
):
    pagination_model: type[TPaginationModel]
    filter_class: type[TPaginatedFilterClass]

    def list(
        self, filters: Optional[TPaginatedFilterClass] = None, retries: Union[int, Retry] = DEFAULT_RETRIES
    ) -> TPaginationModel:
        endpoint_url = self.api_url + self.lookup_url
        filters = filters or self.filter_class()
        response = self._authorized_get(url=endpoint_url, retries=retries, params=filters.cleandict())
        data = response.json()
        return self.pagination_model(**data)

    def list_all(
        self,
        filters,
        max_pages: Optional[int] = None,
        enable_progress: bool = False,
        retries: Union[int, Retry] = DEFAULT_RETRIES,
        keep_failed: bool = False,
        resume_from=None,
    ) -> TPaginationModel:
        next_string: Optional[AnyUrl] = None
        results = []
        is_last_page = False

        if resume_from is not None:
            results = resume_from.results
            next_string = resume_from.next
            if next_string is None and len(results):
                warn(
                    "resume_from.next is None while resume_from.result is not empty, doing nothing.",
                    RuntimeWarning,
                    stacklevel=2,
                )
                is_last_page = True

        total_pages = 0
        use_tqdm = TQDM_INSTALLED and enable_progress

        if use_tqdm:
            progress = tqdm(desc="Progress", total=1)

        while is_last_page is False:
            next_token = dict(next_string.query_params()).get("next_token") if next_string else None
            curr_filters = self.filter_class(**filters.model_dump())
            curr_filters.next_token = next_token
            try:
                response = self.list(curr_filters, retries=retries)
            except Exception as e:  # noqa: BLE001
                if use_tqdm:
                    progress.close()

                if not keep_failed:
                    raise e

                exc_formatted = format_exc()
                warn(
                    "HTTP request failed, returning partial results. Exception: " + exc_formatted,
                    RuntimeWarning,
                    stacklevel=2,
                )
                return self.pagination_model(
                    next=next_string,
                    previous=None,
                    results=results,
                    exc_type=e.__class__.__name__,
                    exc_formatted=exc_formatted,
                )

            results.extend(response.results)
            next_string = response.next
            is_last_page = next_string is None
            total_pages += 1
            max_pages_reached = max_pages and total_pages >= max_pages
            if use_tqdm:
                if is_last_page or max_pages_reached:
                    progress.update()
                else:
                    progress.total = total_pages + 1
                    progress.update(1)
            if max_pages_reached:
                break

        if use_tqdm:
            progress.close()

        return self.pagination_model(
            next=next_string,
            previous=None,
            results=results,
        )
