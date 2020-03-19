from abc import ABC, abstractmethod


class TokenCredential(ABC):
    @abstractmethod
    def get_token(self, *scopes, **kwargs):
        pass


class AuthProviderBase(ABC):
    @abstractmethod
    def get_access_token(self):
        pass