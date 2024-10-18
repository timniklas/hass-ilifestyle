from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.device_registry import DeviceInfo

_LOGGER = logging.getLogger(__name__)

from .mqtt import LifestyleMqtt
from .const import DOMAIN
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_TOKEN,
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up a Buttons."""
    async_add_entities([
        CallButton(hass, config_entry),
        OpenButton(hass, config_entry)
    ], True)

class CallButton(ButtonEntity):

    _attr_has_entity_name = True
    _attr_translation_key = "callbutton"
    _attr_icon = "mdi:video"

    def __init__(self, hass, config_entry):
        """Initialize."""
        super().__init__()
        self._deviceid = config_entry.data[CONF_DEVICE_ID]
        self._token = config_entry.data[CONF_TOKEN]
        self._mqtt_client = LifestyleMqtt(mqtt_username=self._deviceid, mqtt_password=self._token)
        self.unique_id = f"{config_entry.data[CONF_DEVICE_ID]}-{self._attr_translation_key}"
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.data[CONF_DEVICE_ID])}
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._mqtt_client.call_door()

class OpenButton(ButtonEntity):

    _attr_has_entity_name = True
    _attr_translation_key = "openbutton"
    _attr_icon = "mdi:door-open"

    def __init__(self, hass, config_entry):
        """Initialize."""
        super().__init__()
        self._deviceid = config_entry.data[CONF_DEVICE_ID]
        self._token = config_entry.data[CONF_TOKEN]
        self._mqtt_client = LifestyleMqtt(mqtt_username=self._deviceid, mqtt_password=self._token)
        self.unique_id = f"{config_entry.data[CONF_DEVICE_ID]}-{self._attr_translation_key}"
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.data[CONF_DEVICE_ID])}
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._mqtt_client.open_door()
