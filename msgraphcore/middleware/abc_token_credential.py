from abc import ABC, abstractmethod


class TokenCredential(ABC):
    @abstractmethod
    def get_token(self, *scopes, **kwargs):
        pass


class RetryConfigs(ABC):
    @abstractmethod
    def get_retry_configs(self, *retry_config, **kwargs):
        pass
