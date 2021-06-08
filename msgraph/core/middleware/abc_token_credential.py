# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from abc import ABC, abstractmethod


class TokenCredential(ABC):
    @abstractmethod
    def get_token(self, *scopes, **kwargs):
        pass
