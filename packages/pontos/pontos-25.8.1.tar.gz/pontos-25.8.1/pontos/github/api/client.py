# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterator,
    Dict,
    Mapping,
    Optional,
    Type,
    Union,
)

import httpx

from pontos.github.api.helper import (
    DEFAULT_GITHUB_API_URL,
    DEFAULT_TIMEOUT_CONFIG,
    JSON,
    JSON_OBJECT,
    _get_next_url,
)
from pontos.github.models.base import GitHubModel

Headers = Mapping[str, str]
ParamValue = Union[str, None]
Params = Mapping[str, ParamValue]

# supported GitHub API version
# https://docs.github.com/en/rest/overview/api-versions
GITHUB_API_VERSION = "2022-11-28"
DEFAULT_ACCEPT_HEADER = "application/vnd.github+json"
ACCEPT_HEADER_OCTET_STREAM = "application/octet-stream"


class GitHubAsyncRESTClient(AbstractAsyncContextManager):
    """
    A client for calling the GitHub REST API asynchronously

    Should be used as an async context manager

    Example:
        .. code-block:: python

        org = "foo"
        async with GitHubAsyncRESTClient(token) as client:
            response = await client.get(f"/orgs/{org}/repos")
    """

    def __init__(
        self,
        token: Optional[str] = None,
        url: Optional[str] = DEFAULT_GITHUB_API_URL,
        *,
        timeout: Optional[httpx.Timeout] = DEFAULT_TIMEOUT_CONFIG,
    ) -> None:
        self.token = token
        self.url = url
        self._client = httpx.AsyncClient(timeout=timeout, http2=True)

    def _request_headers(
        self,
        *,
        accept: Optional[str] = None,
        content_type: Optional[str] = None,
        content_length: Optional[int] = None,
    ) -> Headers:
        """
        Get the default request headers
        """
        headers: Dict[str, str] = {
            "Accept": accept or DEFAULT_ACCEPT_HEADER,
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        if content_type:
            headers["Content-Type"] = content_type
        if content_length:
            headers["Content-Length"] = str(content_length)

        return headers

    def _request_kwargs(
        self, *, json: Optional[JSON] = None, content: Optional[Any] = None
    ) -> JSON:
        """
        Get the default request arguments
        """
        kwargs = {}
        if json is not None:
            kwargs["json"] = json
        if content is not None:
            kwargs["content"] = content
        return kwargs  # type: ignore

    def _request_api_url(self, api: str) -> str:
        return f"{self.url}{api}"

    def _request_url(self, api_or_url: str) -> str:
        return (
            api_or_url
            if api_or_url.startswith("https")
            else self._request_api_url(api_or_url)
        )

    async def get(
        self,
        api: str,
        *,
        params: Optional[Params] = None,
    ) -> httpx.Response:
        """
        Get request to a GitHub API

        Args:
            api: API path to use for the get request
            params: Optional params to use for the get request
        """
        url = self._request_url(api)
        headers = self._request_headers()
        kwargs = self._request_kwargs()
        return await self._client.get(  # type: ignore
            url,
            headers=headers,
            params=params,
            follow_redirects=True,
            **kwargs,
        )

    async def get_all(
        self,
        api: str,
        *,
        params: Optional[Params] = None,
    ) -> AsyncIterator[httpx.Response]:
        """
        Get paginated content of a get GitHub API request

        Args:
            api: API path to use for the get request
            params: Optional params to use for the get request
        """
        response = await self.get(api, params=params)

        yield response

        next_url = _get_next_url(response)

        while next_url:
            # Workaround for https://github.com/encode/httpx/issues/3433
            new_params = (
                httpx.URL(next_url).params.merge(params) if params else None
            )
            response = await self.get(next_url, params=new_params)

            yield response

            next_url = _get_next_url(response)

    async def delete(
        self, api: str, *, params: Optional[Params] = None
    ) -> httpx.Response:
        """
        Delete request to a GitHub API

        Args:
            api: API path to use for the delete request
            params: Optional params to use for the delete request
        """
        headers = self._request_headers()
        url = self._request_url(api)
        return await self._client.delete(url, params=params, headers=headers)

    async def post(
        self,
        api: str,
        *,
        data: Optional[JSON] = None,
        params: Optional[Params] = None,
        content: Optional[str] = None,
        content_type: Optional[str] = None,
        content_length: Optional[int] = None,
    ) -> httpx.Response:
        """
        Post request to a GitHub API

        Args:
            api: API path to use for the post request
            params: Optional params to use for the post request
            data: Optional data to include in the post request
        """
        headers = self._request_headers(
            content_type=content_type, content_length=content_length
        )
        url = self._request_url(api)
        return await self._client.post(
            url, params=params, headers=headers, json=data, content=content
        )

    async def put(
        self,
        api: str,
        *,
        data: Optional[JSON] = None,
        params: Optional[Params] = None,
        content: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> httpx.Response:
        """
        Put request to a GitHub API

        Args:
            api: API path to use for the put request
            params: Optional params to use for the put request
            data: Optional data to include in the put request
        """
        headers = self._request_headers(content_type=content_type)
        url = self._request_url(api)
        return await self._client.put(
            url, params=params, headers=headers, json=data, content=content
        )

    async def patch(
        self,
        api: str,
        *,
        data: Optional[JSON] = None,
        params: Optional[Params] = None,
        content: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> httpx.Response:
        """
        Patch request to a GitHub API

        Args:
            api: API path to use for the patch request
            params: Optional params to use for the patch request
            data: Optional data to include in the patch request
        """
        headers = self._request_headers(content_type=content_type)
        url = self._request_url(api)
        return await self._client.patch(
            url, params=params, headers=headers, json=data, content=content
        )

    def stream(
        self,
        api: str,
        *,
        accept: Optional[str] = None,
    ) -> AsyncContextManager[httpx.Response]:
        """
        Stream data from a GitHub API

        Args:
            api: API path to use for the post request
            accept: Expected content type in the response.
                Default "application/octet-stream".
        """
        headers = self._request_headers(accept=accept)
        url = self._request_url(api)
        return self._client.stream(
            "GET", url, headers=headers, follow_redirects=True
        )

    async def __aenter__(self) -> "GitHubAsyncRESTClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        return await self._client.__aexit__(  # type: ignore
            exc_type, exc_value, traceback
        )


class GitHubAsyncREST:
    """
    Base class for GitHub asynchronous REST classes
    """

    def __init__(self, client: GitHubAsyncRESTClient):
        self._client = client

    async def _get_paged_items(
        self,
        api: str,
        name: str,
        model_cls: Type[GitHubModel],
        *,
        params: Optional[Params] = None,
    ) -> AsyncIterator[GitHubModel]:
        """
        Internal method to get the paged items information from different REST
        URLs.
        """
        request_params: dict[str, ParamValue] = {}
        if params:
            request_params.update(params)
        request_params["per_page"] = "100"  # max number

        async for response in self._client.get_all(api, params=request_params):
            response.raise_for_status()
            data: JSON_OBJECT = response.json()
            for item in data.get(name, []):  # type: ignore
                yield model_cls.from_dict(item)  # type:ignore
