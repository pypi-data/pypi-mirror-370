# transliteration-ua

[![Build Status](https://github.com/yakimka/transliteration-ua/actions/workflows/workflow-ci.yml/badge.svg?branch=main&event=push)](https://github.com/yakimka/transliteration-ua/actions/workflows/workflow-ci.yml)
[![Codecov](https://codecov.io/gh/yakimka/transliteration-ua/branch/main/graph/badge.svg)](https://codecov.io/gh/yakimka/transliteration-ua)
[![PyPI - Version](https://img.shields.io/pypi/v/transliteration-ua.svg)](https://pypi.org/project/transliteration-ua/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/transliteration-ua)](https://pypi.org/project/picodi/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/transliteration-ua)](https://pypi.org/project/picodi/)

Ukrainian transliteration by official rules

https://zakon.rada.gov.ua/laws/show/55-2010-п

## Installation

```bash
pip install transliteration-ua
```

## Example

To use `transliteration-ua`, import the `transliterate_ua` function and pass a Ukrainian string to
it:

```python
from transliteration_ua import transliterate_ua

# Basic usage
print(transliterate_ua("Привіт, Світ!"))
# Pryvit, Svit!

# Names are transliterated correctly
print(transliterate_ua("Андрій"))
# Andrii

# Words with an apostrophe are also handled
print(transliterate_ua("Короп'є"))
# Koropie
```

### Custom transliteration function

If you need to create your own transliteration function with custom rules, you can use
the `make_transliterate_func` factory. It accepts two mapping arguments: `replacements` for
general character mappings and `first_char_replacements` for special mappings that apply only
to the first letter of a word.

Here's how you can create a simplified transliterator:

```python
from transliteration_ua import make_transliterate_func

# Define custom replacement rules
simple_replacements = {
    "а": "a",
    "б": "b",
    "в": "v",
    # ...
    # all the Ukrainian alphabet need to be defined here
}
# No special first character rules for this example
first_char_replacements = {}

# Create the custom function
simple_transliterate = make_transliterate_func(
    simple_replacements,
    first_char_replacements,
)

# Use it
print(simple_transliterate("баба"))
# baba
```

## Development

### Making Changes

1. List available `make` commands:
   ```bash
   make help
   ```
2. Check code style with:
   ```bash
   make lint
   ```
3. Run tests using:
   ```bash
   make test
   ```
4. Manage dependencies via Poetry:
   ```bash
   make poetry args="<poetry-args>"
   ```
    - For example: `make poetry args="add picodi"`

5. For local CI debugging:
   ```bash
   make run-ci
   ```

#### Pre-commit Hooks

We use [pre-commit](https://pre-commit.com/) for linting and formatting:

- It runs inside a Docker container by default.
- Optionally, set up hooks locally:
  ```bash
  pre-commit install
  ```

#### Mypy

We use [mypy](https://mypy.readthedocs.io/en/stable/) for static type checking.

It is configured for strictly typed code, so you may need to add type hints to your code.
But don't be very strict, sometimes it's better to use `Any` type.

## License

[MIT](https://github.com/yakimka/transliteration-ua/blob/main/LICENSE)

## Credits

This project was generated with [
`yakimka/cookiecutter-pyproject`](https://github.com/yakimka/cookiecutter-pyproject).
