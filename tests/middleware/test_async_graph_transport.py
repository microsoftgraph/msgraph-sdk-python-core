import asyncio

import httpx
import pytest
from kiota_abstractions.authentication import AnonymousAuthenticationProvider
from kiota_abstractions.method import Method
from kiota_abstractions.request_information import RequestInformation
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware.options import RedirectHandlerOption

from msgraph_core._enums import FeatureUsageFlag
from msgraph_core.graph_client_factory import GraphClientFactory
from msgraph_core.middleware import AsyncGraphTransport, GraphRequestContext
from msgraph_core.middleware.async_graph_transport import REQUEST_OPTIONS_KEY


def test_set_request_context_and_feature_usage(mock_request, mock_transport):
    middleware = KiotaClientFactory.get_default_middleware(None)
    pipeline = KiotaClientFactory.create_middleware_pipeline(middleware, mock_transport)
    transport = AsyncGraphTransport(mock_transport, pipeline)
    transport.set_request_context_and_feature_usage(mock_request)

    assert hasattr(mock_request, 'context')
    assert isinstance(mock_request.context, GraphRequestContext)
    assert mock_request.context.feature_usage == hex(
        FeatureUsageFlag.RETRY_HANDLER_ENABLED | FeatureUsageFlag.REDIRECT_HANDLER_ENABLED
    )


@pytest.mark.parametrize(
    'content_type', [
        'application/octet-stream',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ]
)
def test_binary_download_follows_redirect_with_kiota_request_extensions(content_type):
    calls = []
    contexts = []

    def handle_request(request):
        calls.append(str(request.url))
        contexts.append(request.context)
        if request.url.host == 'graph.example':
            return httpx.Response(302, headers={'Location': 'https://download.example/file'})
        return httpx.Response(
            200, content=b'binary content', headers={'Content-Type': content_type}
        )

    async def download():
        client = GraphClientFactory.create_with_default_middleware(
            client=httpx.AsyncClient(transport=httpx.MockTransport(handle_request))
        )
        try:
            adapter = HttpxRequestAdapter(AnonymousAuthenticationProvider(), http_client=client)
            request_info = RequestInformation()
            request_info.http_method = Method.GET
            request_info.url = 'https://graph.example/drive/item/content'
            return await adapter.send_primitive_async(request_info, 'bytes', {})
        finally:
            await client.aclose()

    assert asyncio.run(download()) == b'binary content'
    assert calls == ['https://graph.example/drive/item/content', 'https://download.example/file']
    assert all(isinstance(context, GraphRequestContext) for context in contexts)


def test_extension_options_take_precedence_over_legacy_attribute(mock_transport):
    middleware = KiotaClientFactory.get_default_middleware(None)
    pipeline = KiotaClientFactory.create_middleware_pipeline(middleware, mock_transport)
    transport = AsyncGraphTransport(mock_transport, pipeline)
    request = httpx.Request('GET', 'https://example.org', extensions={REQUEST_OPTIONS_KEY: {}})
    request.options = {'legacy': True}

    transport.set_request_context_and_feature_usage(request)

    assert request.context.middleware_control == {}


def test_request_without_options_bypasses_graph_pipeline():
    calls = []

    def handle_request(request):
        calls.append(request)
        return httpx.Response(200, content=b'body')

    async def send():
        underlying_transport = httpx.MockTransport(handle_request)
        middleware = KiotaClientFactory.get_default_middleware(None)
        pipeline = KiotaClientFactory.create_middleware_pipeline(middleware, underlying_transport)
        transport = AsyncGraphTransport(underlying_transport, pipeline)
        return await transport.handle_async_request(httpx.Request('GET', 'https://example.org'))

    assert asyncio.run(send()).status_code == 200
    assert len(calls) == 1
    assert not hasattr(calls[0], 'context')


def test_extension_only_request_uses_graph_pipeline():
    requests = []

    def handle_request(request):
        requests.append(request)
        return httpx.Response(200, content=b'body')

    async def send():
        underlying_transport = httpx.MockTransport(handle_request)
        middleware = KiotaClientFactory.get_default_middleware(None)
        pipeline = KiotaClientFactory.create_middleware_pipeline(middleware, underlying_transport)
        transport = AsyncGraphTransport(underlying_transport, pipeline)
        request = httpx.Request('GET', 'https://example.org', extensions={REQUEST_OPTIONS_KEY: {}})
        assert not hasattr(request, 'options')
        return await transport.handle_async_request(request)

    assert asyncio.run(send()).content == b'body'
    assert len(requests) == 1
    assert isinstance(requests[0].context, GraphRequestContext)
    assert requests[0].context.middleware_control == {}
    assert requests[0].context.feature_usage == hex(
        FeatureUsageFlag.RETRY_HANDLER_ENABLED | FeatureUsageFlag.REDIRECT_HANDLER_ENABLED
    )


@pytest.mark.parametrize(
    'legacy_redirect, extension_options, expected_status, expected_calls', [
        (False, None, 302, 1),
        (None, None, 200, 2),
        (True, False, 302, 1),
        (False, True, 200, 2),
        (False, {}, 200, 2),
    ]
)
def test_request_redirect_options_are_honored(
    legacy_redirect, extension_options, expected_status, expected_calls
):
    requests = []

    def handle_request(request):
        requests.append(request)
        if request.url.path == '/start':
            return httpx.Response(302, headers={'Location': 'https://example.org/end'})
        return httpx.Response(200, content=b'body')

    async def send():
        underlying_transport = httpx.MockTransport(handle_request)
        middleware = KiotaClientFactory.get_default_middleware(None)
        pipeline = KiotaClientFactory.create_middleware_pipeline(middleware, underlying_transport)
        transport = AsyncGraphTransport(underlying_transport, pipeline)
        request = httpx.Request('GET', 'https://example.org/start')
        request.options = {}
        if legacy_redirect is not None:
            option = RedirectHandlerOption(should_redirect=legacy_redirect)
            request.options[option.get_key()] = option
        if extension_options is not None:
            options = extension_options
            if isinstance(options, bool):
                option = RedirectHandlerOption(should_redirect=options)
                options = {option.get_key(): option}
            request.extensions[REQUEST_OPTIONS_KEY] = options
        return await transport.handle_async_request(request)

    assert asyncio.run(send()).status_code == expected_status
    assert len(requests) == expected_calls
    assert isinstance(requests[0].context, GraphRequestContext)
