from __future__ import annotations

from haffmpeg.camera import CameraMjpeg
from haffmpeg.tools import IMAGE_JPEG

from homeassistant.config_entries import ConfigEntry

from homeassistant.components import ffmpeg
from homeassistant.components.camera import (
    Camera,
    CameraEntityFeature,
)
from homeassistant.components.ffmpeg import get_ffmpeg_manager
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_aiohttp_proxy_stream
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MqttCoordinator
from .const import DOMAIN
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_URL,
    CONF_NAME,
    CONF_IP_ADDRESS,
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up a Camera."""
    # This gets the data update coordinator from hass.data as specified in your __init__.py
    coordinator: MqttCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ].coordinator

    async_add_entities([LifestyleCamera(hass, config_entry, coordinator)], True)


class LifestyleCamera(CoordinatorEntity, Camera):

    _attr_has_entity_name = True
    _attr_translation_key = "video"
    _attr_supported_features = CameraEntityFeature.STREAM
    _options = "-pred 1"

    def __init__(self, hass, config_entry, coordinator):
        """Initialize."""
        super().__init__(coordinator)
        Camera.__init__(self)
        self._manager = get_ffmpeg_manager(hass)
        self._url = config_entry.data[CONF_URL]
        self.unique_id = f"{config_entry.data[CONF_DEVICE_ID]}-{self._attr_translation_key}"
        self.device_info = DeviceInfo(
            #only generate device once!
            model=config_entry.data[CONF_NAME],
            serial_number=config_entry.data[CONF_DEVICE_ID],
            configuration_url=f"http://{config_entry.data[CONF_IP_ADDRESS]}",
            name=f"iLifestyle {config_entry.data[CONF_NAME]}",
            manufacturer="HHG GmbH",
            identifiers={(DOMAIN, config_entry.data[CONF_DEVICE_ID])}
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return the state of the sensor."""
        return self.coordinator.data.connected

    @property
    def is_streaming(self) -> bool:
        """Return the state of the sensor."""
        return self.coordinator.data.transmitting

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        return self.coordinator.data.transmitting

    async def stream_source(self) -> str:
        """Return the stream source."""
        return self._url.split(" ")[-1]

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""
        
        return await ffmpeg.async_get_image(
            self.hass,
            self._url,
            output_format=IMAGE_JPEG,
            extra_cmd=self._options,
        )

    async def handle_async_mjpeg_stream(self, request):
        """Generate an HTTP MJPEG stream from the camera."""

        stream = CameraMjpeg(self._manager.binary)
        await stream.open_camera(self._url, extra_cmd=self._options)

        try:
            stream_reader = await stream.get_reader()
            return await async_aiohttp_proxy_stream(
                self.hass,
                request,
                stream_reader,
                self._manager.ffmpeg_stream_content_type,
            )
        finally:
            await stream.close()
