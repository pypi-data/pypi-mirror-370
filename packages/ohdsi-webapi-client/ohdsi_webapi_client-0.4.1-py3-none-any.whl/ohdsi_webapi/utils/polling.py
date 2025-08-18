from __future__ import annotations

import time
from typing import Callable

from ..exceptions import JobTimeoutError


class Poller:
    def __init__(self, interval: float = 2.0, timeout: float = 600.0):
        self.interval = interval
        self.timeout = timeout

    def poll(self, fn: Callable[[], str], is_terminal: Callable[[str], bool]) -> str:
        start = time.time()
        while True:
            status = fn()
            if is_terminal(status):
                return status
            if time.time() - start > self.timeout:
                raise JobTimeoutError(f"Job did not finish within {self.timeout} seconds")
            time.sleep(self.interval)
