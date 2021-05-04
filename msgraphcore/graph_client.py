from typing import List, Optional

from requests import Session

from msgraphcore.client_factory import HTTPClientFactory
from msgraphcore.middleware.abc_token_credential import TokenCredential
from msgraphcore.middleware.middleware import BaseMiddleware
from msgraphcore.middleware.options.middleware_control import middleware_control


class GraphClient:
    """Constructs a custom HTTPClient to be used for requests against Microsoft Graph

    :keyword credential: Accesstoken used to access the Graph API. Created through one of the
        credential classes from `azure.identity`
    :keyword list middleware: Custom middleware(HTTPAdapter) list that will be used to create
        a middleware pipeline. The middleware should be arranged in the order in which they will
        modify the request.
    :keyword enum api_version: The Microsoft Graph API version to be used, for example
        `APIVersion.v1` (default). This value is used in setting the base url for all requests for
        that session.
        :class:`~msgraphcore.enums.APIVersion` defines valid API versions.
    :keyword enum cloud: a supported Microsoft Graph cloud endpoint.
        Defaults to `NationalClouds.Global`
        :class:`~msgraphcore.enums.NationalClouds` defines supported sovereign clouds.
    :keyword tuple timeout: Default connection and read timeout values for all session requests.
        Specify a tuple in the form of Tuple(connect_timeout, read_timeout) if you would like to set
        the values separately. If you specify a single value for the timeout, the timeout value will
        be applied to both the connect and the read timeouts.
    :keyword obj session: A custom Session instance from the python requests library
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not GraphClient.__instance:
            GraphClient.__instance = object.__new__(cls)
        return GraphClient.__instance

    def __init__(self, **kwargs):
        """
        Class constructor that accepts a session object and kwargs to
        be passed to the HTTPClientFactory
        """
        self.graph_session = self.get_graph_session(**kwargs)

    @middleware_control.get_middleware_options
    def get(self, url: str, **kwargs):
        r"""Sends a GET request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return self.graph_session.get(self._graph_url(url), **kwargs)

    @middleware_control.get_middleware_options
    def post(self, url, data=None, json=None, **kwargs):
        r"""Sends a POST request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return self.graph_session.post(self._graph_url(url), data, json, **kwargs)

    @middleware_control.get_middleware_options
    def put(self, url, data=None, **kwargs):
        r"""Sends a PUT request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return self.graph_session.put(self._graph_url(url), data, **kwargs)

    @middleware_control.get_middleware_options
    def patch(self, url, data=None, **kwargs):
        r"""Sends a PATCH request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return self.graph_session.patch(self._graph_url(url), data, **kwargs)

    @middleware_control.get_middleware_options
    def delete(self, url, **kwargs):
        r"""Sends a DELETE request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return self.graph_session.delete(self._graph_url(url), **kwargs)

    def _graph_url(self, url: str) -> str:
        """Appends BASE_URL to user provided path
        :param url: user provided path
        :return: graph_url
        """
        return self.graph_session.base_url + url if (url[0] == '/') else url

    @staticmethod
    def get_graph_session(**kwargs):
        """Method to always return a single instance of a HTTP Client"""

        credential = kwargs.get('credential')
        middleware = kwargs.get('middleware')

        if credential and middleware:
            raise ValueError(
                "Invalid parameters! Both TokenCredential and middleware cannot be passed"
            )
        if not credential and not middleware:
            raise ValueError("Invalid parameters!. Missing TokenCredential or middleware")

        if credential:
            return HTTPClientFactory(**kwargs).create_with_default_middleware(credential)
        return HTTPClientFactory(**kwargs).create_with_custom_middleware(middleware)
