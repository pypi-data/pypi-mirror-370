import threading
from typing import Generic, Iterable, Iterator, List, Optional, TypeVar

T = TypeVar('T')

class ConcurrentBag(Generic[T]):
    """
    A thread-safe, list-like collection.
    All mutating and reading operations are protected by a lock.
    """
    def __init__(self, iterable: Optional[Iterable[T]] = None) -> None:
        self._lock: threading.RLock = threading.RLock()
        self._items: List[T] = list(iterable) if iterable is not None else []

    def append(self, item: T) -> None:
        with self._lock:
            self._items.append(item)

    def extend(self, iterable: Iterable[T]) -> None:
        with self._lock:
            self._items.extend(iterable)

    def pop(self, index: int = -1) -> T:
        with self._lock:
            return self._items.pop(index)

    def remove(self, value: T) -> None:
        with self._lock:
            self._items.remove(value)

    def __getitem__(self, index: int) -> T:
        with self._lock:
            return self._items[index]

    def __setitem__(self, index: int, value: T) -> None:
        with self._lock:
            self._items[index] = value

    def __delitem__(self, index: int) -> None:
        with self._lock:
            del self._items[index]

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)

    def __iter__(self) -> Iterator[T]:
        with self._lock:
            return iter(self._items.copy())

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def __repr__(self) -> str:
        with self._lock:
            return f"ConcurrentBag({self._items!r})"