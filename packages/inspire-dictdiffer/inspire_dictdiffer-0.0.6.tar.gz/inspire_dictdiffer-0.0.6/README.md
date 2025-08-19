
# Dictdiffer
Dictdiffer is a helper module that helps you to diff and patch dictionaries.

## Installation
 Install using pip
 ```bash
pip install git+https://github.com/inspirehep/dictdiffer.git
```

## Usage
Let's start with an example on how to find the diff between two dictionaries using :func:`.diff` method:

```python
from dictdiffer import diff, patch, swap, revert

first = {
	"title": "hello",
	"fork_count": 20,
	"stargazers": ["/users/20", "/users/30"],
	"settings": {
		"assignees": [100, 101, 201],
	}
}

second = {
	"title": "hellooo",
	"fork_count": 20,
	"stargazers": ["/users/20", "/users/30", "/users/40"],
	"settings": {
		"assignees": [100, 101, 202],
	}
}

result = diff(first, second)

assert list(result) == [
	('change', ['settings', 'assignees', 2], (201, 202)),
	('add', 'stargazers', [(2, '/users/40')]),
	('change', 'title', ('hello', 'hellooo'))]

```

Now we can apply the diff result with `.patch()` method:

```python
result = diff(first, second)
patched = patch(result, first)

assert patched == second
```

Also we can swap the diff result with `.swap()` method:

```python
result = diff(first, second)
swapped = swap(result)

assert list(swapped) == [
	('change', ['settings', 'assignees', 2], (202, 201)),
	('remove', 'stargazers', [(2, '/users/40')]),
	('change', 'title', ('hellooo', 'hello'))]
```
Let's revert the last changes:
```python
result = diff(first, second)
reverted = revert(result, patched)
assert reverted == first
```

A tolerance can be used to consider closed values as equal.
The tolerance parameter only applies for int and float.
Let's try with a tolerance of 10% with the values 10 and 10.5:
```python
first = {'a': 10.0}
second = {'a': 10.5}
result = diff(first, second, tolerance=0.1)

assert list(result) == []
```

Now with a tolerance of 1%:
```python
result = diff(first, second, tolerance=0.01)

assert list(result) == ('change', 'a', (10.0, 10.5))
```
## Testing
Running the test suite is as simple as:
```bash
./run-tests.sh
```
