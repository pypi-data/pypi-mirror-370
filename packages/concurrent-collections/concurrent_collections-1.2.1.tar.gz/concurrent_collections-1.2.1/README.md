# Python Concurrent (thread-safe) collections

![Run all tests](https://github.com/alelom/python-concurrentCollections/actions/workflows/run-all-tests.yml/badge.svg)

## tl;dr

Despite what many people think, Python's built-in `list`, `dict`, and `deque` are **NOT thread-safe**.  
They may be thread safe for [_some operations_, but not all](https://docs.python.org/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe).  
This created a lot of confusion in the Python community.  
[Google style-guide recommends to not rely on atomicity of built-in collections](https://github.com/google/styleguide/blob/91d6e367e384b0d8aaaf7ce95029514fcdf38651/pyguide.md#218-threading).

`concurrent_collections` provides thread-safe alternatives by using locks internally to ensure safe concurrent access and mutation from multiple threads.

Inspired from the amazing [C#'s concurrent collections](https://learn.microsoft.com/en-us/dotnet/api/system.collections.concurrent?view=net-9.0).

## Why use these collections?

**_There is a lot of confusion on whether Python collections are thread-safe or not_**<sup>1, 2, 3</sup>.

The bottom line is that Python's built-in collections are **not fully thread-safe** for all operations.  
While some simple operations (like `list.append()` or `dict[key] = value`) are thread-safe due to the Global Interpreter Lock (GIL), **compound operations and iteration with mutation are not**. This can lead to subtle bugs, race conditions, or even crashes in multi-threaded programs.

See the [Python FAQ: "What kinds of global value mutation are thread-safe?"](https://docs.python.org/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe) for details. The FAQ explains that only some (if common) operations are guaranteed to be atomic and thread-safe, but for anything more complex, you must use your own locking.  
The docs even go as far as to say:

> When in doubt, use a mutex!

Which is telling.

Even [Google recommends to not rely on atomicity of built-in collections](https://github.com/google/styleguide/blob/91d6e367e384b0d8aaaf7ce95029514fcdf38651/pyguide.md#218-threading).

This **`concurrent_collections`** library provides drop-in replacements that handle locking for you.  
Suggestions and feedbacks are welcome.

<sub>

1. [Are lists thread-safe?](https://stackoverflow.com/a/79645609/3873799)  

2. [Google style guide advises against relying on Python's assignment atomicity](https://stackoverflow.com/a/55279169/3873799)  

3. [What kind of "thread safe" are deque's actually?](https://groups.google.com/g/comp.lang.python/c/MAv5MVakB_4)  

</sub>

## Installation

Pip:

```bash
pip install concurrent_collections
```

My recommendation is to always use [`uv`](https://docs.astral.sh/uv/) instead of pip – I personally think it's the best package and environment manager for Python.

```bash
uv add concurrent_collections
```

## Collections

### ConcurrentBag

A thread-safe, list-like collection.

```python
from concurrent_collections import ConcurrentBag

bag = ConcurrentBag([1, 2, 3])
bag.append(4)
print(list(bag))  # [1, 2, 3, 4]
```

### ConcurrentDictionary

A thread-safe dictionary. For atomic compound updates, use `update_atomic`.

```python
from concurrent_collections import ConcurrentDictionary

d = ConcurrentDictionary({'x': 1})
d['y'] = 2  # Simple assignment is thread-safe
# For atomic updates:
d.update_atomic('x', lambda v: v + 1)
print(d['x'])  # 2
```

### ConcurrentQueue

A thread-safe double-ended queue.

```python
from concurrent_collections import ConcurrentQueue

q = ConcurrentQueue()
q.append(1)
q.appendleft(0)
print(q.pop())      # 1
print(q.popleft())  # 0
```

## License

MIT License
