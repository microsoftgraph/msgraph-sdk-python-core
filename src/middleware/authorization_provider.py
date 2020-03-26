from ._base import AuthProviderBase, TokenCredential


class TokenCredentialAuthProvider(AuthProviderBase):
    def __init__(self, credential: TokenCredential, scopes=''):
        self.credential = credential
        self.scopes = scopes

    @property
    def scopes(self):
        return self.scopes

    @scopes.setter
    def scopes(self, scopes):
        self.scopes = scopes

    def get_access_token(self):
        return self.credential.get_token(self.scopes)[0]
