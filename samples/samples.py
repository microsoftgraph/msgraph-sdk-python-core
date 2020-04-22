import json
from pprint import pprint

from azure.identity import InteractiveBrowserCredential
from msgraphcore.middleware.authorization import TokenCredentialAuthProvider

from msgraphcore import GraphSession

browser_credential = InteractiveBrowserCredential(client_id='YOUR_CLIENT_ID')
auth_provider = TokenCredentialAuthProvider(browser_credential)
graph_session = GraphSession(auth_provider)


def post_sample():
    body = {
        'message': {
            'subject': 'Python SDK Meet for lunch?',
            'body': {
                'contentType': 'Text',
                'content': 'The new cafeteria is open.'
            },
            'toRecipients': [
                {
                    'emailAddress': {
                        'address': 'jaobala@microsoft.com'
                    }
                }
            ]}
    }

    result = graph_session \
        .post('/me/sendMail',
              data=json.dumps(body),
              scopes=['mail.send'],
              headers={'Content-Type': 'application/json'}
              )
    pprint(result.status_code)


def get_sample():
    result = graph_session.get('/me/messages', scopes=['mail.read'])
    pprint(result.json())


if __name__ == '__main__':
    post_sample()
    get_sample()

