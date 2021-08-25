[![CI Actions Status](https://github.com/microsoftgraph/msgraph-sdk-python-core/workflows/msgraph-sdk-python-core/badge.svg)](https://github.com/microsoftgraph/msgraph-sdk-python-core/actions)
[![Downloads](https://pepy.tech/badge/msgraph-core)](https://pepy.tech/project/msgraph-core)
## Microsoft Graph Core Python Client Library (preview).

The Microsoft Graph Core Python client library is a lightweight wrapper around the Microsoft Graph API. It provides functionality to create clients with desired configuration and middleware.

**Disclaimer**: Please, be aware that preview versions of `msgraph-core` package are for testing purpose only. Do not use them in a production environment.

## Prerequisites

    Python 3.5+ (this library doesn't support older versions of Python)

## Getting started

### 1. Register your application

To call Microsoft Graph, your app must acquire an access token from the Microsoft identity platform. Learn more about this -

-   [Authentication and authorization basics for Microsoft Graph](https://docs.microsoft.com/en-us/graph/auth/auth-concepts)
-   [Register your app with the Microsoft identity platform](https://docs.microsoft.com/en-us/graph/auth-register-app-v2)


### 2. Install the required packages

msgraph-core is available on PyPI.

```cmd
python -m pip install msgraph-core
python -m pip install azure-identity
```

### 3. Import modules

```python
from azure.identity import InteractiveBrowserCredential
from msgraph.core import GraphClient
```

### 4. Configure a Credential Object

```python
# Using InteractiveBrowserCredential for demonstration purposes.
# There are many other options for getting an access token. See the following for more information.
# https://pypi.org/project/azure-identity/

browser_credential = InteractiveBrowserCredential(client_id='YOUR_CLIENT_ID')
```

### 5. Pass the credential object to the GraphClient constructor.

```python
client = GraphClient(credential=browser_credential)
```

### 6. Make a requests to the graph using the client

```python
result = client.get('/me')
print(result.json())
```

For more information on how to use the package, refer to the [samples](https://github.com/microsoftgraph/msgraph-sdk-python-core/tree/dev/samples).


## Telemetry Metadata

This library captures metadata by default that provides insights into its usage and helps to improve the developer experience. This metadata includes the `SdkVersion`, `RuntimeEnvironment` and `HostOs` on which the client is running.

## Issues

View or log issues on the [Issues](https://github.com/microsoftgraph/msgraph-sdk-python-core/issues) tab in the repo.

## Contributing

Please see the [contributing guidelines](CONTRIBUTING.rst).

## Copyright and license

Copyright (c) Microsoft Corporation. All Rights Reserved. Licensed under the MIT [license](LICENSE).

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.


