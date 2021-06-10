# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
#pylint: disable=undefined-variable
"""Demonstrates using the GraphClient to make HTTP Requests to Microsoft Graph"""
import json
from pprint import pprint

# This sample uses InteractiveBrowserCredential only for demonstration.
# Any azure-identity TokenCredential class will work the same.
from azure.identity import InteractiveBrowserCredential
from requests import Session

from msgraph.core import APIVersion, GraphClient, NationalClouds

scopes = ['user.read']
browser_credential = InteractiveBrowserCredential(client_id='YOUR_CLIENT_ID')
client = GraphClient(credential=browser_credential)


def get_sample():
    """Sample HTTP GET request using the GraphClient"""
    result = client.get('/me/messages', scopes=['mail.read'])
    pprint(result.json())


def post_sample():
    """Sample HTTP POST request using the GraphClient"""
    body = {
        'message': {
            'subject': 'Python SDK Meet for lunch?',
            'body': {
                'contentType': 'Text',
                'content': 'The new cafeteria is open.'
            },
            'toRecipients': [{
                'emailAddress': {
                    'address': 'ENTER_RECEPIENT_EMAIL_ADDRESS'
                }
            }]
        }
    }

    result = client \
        .post('/me/sendMail',
              data=json.dumps(body),
              scopes=['mail.send'],
              headers={'Content-Type': 'application/json'}
              )
    pprint(result.status_code)


def client_with_custom_session_sample():
    """Sample client with a custom Session object"""
    session = Session()
    my_client = GraphClient(credential=browser_credential, session=session)
    result = my_client.get('/me')
    pprint(result.json())


def client_with_custom_settings_sample():
    """
    Sample client that makes requests against the beta api on a specified cloud endpoint
    """
    my_client = GraphClient(
        credential=browser_credential,
        api_version=APIVersion.beta,
        cloud=NationalClouds.Germany,
    )
    result = my_client.get(
        '/users',
        params={
            '$select': 'displayName',
            '$top': '10'
        },
    )
    pprint(result.json())


def client_with_custom_middleware():
    """Sample client with a custom middleware chain"""
    middleware = [
        CustomAuthorizationHandler(),
        MyCustomMiddleware(),
    ]

    my_client = GraphClient(credential=browser_credential, middleware=middleware)
    result = my_client.get(
        'https://graph.microsoft.com/v1.0/users',
        params={
            '$select': 'displayName',
            '$top': '10'
        },
    )
    pprint(result.json())


if __name__ == '__main__':
    post_sample()
    get_sample()
    client_with_custom_session_sample()
    client_with_custom_settings_sample()
    client_with_custom_middleware()
