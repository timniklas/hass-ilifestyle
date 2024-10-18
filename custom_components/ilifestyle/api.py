from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import logging
from random import choice, randrange

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import ClientError, ClientResponseError, ClientSession
from homeassistant.core import HomeAssistant

import json

_LOGGER = logging.getLogger(__name__)

class LocalAPI:
    """Class for API."""

    def __init__(self, hass: HomeAssistant, ipaddress: str) -> None:
        """Initialise."""
        self._ipaddress = ipaddress
        self._session = async_get_clientsession(hass)
        self._token: None = None

    async def login(self, username: str, password: str):
        try:
            async with self._session.post(f"http://{self._ipaddress}/api/login", json={"name": username,"password": password}) as response:
                response.raise_for_status()
                response_json = await response.json()
                if(response_json['status'] != 0):
                    raise APIAuthError("Error connecting to api. Invalid username or password.")
                
                self._token = response_json['token']
                return True
        except ClientError as exc:
            raise APIConnectionError("Error connecting to api.")

    async def getCloudToken(self):
        if self._token is None:
            raise APIAuthError("Please login first.")

        try:
            async with self._session.get(f"http://{self._ipaddress}/api/account", cookies = {"token": self._token}) as response:
                response.raise_for_status()
                response_json = await response.json()
                if(response_json['status'] != 0):
                    raise APIConnectionError("Invalid response from api.")

                return response_json['token']
        except ClientError as exc:
            raise APIConnectionError("Could not get cloud token.")

    async def getDeviceId(self):
        if self._token is None:
            raise APIAuthError("Please login first.")

        try:
            async with self._session.get(f"http://{self._ipaddress}/api/mac", cookies = {"token": self._token}) as response:
                response.raise_for_status()
                response_json = await response.json()
                if(response_json['status'] != 0):
                    raise APIConnectionError("Invalid response from api.")

                return response_json['mac'].replace(':', '')
        except ClientError as exc:
            raise APIConnectionError("Could not get device id.")

    async def getDeviceType(self):
        if self._token is None:
            raise APIAuthError("Please login first.")

        try:
            async with self._session.get(f"http://{self._ipaddress}/api/device", cookies = {"token": self._token}) as response:
                response.raise_for_status()
                response_json = await response.json()
                if(response_json['status'] != 0):
                    raise APIConnectionError("Invalid response from api.")

                return response_json['type']
        except ClientError as exc:
            raise APIConnectionError("Could not get device type.")

    async def getVideoUrl(self):
        if self._token is None:
            raise APIAuthError("Please login first.")

        try:
            async with self._session.get(f"http://{self._ipaddress}/api/video", cookies = {"token": self._token}) as response:
                response.raise_for_status()
                response_json = await response.json()
                if(response_json['status'] != 0):
                    raise APIConnectionError("Invalid response from api.")

                return response_json['rtmp']
        except ClientError as exc:
            raise APIConnectionError("Could not get video url.")

class CloudAPI:
    """Class for API."""

    def __init__(self, hass: HomeAssistant, token: str) -> None:
        """Initialise."""
        self._token = token
        self._session = async_get_clientsession(hass)

    async def setDeviceVideoTransfer(self, device: str, mode: int = 1):
        if self._token is None:
            raise APIAuthError("Please login first.")

        try:
            async with self._session.put(f"http://de.ilifestyle-cloud.com/api/device/{device}", headers={"Authorization": self._token}, json={"video_transfer": mode}) as response:
                response.raise_for_status()
                response_json = await response.json()
                if(response_json['code'] != 0):
                    raise APIConnectionError("Invalid response from api.")

                return True
        except ClientError as exc:
            raise APIConnectionError("Could not set video transfer mode of device.")

class APIAuthError(Exception):
    """Exception class for auth error."""

class APIConnectionError(Exception):
    """Exception class for connection error."""
