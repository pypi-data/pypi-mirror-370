import time
from viso_sdk.status import get_status_logger


if __name__ == '__main__':
    _status_logger = get_status_logger(
        node_id="id",
        node_name="name",
        node_type="type")

    _status_logger.start()
    while True:
        _status_logger.update_status_info(
            info={
                'ts': time.time(),
                'fps': '10.0', 'input': {'frame_size': '1920x1080'}
            },
            source_idx=0
        )
        time.sleep(1)
        _status_logger.update_status_info(
            info={
                'ts': time.time(),
                'fps': '20.', 'input': {'frame_size': '640x480'}
            },
            source_idx=1
        )
        time.sleep(1)
        _status_logger.update_error_info("error")
