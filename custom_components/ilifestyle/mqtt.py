from __future__ import annotations

import paho.mqtt.client as mqtt
import asyncio

import logging

_LOGGER = logging.getLogger(__name__)

class LifestyleMqtt:
    """Class for MQTT client."""

    def __init__(self, mqtt_username: str, mqtt_password: str, alias: str = "HomeAssistant") -> None:
        """Initialise."""
        self.connected = False
        self._topic = mqtt_username
        self._client = mqtt.Client(client_id = alias + "|" + mqtt_username, protocol = mqtt.MQTTv5, transport = "tcp")
        self._client.username_pw_set(username = mqtt_username, password = mqtt_password)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code==0:
            self.connected = True
            _LOGGER.info("Connected to iLifestyle MQTT Broker")
        else:
            self.connected = False
            _LOGGER.error("Connection to iLifestyle MQTT Broker failed:", rc)

    def _on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        self.connected = False
        self.connect()

    def connect(self):
        if self.connected == False:
            self._client.connect(host = "de.ilifestyle-cloud.com", port = 1883)
            self._client.loop_start()

    async def _publish(self, data: str):
        if self.connected == False:
            raise MQTTConnectionError("Not connected to mqtt broker.")

        #publish the data
        self._client.publish(self._topic, data)
    
    async def call_door(self, duration: int = 60):
        return await self._publish('{"action": "monitor","ctrl":"1","key_index": 1,"duration":' + str(duration) + '}')
    
    async def open_door(self):
        return await self._publish('{"action": "OPEN DOOR"}')

class MQTTConnectionError(Exception):
    """Exception class for connection error."""
