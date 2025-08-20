import threading
from typing import Any, Callable, Dict, Iterator, List, Optional, TypeVar, Generic, Tuple
import warnings
import sys

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class ConcurrentDictionary(Generic[K, V]):
    """
    A thread-safe dictionary implementation using a re-entrant lock.
    All operations that mutate or access the dictionary are protected.

    Example usage of update_atomic:

        d = ConcurrentDictionary({'x': 0})
        # Atomically increment the value for 'x'
        d.update_atomic('x', lambda v: v + 1)
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._lock = threading.RLock()
        self._dict: Dict[K, V] = dict(*args, **kwargs)  # type: ignore

    def __getitem__(self, key: K) -> V:
        with self._lock:
            return self._dict[key]

    def __setitem__(self, key: K, value: V) -> None:
        warnings.warn(
            f"Direct assignment (D[key] = value) is discouraged. "
            f"Use update_atomic for thread-safe compound updates.",
            stacklevel=2
        )
        self.update_atomic(key, lambda _: value)


    def __delitem__(self, key: K) -> None:
        with self._lock:
            del self._dict[key]


    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        with self._lock:
            return self._dict.get(key, default)


    def setdefault(self, key: K, default: V) -> V:
        with self._lock:
            return self._dict.setdefault(key, default)


    def update_atomic(self, key: K, func: Callable[[V], V]) -> None:
        """
        Atomically update the value for a key using func(old_value) -> new_value.

        This method ensures that the read-modify-write sequence is performed atomically,
        preventing race conditions in concurrent environments.

        Example:
            d = ConcurrentDictionary({'x': 0})
            # Atomically increment the value for 'x'
            d.update_atomic('x', lambda v: v + 1)
        """
        with self._lock:
            if key in self._dict:
                old_value = self._dict[key]
                new_value = func(old_value)
                self._dict[key] = new_value
            else:
                # If the key does not exist, we can set it directly
                self._dict[key] = func(None) # type: ignore


    def pop(self, key: K, default: Optional[V] = None) -> Optional[V]:
        with self._lock:
            return self._dict.pop(key, default)


    def popitem(self) -> tuple[K, V]:
        with self._lock:
            return self._dict.popitem()


    def clear(self) -> None:
        with self._lock:
            self._dict.clear()


    def keys(self) -> List[K]:
        with self._lock:
            return list(self._dict.keys())


    def values(self) -> List[V]:
        with self._lock:
            return list(self._dict.values())


    def items(self) -> List[Tuple[K, V]]:
        with self._lock:
            return list(self._dict.items())


    def __contains__(self, key: K) -> bool:
        with self._lock:
            return key in self._dict


    def __len__(self) -> int:
        with self._lock:
            return len(self._dict)


    def __iter__(self) -> Iterator[K]:
        with self._lock:
            return iter(list(self._dict))


    def __repr__(self) -> str:
        with self._lock:
            return f"ConcurrentDictionary({self._dict!r})"