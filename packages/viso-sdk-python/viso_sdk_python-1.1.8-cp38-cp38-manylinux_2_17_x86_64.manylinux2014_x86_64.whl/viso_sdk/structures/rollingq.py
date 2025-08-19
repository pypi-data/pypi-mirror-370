import queue
from typing import Any
from viso_sdk.logging import get_logger

class RollingQueue(queue.Queue):
    """
    thread safe rolling queue
    """         
    def __init__(self, batch_size: int, debug = False) -> None:
        super().__init__(maxsize=batch_size)
        self.debug = debug
        if debug:
            self.logger = get_logger("RQ: ")
    
    def put(self, item: Any, block: bool = True, timeout: float | None = None) -> None:  # noqa: D401
        with self.mutex:  
            if self._qsize() == self.maxsize:
                if self.debug:
                    self.logger.warning("Throwing away element")
                self._get()
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    def drain_fast(self, max_items: int, *,
                   dest_factory=list, adjust_unfinished=True):
        """
        Bulk-move up to *max_items* items out of *self* under its
        internal mutex.  10–30× faster than calling `get_nowait()` in a loop
        because the lock is taken only once.

        *adjust_unfinished* keeps `queue.join()` semantics intact.
        """
        with self.mutex:                        # one lock, atomic view
            n = min(max_items, len(self.queue))
            dest = dest_factory(self.queue.popleft() for _ in range(n))

            if adjust_unfinished and self.unfinished_tasks:
                self.unfinished_tasks -= n
                if self.unfinished_tasks == 0:
                    self.all_tasks_done.notify_all()

        return dest
