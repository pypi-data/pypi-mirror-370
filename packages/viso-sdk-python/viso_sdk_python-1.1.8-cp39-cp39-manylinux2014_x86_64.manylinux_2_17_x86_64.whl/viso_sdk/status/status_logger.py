"""Status Caching of containers"""

import json
import threading
import time
from typing import Any, Dict

from viso_sdk.logging import get_logger
from viso_sdk.mqtt.mqtt_wrapper import MqttWrapper as VisoMqtt
from viso_sdk.redis.redis_wrapper import RedisWrapper as VisoRedis
from viso_sdk.redis.utils import gen_redis_key_status
from viso_sdk.constants import PREFIX, NODE_ID, NODE_TYPE


# Interval of the status logging module
STATUS_LOG_INTERVAL: int = 60


logger = get_logger(name="STATUS")


class StatusCaching(threading.Thread):
    """Status logger class

    Args:
        node_id(str): Id of the target node. Use NODE_ID env variable normally.
        node_name(str): Target node name.
        node_type(str): Target node type.
        log_interval(int): Interval of the status logger. Default value is 60 sec.
    """

    def __init__(
            self,
            node_id: str = "",
            node_name: str = "",
            node_type: str = "",
            log_interval: int = STATUS_LOG_INTERVAL,
            verbose=False
    ):
        super().__init__()
        self.node_id = node_id
        self.node_name = node_name
        self.node_type = node_type
        self.log_interval = log_interval
        self._status_buf: Dict[str, Any] = {
            "ts": 0,
            "id": node_id,
            "name": node_name,
            "msg_type": "info",
            "type": node_type,
        }
        self._error_buf: Dict[str, Any] = {}
        self._b_stop = threading.Event()
        self._b_stop.clear()

        self.verbose = verbose

    def run(self) -> None:
        last_status_log_ts: float = 0.0
        last_error_log_ts: float = 0.0
        mqtt = VisoMqtt()
        redis = VisoRedis()

        while not self._b_stop.is_set():

            if self._error_buf and time.time() - last_error_log_ts > self.log_interval:
                # Publish to the CLOUD MQTT topic so that this is redirected to the telegraf by emqx
                mqtt.publish(
                    topic=f"{PREFIX.MQTT.CLOUD}_{self.node_id}",
                    message=json.dumps(self._error_buf),
                )
                logger.warning(
                    f"Published error message to MQTT - {json.dumps(self._error_buf)}"
                )
                self._error_buf = {}
                last_error_log_ts = time.time()

            if time.time() - last_status_log_ts > self.log_interval:
                # Publish to the DEBUG MQTT topic.
                mqtt.publish(
                    topic=f"{PREFIX.MQTT.DEBUG}_{self.node_id}",
                    message=json.dumps(self._status_buf),
                )
                # Write data to redis
                redis.write_data(
                    redis_key=gen_redis_key_status(node_id=self.node_id),
                    data=json.dumps(self._status_buf),
                )
                if self.verbose:
                    logger.info(f"publish message - {json.dumps(self._status_buf)}")
                last_status_log_ts = time.time()

            time.sleep(0.1)
        mqtt.stop()
        mqtt.join(0.5)

    def update_status_info(self, info: dict, source_idx: int) -> None:
        """Update status buf

        Args:
            info(dict): New buf to be updated
            source_idx(int): Source index number.
        """
        # Inject data to correct position by using source_idx
        self._status_buf['ts'] = time.time().__int__()
        for k, val in info.items():
            old_val = self._status_buf.get(k)

            if old_val is None:
                self._status_buf[k] = [val]
            elif isinstance(old_val, list):
                if len(old_val) < source_idx + 1:
                    old_val.extend(["" for _ in range(source_idx + 1 - len(old_val))])
                old_val[source_idx] = val
                self._status_buf[k] = old_val
            else:
                old_val = self._status_buf.get(k)
                self._status_buf[k] = val

        if self.verbose or True:
            logger.info(f"Status info: {self._status_buf}")

    def update_error_info(self, msg: str) -> None:
        """Update error buf with given message"""
        self._error_buf = {
            "ts": time.time().__int__(),
            "id": self.node_id,
            "name": self.node_name,
            "type": self.node_type,
            "msg_type": "error",
            "message": msg,
        }
        logger.warning(f"Updated error buf - {self._error_buf}")

    @staticmethod
    def info(msg: str) -> None:
        """Just call this function to add a status info"""
        logger.info(msg)

    @staticmethod
    def warning(msg: str) -> None:
        """Just call this function to add a status warning"""
        logger.warning(msg)

    def error(self, msg: str) -> None:
        """Add status error log(and will be published)"""
        self.update_error_info(msg=msg)

    def stop(self) -> None:
        """Stop this thread"""
        self._b_stop.set()


def get_status_logger(node_id=None, node_name="", node_type=""):
    if node_id is None:
        node_id = NODE_ID
    if node_type is None:
        node_type = NODE_TYPE
    status_logger = StatusCaching(node_id, node_name, node_type)
    # status_logger.start()
    return status_logger
