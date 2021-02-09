import json
from pprint import pprint

from azure.identity import InteractiveBrowserCredential

from msgraphcore import GraphSession

scopes = ['user.read']
browser_credential = InteractiveBrowserCredential(client_id='ENTER_YOUR_CLIENT_ID')
graph_session = GraphSession(browser_credential, scopes)


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
                        'address': 'ENTER_RECEPIENT_EMAIL_ADDRESS'
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

