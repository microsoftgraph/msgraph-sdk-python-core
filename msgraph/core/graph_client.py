# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
from typing import List, Optional

import httpx
from kiota_abstractions.authentication import AccessTokenProvider
from kiota_http.middleware.middleware import BaseMiddleware

from ._enums import APIVersion, NationalClouds
from .graph_client_factory import GraphClientFactory


def collect_options(func):
    """Collect middleware options into a middleware control dict and pass it as a header"""

    def wrapper(*args, **kwargs):

        # These are middleware options that can be configured per request.
        # Supports options for default middleware as well as custom middleware.

        options = kwargs.pop('request_options', None)
        if options:
            if 'headers' in kwargs:
                kwargs['headers'].update({'request_options': json.dumps(options)})
            else:
                kwargs['headers'] = {'request_options': json.dumps(options)}

        return func(*args, **kwargs)

    return wrapper


class GraphClient:
    """Constructs a custom HTTPClient to be used for requests against Microsoft Graph

    :keyword token_provider: AccessTokenProvider used to acquire an access token for the Microsoft
        Graph API. Created through one of the credential classes from `azure.identity`
    :keyword list middleware: Custom middleware list that will be used to create
        a middleware pipeline. The middleware should be arranged in the order in which they will
        modify the request.
    :keyword enum api_version: The Microsoft Graph API version to be used, for example
        `APIVersion.v1` (default). This value is used in setting the base url for all requests for
        that session.
        :class:`~msgraphcore.enums.APIVersion` defines valid API versions.
    :keyword enum base_url: a supported Microsoft Graph cloud endpoint.
        Defaults to `NationalClouds.Global`
        :class:`~msgraphcore.enums.NationalClouds` defines supported sovereign clouds.
    :keyword tuple timeout: Default connection and read timeout values for all session requests.
        Specify a tuple in the form of Tuple(connect_timeout, read_timeout) if you would like to set
        the values separately. If you specify a single value for the timeout, the timeout value will
        be applied to both the connect and the read timeouts.
    :keyword client: A custom client instance from the python httpx library
    """
    DEFAULT_CONNECTION_TIMEOUT: int = 30
    DEFAULT_REQUEST_TIMEOUT: int = 100
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not GraphClient.__instance:
            GraphClient.__instance = object.__new__(cls)
        return GraphClient.__instance

    def __init__(
        self,
        token_provider: Optional[AccessTokenProvider] = None,
        api_version: APIVersion = APIVersion.v1,
        base_url: NationalClouds = NationalClouds.Global,
        timeout: httpx.Timeout = httpx.Timeout(
            DEFAULT_REQUEST_TIMEOUT, connect=DEFAULT_CONNECTION_TIMEOUT
        ),
        client: Optional[httpx.AsyncClient] = None,
        middleware: Optional[List[BaseMiddleware]] = None
    ):
        """
        Class constructor that accepts a session object and kwargs to
        be passed to the GraphClientFactory
        """
        self.client = self.get_graph_client(
            token_provider, api_version, base_url, timeout, client, middleware
        )

    @collect_options
    async def get(
        self,
        url,
        *,
        params=None,
        headers=None,
        cookies=None,
        request_options=None,
        extensions=None
    ):
        r"""Sends a GET request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        async with self.client as client:
            return await client.get(
                url, params=params, headers=headers, cookies=cookies, extensions=extensions
            )

    @collect_options
    async def options(
        self,
        url,
        *,
        params=None,
        headers=None,
        cookies=None,
        request_options=None,
        extensions=None
    ):
        r"""Sends a OPTIONS request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        async with self.client as client:
            return await client.options(
                url, params=params, headers=headers, cookies=cookies, extensions=extensions
            )

    @collect_options
    async def head(
        self,
        url,
        *,
        params=None,
        headers=None,
        cookies=None,
        request_options=None,
        extensions=None
    ):
        r"""Sends a HEAD request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        async with self.client as client:
            return await client.head(
                url, params=params, headers=headers, cookies=cookies, extensions=extensions
            )

    @collect_options
    async def post(
        self,
        url,
        *,
        content=None,
        data=None,
        files=None,
        json=None,
        params=None,
        headers=None,
        cookies=None,
        request_options=None,
        extensions=None
    ):
        r"""Sends a POST request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        async with self.client as client:
            return await client.post(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                cookies=cookies,
                extensions=extensions
            )

    @collect_options
    async def put(
        self,
        url,
        *,
        content=None,
        data=None,
        files=None,
        json=None,
        params=None,
        headers=None,
        cookies=None,
        request_options=None,
        extensions=None
    ):
        r"""Sends a PUT request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        async with self.client as client:
            return await client.put(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                cookies=cookies,
                extensions=extensions
            )

    @collect_options
    async def patch(
        self,
        url,
        *,
        content=None,
        data=None,
        files=None,
        json=None,
        params=None,
        headers=None,
        cookies=None,
        request_options=None,
        extensions=None
    ):
        r"""Sends a PATCH request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        async with self.client as client:
            return await client.patch(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                cookies=cookies,
                extensions=extensions
            )

    @collect_options
    async def delete(
        self,
        url,
        *,
        params=None,
        headers=None,
        cookies=None,
        request_options=None,
        extensions=None
    ):
        r"""Sends a DELETE request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        async with self.client as client:
            return await client.delete(
                url, params=params, headers=headers, cookies=cookies, extensions=extensions
            )

    @staticmethod
    def get_graph_client(
        token_provider: Optional[AccessTokenProvider],
        api_version: APIVersion,
        base_url: NationalClouds,
        timeout: httpx.Timeout,
        client: Optional[httpx.AsyncClient],
        middleware: Optional[List[BaseMiddleware]],
    ):
        """Method to always return a single instance of a HTTP Client"""

        if token_provider and middleware:
            raise ValueError(
                "Invalid parameters! Both TokenCredential and middleware cannot be passed"
            )
        if not token_provider and not middleware:
            raise ValueError("Invalid parameters!. Missing TokenCredential or middleware")

        if token_provider and not middleware:
            return GraphClientFactory(api_version, base_url, timeout,
                                      client).create_with_default_middleware(token_provider)
        return GraphClientFactory(api_version, base_url, timeout,
                                  client).create_with_custom_middleware(middleware)
