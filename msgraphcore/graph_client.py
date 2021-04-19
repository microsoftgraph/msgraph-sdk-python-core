from typing import List, Optional

from requests import Session

from msgraphcore.client_factory import HTTPClientFactory
from msgraphcore.middleware.abc_token_credential import TokenCredential
from msgraphcore.middleware.middleware import BaseMiddleware
from msgraphcore.middleware.options.middleware_control import middleware_control


class GraphClient:
    """Constructs a custom HTTPClient to be used for requests against Microsoft Graph"""
    def __init__(self, **kwargs):
        """
        Class constructor that accepts a session object and kwargs to
        be passed to the HTTPClientFactory
        """
        self.graph_session = get_graph_session(**kwargs)

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


_INSTANCE = None


def get_graph_session(**kwargs):
    """Method to always return a single instance of a HTTP Client"""

    global _INSTANCE

    credential = kwargs.get('credential')
    middleware = kwargs.get('middleware')

    if credential and middleware:
        raise Exception("Invalid parameters! Both TokenCredential and middleware cannot be passed")
    if not credential and not middleware:
        raise ValueError("Invalid parameters!. Missing TokenCredential or middleware")
    if _INSTANCE is None:
        if credential:
            _INSTANCE = HTTPClientFactory(**kwargs).create_with_default_middleware(credential)
        elif middleware:
            _INSTANCE = HTTPClientFactory(**kwargs).create_with_custom_middleware(middleware)
    return _INSTANCE
