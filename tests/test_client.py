"""Tests for the VelaSmart cloud API client."""

from velasmart import VelaSmartApiClient, VelaSmartApiError


def test_parse_devices() -> None:
    """Test parsing the nested device list response."""
    result = {
        "code": 200,
        "data": {
            "list": [
                {
                    "list": [
                        {
                            "deviceId": "5c1c0a6612",
                            "deviceName": "BidRoller",
                            "gatewayMac": "e08cfec409a2",
                            "deviceType": 3,
                            "position": 50,
                            "onlineStatus": 0,
                            "electric": 31,
                        }
                    ]
                }
            ]
        },
    }
    devices = VelaSmartApiClient._parse_devices(result)
    assert len(devices) == 1
    device = devices[0]
    assert device["id"] == "5c1c0a6612"
    assert device["name"] == "BidRoller"
    assert device["gateway_mac"] == "e08cfec409a2"
    assert device["device_type"] == 3
    assert device["position"] == 50
    assert device["is_closed"] is False
    assert device["online"] is False
    assert device["battery"] == 31


def test_parse_devices_empty() -> None:
    """Test parsing an empty device list."""
    result = {"code": 200, "data": {"list": []}}
    assert VelaSmartApiClient._parse_devices(result) == []


def test_parse_devices_position_closed() -> None:
    """Test that position 0 marks the device as closed."""
    result = {
        "code": 200,
        "data": {
            "list": [
                {
                    "list": [
                        {
                            "deviceId": "abc",
                            "position": 0,
                        }
                    ]
                }
            ]
        },
    }
    devices = VelaSmartApiClient._parse_devices(result)
    assert devices[0]["is_closed"] is True
