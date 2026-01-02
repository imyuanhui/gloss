import time
from typing import Callable, Type, Tuple

def retry(
    fn: Callable,
    exceptions: Tuple[Type[BaseException], ...],
    attempts: int = 3,
    backoff_seconds: float = 0.2,
):
    last = None
    for i in range(attempts):
        try:
            return fn()
        except exceptions as e:
            last = e
            time.sleep(backoff_seconds * (i + 1))
    raise last
