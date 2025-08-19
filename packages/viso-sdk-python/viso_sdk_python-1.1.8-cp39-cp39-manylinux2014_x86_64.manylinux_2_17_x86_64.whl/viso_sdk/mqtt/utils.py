import time

from viso_sdk.constants import PREFIX
from viso_sdk.constants import NODE_ID, NODE_TYPE


class Category:
    info = "info"
    error = "error"
    warning = "warning"


def gen_mqtt_key_local(node_id):
    return f"{PREFIX.MQTT.LOCAL}_{node_id}"


def meta_info_to_publish(
        source_name,
        source_id,
        source_idx=0,
        result=None,
        node_id=NODE_ID,
        node_type=NODE_TYPE,
        infer_t=0,
        category='info'
):

    if result is None:
        result = []
    payload = {
        "source_id": source_id,
        "source_name": source_name,
        "source_key": f"{source_id}_{source_idx}",
        "source_idx": source_idx,
        "ts": time.time(),
        "id": node_id,
        "type": node_type,
        "result": result,
        "inference time(sec)": round(infer_t, 4),
        "category": category
    }
    return payload
