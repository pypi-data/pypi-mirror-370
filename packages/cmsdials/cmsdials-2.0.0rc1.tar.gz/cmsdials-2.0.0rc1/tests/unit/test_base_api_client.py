import sys

import requests

from cmsdials import __version__
from cmsdials.utils.api_client import BaseAPIClient


def test_user_agent():
    ua = BaseAPIClient._build_user_agent()
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    req_version = requests.__version__
    assert (
        "dials-py/" in ua
        and __version__ in ua
        and "python/" in ua
        and py_version in ua
        and "python-requests/" in ua
        and req_version in ua
    )
