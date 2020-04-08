## Microsoft Graph Python Client Library

The Microsoft Graph Python client library is a lightweight wrapper around
the Microsoft Graph API.

## Getting Started

Install packages

1. `pip install -i https://test.pypi.org/simple/ msgraphcore`
2. `pip install azure-identity`

Import modules

```python
from azure.identity import XCredential
from msgraphcore import GraphSession, AuthorizationHandler, AuthMiddlewareOptions, TokenCredentialAuthProvider
```

Configure Credential Object

```python
browser_credential = XCredential(<tenant_id>, <client_id>)
```

Create AuthorizationProvider, AuthorizationHandler and list of middleware
```python
auth_provider = TokenCredentialAuthProvider(browser_credential)
options = AuthMiddlewareOptions(['mail.send', 'user.read'])
auth_handler = AuthorizationHandler(auth_provider, auth_provider_options=options)

middleware = [
    auth_handler
]
```

```python
requests = GraphSession(middleware=middleware)
result = graph_session.get('/me')
print(result.json())
```


