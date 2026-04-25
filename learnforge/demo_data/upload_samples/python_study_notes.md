# Python Programming Study Notes

## Variables and Data Types

Python is dynamically typed — you don't declare types explicitly.

### Basic Types
- **int**: Whole numbers like `42`, `-7`, `0`
- **float**: Decimal numbers like `3.14`, `-0.5`
- **str**: Text strings like `"hello"`, `'world'`
- **bool**: `True` or `False`
- **NoneType**: The `None` value (similar to null)

### Collections
- **list**: Ordered, mutable — `[1, 2, 3]`
- **tuple**: Ordered, immutable — `(1, 2, 3)`
- **dict**: Key-value pairs — `{"name": "Alice", "age": 30}`
- **set**: Unordered, unique values — `{1, 2, 3}`

## Control Flow

### If/Elif/Else
```python
x = 10
if x > 0:
    print("positive")
elif x == 0:
    print("zero")
else:
    print("negative")
```

### Loops
```python
# For loop
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# While loop
count = 0
while count < 3:
    print(count)
    count += 1

# List comprehension
squares = [x**2 for x in range(10)]
```

## Functions

```python
def greet(name, greeting="Hello"):
    """Greet someone by name."""
    return f"{greeting}, {name}!"

# *args and **kwargs
def flexible(*args, **kwargs):
    print(args)    # tuple of positional args
    print(kwargs)  # dict of keyword args
```

## Common Mistakes

1. **Mutable default arguments**: `def f(lst=[])` shares the same list across calls. Use `def f(lst=None)` instead.
2. **Modifying a list while iterating**: Create a copy or use list comprehension.
3. **Confusing `=` and `==`**: Assignment vs comparison.
4. **Forgetting `self` in methods**: First parameter of instance methods must be `self`.
5. **Integer division**: `7 / 2 = 3.5` (float division), `7 // 2 = 3` (integer division).
