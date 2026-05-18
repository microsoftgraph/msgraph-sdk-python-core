"""Tests for msgraph_core._enums module."""
from enum import Enum, IntFlag

from msgraph_core._enums import APIVersion, FeatureUsageFlag, NationalClouds


def test_feature_usage_flag_str_returns_string_type():
    """__str__() must return str, not int (Python data model requirement)."""
    for flag in FeatureUsageFlag:
        result = str(flag)
        assert isinstance(result, str), (
            f"str({flag.name}) returned {type(result).__name__}, expected str"
        )


def test_feature_usage_flag_str_returns_numeric_value_as_string():
    """__str__() should return the numeric value as a string."""
    assert str(FeatureUsageFlag.NONE) == "0"
    assert str(FeatureUsageFlag.REDIRECT_HANDLER_ENABLED) == "1"
    assert str(FeatureUsageFlag.RETRY_HANDLER_ENABLED) == "2"
    assert str(FeatureUsageFlag.AUTH_HANDLER_ENABLED) == "4"
    assert str(FeatureUsageFlag.DEFAULT_HTTP_PROVIDER_ENABLED) == "8"
    assert str(FeatureUsageFlag.LOGGING_HANDLER_ENABLED) == "16"


def test_feature_usage_flag_is_intflag():
    """FeatureUsageFlag should be an IntFlag for proper bitwise operations."""
    assert issubclass(FeatureUsageFlag, IntFlag)


def test_feature_usage_flag_is_int_instance():
    """FeatureUsageFlag members should be instances of int."""
    for flag in FeatureUsageFlag:
        assert isinstance(flag, int)


def test_feature_usage_flag_is_enum_instance():
    """FeatureUsageFlag members should be instances of Enum."""
    for flag in FeatureUsageFlag:
        assert isinstance(flag, Enum)


def test_feature_usage_flag_bitwise_or_returns_feature_usage_flag():
    """Bitwise OR should return FeatureUsageFlag, not plain int."""
    combined = FeatureUsageFlag.REDIRECT_HANDLER_ENABLED | FeatureUsageFlag.RETRY_HANDLER_ENABLED
    assert isinstance(combined, FeatureUsageFlag)
    assert combined.value == 3


def test_feature_usage_flag_bitwise_and_returns_feature_usage_flag():
    """Bitwise AND should return FeatureUsageFlag, not plain int."""
    combined = FeatureUsageFlag.REDIRECT_HANDLER_ENABLED | FeatureUsageFlag.RETRY_HANDLER_ENABLED
    result = combined & FeatureUsageFlag.REDIRECT_HANDLER_ENABLED
    assert isinstance(result, FeatureUsageFlag)
    assert result.value == 1


def test_feature_usage_flag_bitwise_xor_returns_feature_usage_flag():
    """Bitwise XOR should return FeatureUsageFlag, not plain int."""
    combined = FeatureUsageFlag.REDIRECT_HANDLER_ENABLED | FeatureUsageFlag.RETRY_HANDLER_ENABLED
    result = combined ^ FeatureUsageFlag.REDIRECT_HANDLER_ENABLED
    assert isinstance(result, FeatureUsageFlag)
    assert result.value == 2


def test_feature_usage_flag_bitwise_invert_returns_feature_usage_flag():
    """Bitwise invert should return FeatureUsageFlag, not plain int."""
    result = ~FeatureUsageFlag.NONE
    assert isinstance(result, FeatureUsageFlag)


def test_feature_usage_flag_combined_flags_str():
    """Combined flags should also return string from __str__()."""
    combined = FeatureUsageFlag.REDIRECT_HANDLER_ENABLED | FeatureUsageFlag.RETRY_HANDLER_ENABLED
    result = str(combined)
    assert isinstance(result, str)
    assert result == "3"


def test_feature_usage_flag_values_are_powers_of_two():
    """Flag values should be powers of 2 (except NONE=0) for proper bitmask behavior."""
    assert FeatureUsageFlag.NONE.value == 0
    assert FeatureUsageFlag.REDIRECT_HANDLER_ENABLED.value == 1
    assert FeatureUsageFlag.RETRY_HANDLER_ENABLED.value == 2
    assert FeatureUsageFlag.AUTH_HANDLER_ENABLED.value == 4
    assert FeatureUsageFlag.DEFAULT_HTTP_PROVIDER_ENABLED.value == 8
    assert FeatureUsageFlag.LOGGING_HANDLER_ENABLED.value == 16


def test_api_version_str_returns_string_type():
    """__str__() must return str."""
    for version in APIVersion:
        result = str(version)
        assert isinstance(result, str)


def test_api_version_str_returns_value():
    """__str__() should return the enum value."""
    assert str(APIVersion.beta) == "beta"
    assert str(APIVersion.v1) == "v1.0"


def test_national_clouds_str_returns_string_type():
    """__str__() must return str."""
    for cloud in NationalClouds:
        result = str(cloud)
        assert isinstance(result, str)


def test_national_clouds_str_returns_url_value():
    """__str__() should return the cloud URL."""
    assert str(NationalClouds.Global) == "https://graph.microsoft.com"
    assert str(NationalClouds.US_GOV) == "https://graph.microsoft.us"
    assert str(NationalClouds.China) == "https://microsoftgraph.chinacloudapi.cn"
