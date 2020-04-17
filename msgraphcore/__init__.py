"""msgraph-core"""

from msgraphcore.graph_session import GraphSession
from .middleware.authorization import AuthProviderBase, TokenCredentialAuthProvider
from .constants import SDK_VERSION

__version__ = SDK_VERSION
