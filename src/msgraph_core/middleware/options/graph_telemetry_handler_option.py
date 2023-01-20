from typing import List, Optional

from kiota_abstractions.request_option import RequestOption

from ..._constants import SDK_VERSION
from ..._enums import APIVersion


class GraphTelemetryHandlerOption(RequestOption):
    """Config options for the GraphTelemetryHandler
    """

    GRAPH_TELEMETRY_HANDLER_OPTION_KEY = "GraphTelemetryHandlerOption"

    def __init__(
        self, api_version: Optional[APIVersion] = None, sdk_version: str = SDK_VERSION
    ) -> None:
        """To create an instance of GraphTelemetryHandlerOption

        Args:
            api_version (Optional[APIVersion], optional): The Graph API version in use.
            Defaults to None.
            sdk_version (str): The sdk version in use.
            Defaults to SDK_VERSION of grap core.
        """
        self._api_version = api_version
        self._sdk_version = sdk_version

    @property
    def api_version(self):
        """The Graph API version in use"""
        return self._api_version

    @api_version.setter
    def api_version(self, value: bool):
        self._api_version = value

    @property
    def sdk_version(self):
        """The sdk version in use"""
        return self._sdk_version

    @sdk_version.setter
    def sdk_version(self, value: List[str]):
        self._sdk_version = value

    def get_key(self) -> str:
        return self.GRAPH_TELEMETRY_HANDLER_OPTION_KEY
