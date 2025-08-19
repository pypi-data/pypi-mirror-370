import threading
import time
import paho.mqtt.client as mqttc
import paho.mqtt as mqtt
from paho.mqtt.client import CallbackAPIVersion
import json
from typing import Optional  # Any, Union


from viso_sdk.logging import get_logger

logger = get_logger(name="MQTT")


DEFAULT_MQTT_HOST = "127.0.0.1"
DEFAULT_MQTT_PORT = 1883


mqtt_v = mqtt.__version__
if mqtt_v[0] < '2':
    logger.info(f"mqtt version is {mqtt_v} ")


class MqttWrapper(threading.Thread):
    def __init__(self,
                 host: Optional[str] = DEFAULT_MQTT_HOST,
                 port: Optional[int] = DEFAULT_MQTT_PORT,
                 subscribe_topics: Optional[list] = None,
                 verbose: Optional[bool] = False,
                 username=None,
                 password=None):
        super().__init__()
        callbacks = {}
        if subscribe_topics is None:
            subscribe_topics = []
        for topic in subscribe_topics:
            if topic is not None:
                callbacks[topic] = self._on_viso_msg_listen
        self.callbacks: dict = callbacks or {}

        self.host = host
        self.port = port
        self.verbose = verbose

        # TODO: DeprecationWarning: Callback API version 1 is deprecated, update to latest version
        if mqtt_v[0] < '2':
            self.client = mqttc.Client()
        else:
            self.client = mqttc.Client(callback_api_version=CallbackAPIVersion.VERSION1)

        # Set username and password if provided
        self._username = username
        self._password = password
        if username and password:
            self.client.username_pw_set(self._username, self._password)

        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_publish = self._on_publish
        self.client.on_message = self._on_message

        self._b_stop = threading.Event()
        self._b_stop.clear()
        self._lock = threading.Lock()

        self.msg_subscribed = {}

        self.start()

    def connect(self):
        try:
            self.client.connect(host=self.host, port=self.port)
        except Exception as err:
            logger.error(f"Failed to connect to {self.host}:{self.port} - {err}")
            return False
        self.client.loop_start()
        return True

    def run(self) -> None:
        """Main thread loop"""
        while not self._b_stop.is_set():
            # Check MQTT connection and connect if not.
            if not self.client.is_connected():
                self.connect()
            time.sleep(1)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    # def _on_mqtt_connected(self, *args: Any) -> None:
    #     rc = args[-1]
    #     print("Connected with result code " + str(rc))
    def _on_connect(self, client, userdata, flags, rc):
        # Subscribe to topics here if needed
        logger.info(f"Connected with result code {rc}")
        if rc == 0:  # Check ResultCode
            for topic in self.callbacks.keys():
                self.subscribe(topic=topic)

    # def _on_mqtt_message(self, *args: Any) -> None:
    #     print("Received message: " + msg.topic + " " + str(msg.payload))
    def _on_message(self, client, userdata, msg):
        """Callback when a message on subscribed channels is received."""
        topic = msg.topic
        _msg = msg.payload.decode("utf-8")
        if self.verbose:
            logger.info(f"Received a message(`{_msg}`) on topic: `{topic}`")
        if callable(self.callbacks.get(topic)):
            # Call corresponding callback function with the message payload as an argument.
            self.callbacks[topic](topic=topic, msg=_msg)
        else:
            logger.error(f"Callback of topic '{topic}' is not callable!")

    # def on_publish(self, client, userdata, mid):
    #     print("Message published.")
    def _on_publish(self, client, userdata, mid) -> None:
        """Publish a message to a topic"""
        published_msg_id = mid
        if self.verbose:
            logger.info(f"Published message with ID: {published_msg_id}")

    def publish(self, topic, message):
        _, mid = self.client.publish(topic, message)
        return self.client.is_connected(), mid

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)

    def stop(self) -> None:
        """Stop this thread"""
        self._b_stop.set()

    def _on_viso_msg_listen(self, topic, msg):
        try:
            resp = json.loads(msg)
        except Exception as e:
            logger.error(f"Failed to parse subscribed message({msg}) - {e}")
            return
        with self._lock:
            if "source_key" in resp.keys():

                # TODO: for redis met info (after removing mqtt prt)
                # source_key = f"{REDIS_PREFIX}_{node_id}_{source_idx + 1}"
                # self.msg_subscribed[f"{resp['source_key']}"] = resp

                self.msg_subscribed[topic] = resp
            else:
                self.msg_subscribed[0] = resp

    def get_last_published_msg(self):
        try:
            return self.msg_subscribed
        except Exception as e:
            if self.verbose:
                logger.warning(e)
            return {}
