import paho.mqtt.client as mqtt
import logging
import json

import sys
import os
sys.path.append(os.getcwd())

from App.Controllers.API import ApiController, CageController, DailyActivityController, IoTController

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self, app=None):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message 
        self.connected = False

        if app:
            self.init_app(app)

    def init_app(self, app):
        broker_host = os.getenv('BROKER_HOST')
        broker_port = int(os.getenv('BROKER_PORT', 1883))
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.connected = True
        except Exception as e:
            logger.info(f"Failed to connect to MQTT broker at {self.broker_host}:{self.broker_port}")
            logger.error(f"Failed to connect MQTT broker: {e}")
            self.connected = False

    def disconnect(self):
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
            self.connected = False

    def publish(self, topic, message, qos=1, retain=False):
        if not self.connected:
            logger.warning("MQTT client not connected, trying to reconnect...")
            self.connect()
        result = self.client.publish(topic, message, qos=qos, retain=retain)
        if result.rc != 0:
            logger.error(f"Failed to publish message to {topic}")
        else:
            logger.info(f"Published message to {topic}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connected successfully")
            self.connected = True
        else:
            logger.error(f"MQTT connection failed with code {rc}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc):
        logger.info("MQTT disconnected")
        self.connected = False

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload_raw = msg.payload.decode()
        logger.info(f"Received message: {topic} = {payload_raw}")

        try:
            payload = json.loads(payload_raw)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON payload: {payload_raw}")
            return

        parts = topic.split('/')
        if len(parts) < 3:
            logger.warning(f"Ignored invalid topic: {topic}")
            return
        
        handler = None
        base = parts[2]
        if base == "status":
            handler = IoTController.insert_device_status
            # handler(payload)
        else:
            handler = IoTController.insert_device_data

        handler(payload)


    def subscribe(self, topic, qos=1):
        if not self.connected:
            self.connect()
        self.client.subscribe(topic, qos)
        logger.info(f"Subscribed to topic {topic} with QoS {qos}")


mqtt_client = MQTTClient()
