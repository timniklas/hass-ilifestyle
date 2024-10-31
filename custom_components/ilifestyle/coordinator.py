from dataclasses import dataclass
from datetime import timedelta
import logging

import re
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_TOKEN
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .mqtt import LifestyleMqtt

_LOGGER = logging.getLogger(__name__)

@dataclass
class MqttData:
    """Class to hold api data."""

    connected: bool
    transmitting: bool

class MqttCoordinator(DataUpdateCoordinator):
    """My coordinator."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        deviceid = config_entry.data[CONF_DEVICE_ID]
        token = config_entry.data[CONF_TOKEN]

        self._hass = hass
        self.mqtt_client = LifestyleMqtt(mqtt_username=deviceid, mqtt_password=token, callback=self._updateConnection)
        self.transmitting = False

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Set update method to get devices on first load.
            update_method=self.async_update_data,
            # Do not set a polling interval as data will be pushed.
            # You can remove this line but left here for explanatory purposes.
            update_interval=None,
        )

    def _updateData(self):
        self.async_set_updated_data(MqttData(self.mqtt_client.connected, self.transmitting))
    
    def _updateConnection(self):
        self._updateData()
        self._hass.bus.fire("ilifestyle_connection_event", {"connected": self.mqtt_client.connected})
    
    async def _updateTransmission(self, state: bool):
        if state != self.transmitting: #ignore double fires
            self.transmitting = state
            self._updateData()
            self._hass.bus.fire("ilifestyle_transmission_event", {"transmission": self.transmitting})

    async def _transmit(self, duration: int = 60):
        await self._updateTransmission(True)
        await asyncio.sleep(duration)
        await self._updateTransmission(False)

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        if self.mqtt_client.connected == False:
            self.mqtt_client.connect()
        
        return MqttData(self.mqtt_client.connected, self.transmitting)

    async def call_door(self, duration: int = 60):
        await self.mqtt_client.call_door(duration)
        await self._transmit(duration)
    
    async def open_door(self):
        await self.mqtt_client.open_door()
        await self._updateTransmission(False)
    
    async def hangup_door(self):
        await self.mqtt_client.hangup_door()
        await self._updateTransmission(False)
