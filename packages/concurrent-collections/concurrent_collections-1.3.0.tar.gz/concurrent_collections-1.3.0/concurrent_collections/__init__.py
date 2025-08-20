from .concurrent_bag import ConcurrentBag
from .concurrent_dict import ConcurrentDictionary
from .concurrent_deque import ConcurrentQueue

__all__ = ["ConcurrentBag", "ConcurrentDictionary", "ConcurrentQueue"]

# Type annotations for better IDE support
ConcurrentBag.__doc__ = "A thread-safe, list-like collection."
ConcurrentDictionary.__doc__ = "A thread-safe dictionary implementation using a re-entrant lock."
ConcurrentQueue.__doc__ = "A thread-safe queue implementation using a deque."