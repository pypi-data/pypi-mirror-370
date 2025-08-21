import requests
from dataclasses import dataclass
from typing import Optional

import simplex.core.error.handling

import simplex.core.error

import simplex.core
import simplex
@dataclass
class FetchStringResult:
    text: str
    error: Optional[Exception] = None


def fetch_string(
    url: str,
    token: Optional[str] = None,
    request_data: Optional[str] = None,
    content_type: str = "application/json",
    verify_ssl: bool = True,
    timeout: int = 60
) -> FetchStringResult:
    """
    Send a POST (or GET) request with optional data and bearer token.
    Returns text content and any exception.
    """
    headers = {
        "Accept": "*/*",
        "Connection": "close"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if request_data is not None:
        headers["Content-Type"] = content_type
        method = "POST"
    else:
        method = "GET"

    try:
        response = requests.request(
            method=method,
            url=url,
            data=request_data,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl  # False means allow self-signed certs
        )
        response.raise_for_status()
        return FetchStringResult(text=response.text)

    except requests.RequestException as e:
        raise Exception(f"{simplex.core.error.handling.RED}Request failed: {e}{simplex.core.error.handling.RESET}") from e