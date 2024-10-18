from __future__ import annotations

import paho.mqtt.client as mqtt
import asyncio

import logging

_LOGGER = logging.getLogger(__name__)

class LifestyleMqtt:
    """Class for MQTT client."""

    def __init__(self, mqtt_username: str, mqtt_password: str) -> None:
        """Initialise."""
        self._client = mqtt.Client(client_id = "Phone|" + mqtt_username, protocol = mqtt.MQTTv5, transport = "tcp")
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc==0:
            _LOGGER.info("Connected to iLifestyle MQTT Broker")
        else:
            _LOGGER.error("Connection to iLifestyle MQTT Broker failed:", rc)

    async def _publish(self, data: str):
        self._client.username_pw_set(username = self.mqtt_username, password = self.mqtt_password)
        self._client.on_connect = self._on_connect
        self._client.connect(host = "de.ilifestyle-cloud.com", port = 1883)
        self._client.loop_start();
        await asyncio.sleep(0.1) #wait for connection

        #publish the data
        self._client.publish(self.mqtt_username, data)

        # disconnect
        self._client.loop_stop()
        self._client.disconnect()
    
    async def call_door(self, duration: int = 60):
        return await self._publish('{"action": "monitor","ctrl":"1","key_index": 1,"duration":' + str(duration) + '}')
    
    async def open_door(self):
        return await self._publish('{"action": "OPEN DOOR"}')
