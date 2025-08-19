"""
Redis Wrapper from viso.ai
"""
import json
import threading
import atexit
import queue
from typing import Any, Optional, Union
import cv2  # type: ignore
import redis
from concurrent.futures import ThreadPoolExecutor


from viso_sdk.logging.logger import get_logger


logger = get_logger("REDIS")


class RedisWrapper:
    """Represents a redis client specified for the containers.

    Args:
        thread(bool): Use threading or not
        host(str): Redis server host
        port(int): Redis server port
    """

    def __init__(
            self,
            thread: bool = True,
            host: str = "localhost",
            port: int = 6379,
            workers: int = 2,
    ):
        self._use_thread = thread
        self._redis_client = redis.StrictRedis(host, port)
        # Use a single background worker with a bounded queue to minimize CPU and context switching.
        self._executor: Optional[ThreadPoolExecutor] = None  # kept for backward compatibility
        self._queue: Optional[queue.Queue] = None
        self._worker: Optional[threading.Thread] = None
        self._stop_evt = threading.Event()
        if self._use_thread:
            self._queue = queue.Queue(maxsize=max(1, int(workers)))  # allow tuning buffer size; default 1
            self._worker = threading.Thread(target=self._worker_loop, name="RedisWrapperWorker", daemon=True)
            self._worker.start()
            atexit.register(self._shutdown_executor)

        _img_arr = None

    def _shutdown_executor(self):
        try:
            # Signal worker to stop and drain
            self._stop_evt.set()
            if self._worker is not None:
                self._worker.join(timeout=0.5)
            self._queue = None
            self._executor = None
            self._use_thread = False
        except Exception:
            pass

    def _worker_loop(self):
        while not self._stop_evt.is_set():
            try:
                item = self._queue.get(timeout=0.2)
            except Exception:
                continue
            try:
                data, redis_key, ttl = item
                self._write_(data, redis_key, ttl)
            finally:
                try:
                    self._queue.task_done()
                except Exception:
                    pass

    def _write_(
            self,
            data: dict,
            redis_key: str,
            ttl: Optional[int] = None,
    ) -> bool:
        """
        Internal function that is executed in background thread
        Args:
            data,
            redis_key:
        Returns:

        """
        if isinstance(data, dict):
            str_as_data = json.dumps(data)
        elif data is None:
            return bool(self._redis_client.delete(redis_key))
        else:
            str_as_data = data

        try:
            return bool(self._redis_client.set(redis_key, str_as_data, ex=ttl))
        except Exception as err:
            logger.error(f"Failed to write data to redis`{redis_key}` - {err}")
        return False

    def write_viso_data(
            self,
            data: dict,
            redis_key: str,
            ttl: Optional[int] = None,
    ) -> bool:
        """
        Write video frame to the target redis key
        Args:
                data:
                redis_key(str): Target redis key.
        """
        if self._use_thread and self._queue is not None:
            # Drop-older policy: if queue is full, remove one item and enqueue the latest
            try:
                self._queue.put_nowait((data, redis_key, ttl))
                return True
            except queue.Full:
                try:
                    _ = self._queue.get_nowait()
                    self._queue.task_done()
                except Exception:
                    pass
                try:
                    self._queue.put_nowait((data, redis_key, ttl))
                    return True
                except Exception:
                    # Fallback to sync write if still cannot enqueue
                    return self._write_(data, redis_key, ttl)
        return self._write_(data, redis_key, ttl)

    def delete_data(self, redis_key: str) -> bool:
        """Delete data from the target redis location

        Args:
            redis_key(str): Target redis key.
        """
        return bool(self._redis_client.delete(redis_key))

    def write_data(self, redis_key: str, data: Union[str, dict], ttl: Optional[int] = None) -> bool:
        """Write data to the target redis location

        Args:
            redis_key(str): Target redis key.
            data(str): Data to be written.
        """
        if isinstance(data, dict):
            return bool(self._redis_client.set(redis_key, json.dumps(data), ex=ttl))
        else:
            return bool(self._redis_client.set(redis_key, data, ex=ttl))

    def read_data(self, redis_key: str) -> Any:
        """Read data from the target redis location

        Args:
            redis_key(str): Target redis key.
        """
        return self._redis_client.get(redis_key)

    def read_viso_data(
            self,
            redis_key: str,
    ):
        """Read video frame from a given redis key

        Args:
            redis_key(str): Target redis key.
        """
        try:
            data = self.read_data(redis_key=redis_key)
            if isinstance(data, bytes):
                return json.loads(data.decode())
            return data
        except Exception as err:
            logger.warning(f"Failed to get redis frame from {redis_key} - {err}")
        return None
