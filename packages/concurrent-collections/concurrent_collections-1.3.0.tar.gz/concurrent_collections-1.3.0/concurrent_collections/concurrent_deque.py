import threading
from collections import deque
from typing import Generic, Iterable, Iterator, Optional, TypeVar

T = TypeVar('T')

class ConcurrentQueue(Generic[T]):
    def __init__(self, iterable: Optional[Iterable[T]] = None) -> None:
        self._deque: deque[T] = deque(iterable) if iterable is not None else deque()
        self._lock: threading.RLock = threading.RLock()

    def append(self, item: T) -> None:
        with self._lock:
            self._deque.append(item)

    def appendleft(self, item: T) -> None:
        with self._lock:
            self._deque.appendleft(item)

    def pop(self) -> T:
        with self._lock:
            return self._deque.pop()

    def popleft(self) -> T:
        with self._lock:
            return self._deque.popleft()

    def __len__(self) -> int:
        with self._lock:
            return len(self._deque)

    def __iter__(self) -> Iterator[T]:
        # Make a snapshot copy for safe iteration
        with self._lock:
            return iter(list(self._deque))

    def clear(self) -> None:
        with self._lock:
            self._deque.clear()

    def extend(self, iterable: Iterable[T]) -> None:
        with self._lock:
            self._deque.extend(iterable)

    def extendleft(self, iterable: Iterable[T]) -> None:
        with self._lock:
            self._deque.extendleft(iterable)

    def __repr__(self) -> str:
        with self._lock:
            return f"ConcurrentQueue({list(self._deque)})"