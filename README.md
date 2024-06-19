[![PyPI version](https://badge.fury.io/py/msgraph-core.svg)](https://badge.fury.io/py/msgraph-core)
[![CI Actions Status](https://github.com/microsoftgraph/msgraph-sdk-python-core/actions/workflows/build.yml/badge.svg)](https://github.com/microsoftgraph/msgraph-sdk-python-core/actions/workflows/build.yml)
[![Downloads](https://pepy.tech/badge/msgraph-core)](https://pepy.tech/project/msgraph-core)

## Microsoft Graph Core Python Client Library

The Microsoft Graph Core Python Client Library contains core classes used by [Microsoft Graph Python Client Library](https://github.com/microsoftgraph/msgraph-sdk-python) to send native HTTP requests to [Microsoft Graph API](https://graph.microsoft.com).

> NOTE:
> This is a new major version of the Python Core library for Microsoft Graph based on the [Kiota](https://microsoft.github.io/kiota/) project. We recommend to use this library with the [full Python SDK](https://github.com/microsoftgraph/msgraph-sdk-python).
> Upgrading to this version from the [previous version of the Python Core library](https://pypi.org/project/msgraph-core/0.2.2/) will introduce breaking changes into your application.

## Prerequisites

    Python 3.8+

This library doesn't support [older](https://devguide.python.org/versions/) versions of Python.

## Getting started

### 1. Register your application

To call Microsoft Graph, your app must acquire an access token from the Microsoft identity platform. Learn more about this -

- [Authentication and authorization basics for Microsoft Graph](https://docs.microsoft.com/en-us/graph/auth/auth-concepts)
- [Register your app with the Microsoft identity platform](https://docs.microsoft.com/en-us/graph/auth-register-app-v2)

### 2. Install the required packages

msgraph-core is available on PyPI.

```cmd
pip3 install msgraph-core
pip3 install azure-identity
```

### 3. Configure an Authentication Provider Object

An instance of the `BaseGraphRequestAdapter` class handles building client. To create a new instance of this class, you need to provide an instance of `AuthenticationProvider`, which can authenticate requests to Microsoft Graph.

> **Note**: This client library offers an asynchronous API by default. Async is a concurrency model that is far more efficient than multi-threading, and can provide significant performance benefits and enable the use of long-lived network connections such as WebSockets. We support popular python async environments such as `asyncio`, `anyio` or `trio`. For authentication you need to use one of the async credential classes from `azure.identity`.

```py
# Using EnvironmentCredential for demonstration purposes.
# There are many other options for getting an access token. See the following for more information.
# https://pypi.org/project/azure-identity/#async-credentials
from azure.identity.aio import EnvironmentCredential
from msgraph_core.authentication import AzureIdentityAuthenticationProvider

credential=EnvironmentCredential()
auth_provider = AzureIdentityAuthenticationProvider(credential)
```

> **Note**: `AzureIdentityAuthenticationProvider` sets the default scopes and allowed hosts.

### 5. Pass the authentication provider object to the BaseGraphRequestAdapter constructor

```python
from msgraph_core import BaseGraphRequestAdapter
adapter = BaseGraphRequestAdapter(auth_provider)
```

### 6. Make a requests to the graph

After you have a `BaseGraphRequestAdapter` that is authenticated, you can begin making calls against the service.

```python
import asyncio
from kiota_abstractions.request_information import RequestInformation

request_info = RequestInformation()
request_info.url = 'https://graph.microsoft.com/v1.0/me'

# User is your own type that implements Parsable or comes from the service library
user = asyncio.run(adapter.send_async(request_info, User, {}))
print(user.display_name)
```

## Telemetry Metadata

This library captures metadata by default that provides insights into its usage and helps to improve the developer experience. This metadata includes the `SdkVersion`, `RuntimeEnvironment` and `HostOs` on which the client is running.

## Issues

View or log issues on the [Issues](https://github.com/microsoftgraph/msgraph-sdk-python-core/issues) tab in the repo.

## Contributing

Please see the [contributing guidelines](CONTRIBUTING.md).

## Copyright and license

Copyright (c) Microsoft Corporation. All Rights Reserved. Licensed under the MIT [license](LICENSE).

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
