# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2023 viso.ai AG <info@viso.ai>
"""
Testing module for the status logger
"""
import json
import time

import pytest

from viso_sdk.constants import PREFIX
from viso_sdk.mqtt.mqtt_wrapper import MqttWrapper as VisoMqtt
from viso_sdk.redis.redis_wrapper import RedisWrapper as VisoRedis
from viso_sdk.logging import get_status_logger

NODE_ID = "638acaf9.bf6014"
mqtt_received = False
test_error_msg = "test_error_msg"


@pytest.fixture
def status_logger():
    sl = get_status_logger(node_id=NODE_ID, node_name="", node_type="object-detection")
    sl.start()
    return sl


@pytest.fixture
def viso_redis():
    return VisoRedis()


def on_mqtt_error_message(recv_msg):
    global mqtt_received
    mqtt_received = True
    msg = json.loads(recv_msg)
    assert msg["id"] == NODE_ID
    assert msg["type"] == "object-detection"
    assert msg["msg"] == test_error_msg


def test_status_logger(status_logger, viso_redis: VisoRedis):

    mqtt = VisoMqtt(callbacks={f"{PREFIX.MQTT.CLOUD}_{NODE_ID}": on_mqtt_error_message})

    status_logger.update_status_info(info={"fps": 5}, source_idx=3)
    time.sleep(2)

    b_status = viso_redis.read_data(redis_key=f"{PREFIX.REDIS.STATUS}_{NODE_ID}")
    assert b_status is not None
    status = json.loads(b_status.decode())

    assert status["id"] == NODE_ID
    assert len(status["fps"]) == 4
    assert status["fps"][3] == 5

    while not mqtt_received:
        status_logger.error(test_error_msg)
        time.sleep(1)
    mqtt.stop()
    mqtt.join(0.5)
    status_logger.stop()
    status_logger.join(0.5)
