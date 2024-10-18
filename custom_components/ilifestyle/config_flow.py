from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow

from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_ID,
    CONF_TOKEN,
    CONF_URL,
    CONF_NAME,
)

from .const import DOMAIN
from .api import (
    LocalAPI,
    CloudAPI,
    APIAuthError,
    APIConnectionError
)

class SmartmeConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.api: None

    async def async_step_user(self, formdata):
        if formdata is not None:
            ipaddress = formdata[CONF_IP_ADDRESS]
            username = formdata[CONF_USERNAME]
            password = formdata[CONF_PASSWORD]

            try:
                api = LocalAPI(self.hass, ipaddress=ipaddress)
                await api.login(username=username, password=password)
                cloud_token = await api.getCloudToken()
                deviceid = await api.getDeviceId()
                name = await api.getDeviceType()

                #set video mode to rtmp
                cloud = CloudAPI(self.hass, token=cloud_token)
                await cloud.setDeviceVideoTransfer(deviceid)
                
                video_url = await api.getVideoUrl()

                await self.async_set_unique_id(deviceid, raise_on_progress=False)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"iLifestyle {name}", data={
                    CONF_DEVICE_ID: deviceid,
                    CONF_TOKEN: cloud_token,
                    CONF_URL: video_url,
                    CONF_NAME: name,
                    CONF_IP_ADDRESS: ipaddress,
                })
            except APIAuthError as err:
                return self.async_abort(reason="authentication")
            except APIConnectionError as err:
                return self.async_abort(reason="connenction")
        
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str
            })
        )
