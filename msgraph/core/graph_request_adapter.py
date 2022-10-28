from kiota_abstractions.authentication import AuthenticationProvider
from kiota_abstractions.serialization import (
    Parsable,
    ParsableFactory,
    ParseNode,
    ParseNodeFactory,
    ParseNodeFactoryRegistry,
    SerializationWriterFactory,
    SerializationWriterFactoryRegistry,
)
from kiota_http.httpx_request_adapter import HttpxRequestAdapter

from .graph_client import GraphClient
from .graph_client_factory import GraphClientFactory


class GraphRequestAdapter(HttpxRequestAdapter):

    def __init__(
        self,
        authentication_provider: AuthenticationProvider,
        parse_node_factory: ParseNodeFactory = ParseNodeFactoryRegistry(),
        serialization_writer_factory:
        SerializationWriterFactory = SerializationWriterFactoryRegistry(),
        http_client: GraphClient = GraphClient()
    ) -> None:
        super().__init__(
            authentication_provider=authentication_provider,
            parse_node_factory=parse_node_factory,
            serialization_writer_factory=serialization_writer_factory,
            http_client=http_client
        )
