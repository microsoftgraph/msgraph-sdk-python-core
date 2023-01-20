import pytest

from src.msgraph_core._constants import SDK_VERSION
from src.msgraph_core._enums import APIVersion
from src.msgraph_core.middleware.options import GraphTelemetryHandlerOption

def test_graph_telemetry_handler_options_default():
    telemetry_options = GraphTelemetryHandlerOption()
    
    assert telemetry_options.get_key() == "GraphTelemetryHandlerOption"
    assert telemetry_options.api_version is None
    assert telemetry_options.sdk_version == SDK_VERSION

def test_graph_telemetry_handler_options_custom():
    telemetry_options = GraphTelemetryHandlerOption(api_version=APIVersion.beta, sdk_version='1.0.0')
    
    assert telemetry_options.get_key() == "GraphTelemetryHandlerOption"
    assert telemetry_options.api_version == APIVersion.beta
    assert telemetry_options.sdk_version == '1.0.0'


