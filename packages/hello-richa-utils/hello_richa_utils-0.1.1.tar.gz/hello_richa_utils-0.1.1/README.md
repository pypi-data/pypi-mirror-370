# helloutils

A simple utility package with a `say_hello()` function.

Create `tests/test_hello.py`:

```python
from helloutils import say_hello

def test_say_hello():
   assert say_hello("World") == "Hello, World!"
```

