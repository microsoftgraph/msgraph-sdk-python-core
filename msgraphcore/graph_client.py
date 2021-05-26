from msgraphcore.middleware.options.middleware_control import MiddlewareControl
from msgraphcore.middleware.request_context import RequestContext
from typing import List, Optional

from requests import Session
from requests import PreparedRequest
from requests import Request

from msgraphcore.client_factory import HTTPClientFactory
from msgraphcore.middleware.abc_token_credential import TokenCredential
from msgraphcore.middleware.middleware import BaseMiddleware

supported_options = ['scopes', 'custom_option']


def attach_context(func):
    def wrapper(*args, **kwargs):
        mw_control = dict()
        headers = kwargs.pop('headers', {})

        for option in supported_options:
            mw_option = kwargs.pop(option, None)

            if mw_option:
                mw_control.update({option: mw_option})

        req_context = RequestContext(mw_control, headers)

        request = func(*args, **kwargs)
        request.context = req_context

        return request

    return wrapper


class GraphClient:
    """Constructs a custom HTTPClient to be used for requests against Microsoft Graph"""
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

    def get(self, url: str, **kwargs):
        r"""Sends a GET request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        prepped_req = self.prepare_request('GET', self._graph_url(url), **kwargs)
        return self.graph_session.send(prepped_req)

    def post(self, url, **kwargs):
        r"""Sends a POST request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        prepped_req = self.prepare_request('POST', self._graph_url(url), **kwargs)
        return self.graph_session.send(prepped_req)

    def put(self, url, data=None, **kwargs):
        r"""Sends a PUT request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return self.graph_session.put(self._graph_url(url), data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        r"""Sends a PATCH request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return self.graph_session.patch(self._graph_url(url), data, **kwargs)

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

    @attach_context
    def prepare_request(self, method, url, **kwargs):
        req = Request(method, url, **kwargs)
        prepared = Session().prepare_request(req)
        return prepared

    @staticmethod
    def get_graph_session(**kwargs):
        """Method to always return a single instance of a HTTP Client"""

        credential = kwargs.pop('credential', None)
        middleware = kwargs.pop('middleware', None)

        if credential and middleware:
            raise ValueError(
                "Invalid parameters! Both TokenCredential and middleware cannot be passed"
            )
        if not credential and not middleware:
            raise ValueError("Invalid parameters!. Missing TokenCredential or middleware")

        if credential:
            return HTTPClientFactory(**kwargs).create_with_default_middleware(credential, **kwargs)
        return HTTPClientFactory(**kwargs).create_with_custom_middleware(middleware)
