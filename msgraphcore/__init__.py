"""msgraph-core"""

from .core.graph_session import GraphSession
from .middleware.authorization_handler import AuthorizationHandler
from .middleware.authorization_provider import AuthProviderBase, TokenCredentialAuthProvider
from .middleware.options.auth_middleware_options import AuthMiddlewareOptions

__version__ = '0.0.1'
