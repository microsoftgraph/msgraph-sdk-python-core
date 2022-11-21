import pytest
from kiota_http.kiota_client_factory import KiotaClientFactory

from msgraph_core._enums import FeatureUsageFlag
from msgraph_core.middleware import AsyncGraphTransport, GraphRequestContext


def test_set_request_context_and_feature_usage(mock_request, mock_transport):
    middleware = KiotaClientFactory.get_default_middleware()
    pipeline = KiotaClientFactory.create_middleware_pipeline(middleware, mock_transport)
    transport = AsyncGraphTransport(mock_transport, pipeline)
    transport.set_request_context_and_feature_usage(mock_request)

    assert hasattr(mock_request, 'context')
    assert isinstance(mock_request.context, GraphRequestContext)
    assert mock_request.context.feature_usage == hex(
        FeatureUsageFlag.RETRY_HANDLER_ENABLED | FeatureUsageFlag.REDIRECT_HANDLER_ENABLED
    )
