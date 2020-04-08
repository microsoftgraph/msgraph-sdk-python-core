"""msgraph-core"""

from msgraphcore.graph_session import GraphSession
from .middleware.authorization_handler import AuthorizationHandler
from .middleware.authorization_provider import AuthProviderBase, TokenCredentialAuthProvider
from .middleware.options.auth_middleware_options import AuthMiddlewareOptions
from .constants import SDK_VERSION

__version__ = SDK_VERSION
