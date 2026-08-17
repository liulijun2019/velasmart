"""Client for the VelaSmart cloud API."""

from __future__ import annotations

import binascii
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

AUTH_URL = (
    "https://wly87bcr9j.execute-api.cn-north-1.amazonaws.com.cn/prod/assistantLogin"
)
DEVICE_LIST_URL = (
    "https://wly87bcr9j.execute-api.cn-north-1.amazonaws.com.cn/prod/findDeviceByAccount"
)
SEND_ORDER_URL = (
    "https://wly87bcr9j.execute-api.cn-north-1.amazonaws.com.cn/prod/assistantSendOrder"
)

TIMEOUT = aiohttp.ClientTimeout(total=10)


class VelaSmartApiError(Exception):
    """Raised when the VelaSmart cloud API returns an error."""


class VelaSmartApiClient:
    """Client for the VelaSmart cloud API."""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the client."""
        self._username = username
        self._password = password
        self._session = session
        self._token: str | None = None

    async def _post(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform a POST request, reusing an injected session when available."""
        if self._session is not None:
            async with self._session.post(
                url, headers=headers, json=data, timeout=TIMEOUT
            ) as response:
                return await response.json()

        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.post(url, headers=headers, json=data) as response:
                return await response.json()

    async def authenticate(self) -> None:
        """Authenticate with the cloud API and store the returned token."""
        try:
            result = await self._post(
                AUTH_URL,
                data={"account": self._username, "password": self._password},
            )
        except aiohttp.ClientError as err:
            raise VelaSmartApiError(f"Network error: {err}") from err

        if result.get("code") != 200:
            raise VelaSmartApiError(f"Authentication failed: {result}")

        token = (result.get("data") or {}).get("token")
        if not token:
            raise VelaSmartApiError("Authentication response did not contain a token")
        self._token = token

    async def get_devices(self) -> list[dict[str, Any]]:
        """Fetch the list of devices for the account."""
        if not self._token:
            await self.authenticate()

        try:
            result = await self._post(
                DEVICE_LIST_URL, headers={"token": self._token}, data={}
            )
        except aiohttp.ClientError as err:
            raise VelaSmartApiError(f"Network error: {err}") from err

        if result.get("code") != 200:
            raise VelaSmartApiError(f"Failed to fetch device list: {result}")

        return self._parse_devices(result)

    @staticmethod
    def _parse_devices(result: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse the nested device list returned by the API."""
        data = result.get("data") or {}
        groups = data.get("list") or []
        devices: list[dict[str, Any]] = []
        for group in groups:
            if not isinstance(group, dict):
                continue
            for device in group.get("list") or []:
                if not isinstance(device, dict):
                    continue
                position = int(device.get("position", 0) or 0)
                devices.append(
                    {
                        "id": device.get("deviceId", ""),
                        "name": device.get("deviceName", "VelaSmart Curtain"),
                        "gateway_mac": device.get("gatewayMac", ""),
                        "device_type": device.get("deviceType", "curtain"),
                        "position": position,
                        "is_closed": position == 0,
                        "online": device.get("onlineStatus", 0) == 1,
                        "battery": device.get("electric"),
                    }
                )
        return devices

    async def send_command(
        self, device_id: str, gateway_mac: str, position: int
    ) -> None:
        """Send a position command to the given device."""
        if not self._token:
            await self.authenticate()

        order = self._build_order(device_id, position)
        try:
            result = await self._post(
                SEND_ORDER_URL,
                headers={"token": self._token},
                data={"deviceId": gateway_mac, "order": order},
            )
        except aiohttp.ClientError as err:
            raise VelaSmartApiError(f"Network error: {err}") from err

        if result.get("code") != 200:
            raise VelaSmartApiError(f"Command failed: {result}")

    @staticmethod
    def _build_order(device_id: str, position: int) -> str:
        """Build the hex command payload for a device position change."""
        hex_device = binascii.hexlify(device_id.encode("utf-8")).decode("ascii")
        hex_height = f"{position:02X}"
        res = f"01 {hex_device} 02 {hex_height}"
        res_compact = res.replace(" ", "")
        length = len(res_compact.encode("ascii")) // 2
        hex_length = f"{length:02X}"
        order = f"4A640040FF{hex_length}00{res_compact}"
        return order + VelaSmartApiClient._make_checksum(order)

    @staticmethod
    def _make_checksum(data: str) -> str:
        """Calculate the byte checksum appended to a command."""
        if not data:
            return ""
        total = sum(int(data[i : i + 2], 16) for i in range(0, len(data), 2))
        return f"{total % 256:02X}"
