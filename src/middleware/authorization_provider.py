from ._base_auth import AuthProviderBase, TokenCredential


class TokenCredentialAuthProvider(AuthProviderBase):
    def __init__(self, credential: TokenCredential):
        self.credential = credential
        self.scopes = ''

    def get_access_token(self):
        return self.credential.get_token(self.scopes)[0]
