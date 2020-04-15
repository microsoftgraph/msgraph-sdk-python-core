## Microsoft Graph Python Client Library

The Microsoft Graph Python client library is a lightweight wrapper around
the Microsoft Graph API.

## Getting Started

Install packages

1. `pip install -i https://test.pypi.org/simple/ msgraphcore`
2. `pip install azure-identity`

Import modules

```python
from azure.identity import UsernamePasswordCredential, DeviceCodeCredential
from msgraphcore import GraphSession, AuthorizationHandler, AuthMiddlewareOptions, TokenCredentialAuthProvider
```

Configure Credential Object

```python
# Added UsernamePassword for demo purposes only, please don't use this in production.
# ugly_credential = UsernamePasswordCredential('set-clientId', 'set-username', 'set-password')

device_credential = DeviceCodeCredential(
    'set-clientId')

# There are many other options for getting an access token. See the following for more information.
# https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/azure/identity/_credentials/__init__.py

```

Create AuthorizationProvider, AuthorizationHandler and list of middleware
```python
auth_provider = TokenCredentialAuthProvider(device_credential)
options = AuthMiddlewareOptions(['mail.send', 'user.read'])
auth_handler = AuthorizationHandler(auth_provider, auth_provider_options=options)

middleware = [
    auth_handler
]
```

```python
graph_session = GraphSession(middleware=middleware)
result = graph_session.get('/me')
print(result.json())
```


