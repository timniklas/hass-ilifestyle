from __future__ import annotations

import logging

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

_LOGGER = logging.getLogger(__name__)

from .coordinator import MqttCoordinator
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
    # This gets the data update coordinator from hass.data as specified in your __init__.py
    coordinator: MqttCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ].coordinator

    async_add_entities([
        CallButton(config_entry, coordinator),
        HangupButton(config_entry, coordinator),
        OpenButton(config_entry, coordinator)
    ], True)

class CallButton(CoordinatorEntity):

    _attr_has_entity_name = True
    _attr_translation_key = "callbutton"
    _attr_icon = "mdi:video"

    def __init__(self, config_entry: ConfigEntry, coordinator: MqttCoordinator):
        """Initialize."""
        super().__init__(coordinator)
        self.unique_id = f"{config_entry.data[CONF_DEVICE_ID]}-{self._attr_translation_key}"
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.data[CONF_DEVICE_ID])}
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    async def _async_press_action(self) -> None:
        """Handle the button press."""
        await self.coordinator.call_door()

    @property
    def available(self) -> bool:
        """Return the state of the sensor."""
        return self.coordinator.data.connected

class HangupButton(CoordinatorEntity):

    _attr_has_entity_name = True
    _attr_translation_key = "hangupbutton"
    _attr_icon = "mdi:video-off"

    def __init__(self, config_entry: ConfigEntry, coordinator: MqttCoordinator):
        """Initialize."""
        super().__init__(coordinator)
        self.unique_id = f"{config_entry.data[CONF_DEVICE_ID]}-{self._attr_translation_key}"
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.data[CONF_DEVICE_ID])}
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    async def _async_press_action(self) -> None:
        """Handle the button press."""
        await self.coordinator.hangup_door()

    @property
    def available(self) -> bool:
        """Return the state of the sensor."""
        return self.coordinator.data.connected

class OpenButton(CoordinatorEntity):

    _attr_has_entity_name = True
    _attr_translation_key = "openbutton"
    _attr_icon = "mdi:door-open"

    def __init__(self, config_entry: ConfigEntry, coordinator: MqttCoordinator):
        """Initialize."""
        super().__init__(coordinator)
        self.unique_id = f"{config_entry.data[CONF_DEVICE_ID]}-{self._attr_translation_key}"
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.data[CONF_DEVICE_ID])}
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    async def _async_press_action(self) -> None:
        """Handle the button press."""
        await self.coordinator.open_door()

    @property
    def available(self) -> bool:
        """Return the state of the sensor."""
        return self.coordinator.data.connected
