[![CI Actions Status](https://github.com/microsoftgraph/msgraph-sdk-python-core/workflows/CI/badge.svg)](https://github.com/microsoftgraph/msgraph-sdk-python-core/actions)

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
from msgraphcore import GraphSession
```

Configure Credential Object

```python
# Added UsernamePassword for demo purposes only, please don't use this in production.
# ugly_credential = UsernamePasswordCredential('set-clientId', 'set-username', 'set-password')

device_credential = DeviceCodeCredential(
    'set-clientId')

# There are many other options for getting an access token. See the following for more information.
# https://pypi.org/project/azure-identity/

```

Pass the credential object and scopes to the GraphSession constructor.
```python
scopes = ['mail.send', 'user.read']
graph_session = GraphSession(device_credential, scopes)
```

```python
result = graph_session.get('/me')
print(result.json())
```


