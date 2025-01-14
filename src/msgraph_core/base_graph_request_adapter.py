from typing import Optional

import httpx
from kiota_abstractions.authentication import AuthenticationProvider
from kiota_abstractions.serialization import (
    ParseNodeFactory,
    ParseNodeFactoryRegistry,
    SerializationWriterFactory,
    SerializationWriterFactoryRegistry,
)
from kiota_http.httpx_request_adapter import HttpxRequestAdapter

from .graph_client_factory import GraphClientFactory


class BaseGraphRequestAdapter(HttpxRequestAdapter):

    def __init__(
        self,
        authentication_provider: AuthenticationProvider,
        parse_node_factory: Optional[ParseNodeFactory] = None,
        serialization_writer_factory: Optional[SerializationWriterFactory] = None,
        http_client: Optional[httpx.AsyncClient] = None
    ) -> None:
        if parse_node_factory is None:
            parse_node_factory = ParseNodeFactoryRegistry()
        if serialization_writer_factory is None:
            serialization_writer_factory = SerializationWriterFactoryRegistry()
        if http_client is None:
            http_client = GraphClientFactory.create_with_default_middleware()
        super().__init__(
            authentication_provider=authentication_provider,
            parse_node_factory=parse_node_factory,
            serialization_writer_factory=serialization_writer_factory,
            http_client=http_client
        )
