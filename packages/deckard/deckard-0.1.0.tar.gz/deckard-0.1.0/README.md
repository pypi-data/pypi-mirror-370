<h1 align="center">Deckard 🕵️‍♂️</h1>

<p align="center">Extract structured data from unstructured text — no AI, just regular expressions. 🔍</p>

[![GitHub License](https://img.shields.io/github/license/SpaceShaman/deckard)](https://github.com/SpaceShaman/deckard?tab=MIT-1-ov-file)
[![Tests](https://img.shields.io/github/actions/workflow/status/SpaceShaman/deckard/release.yml?label=tests)](https://app.codecov.io/github/SpaceShaman/deckard)
[![Codecov](https://img.shields.io/codecov/c/github/SpaceShaman/deckard)](https://app.codecov.io/github/SpaceShaman/deckard)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/deckard)](https://pypi.org/project/deckard)
[![PyPI - Version](https://img.shields.io/pypi/v/deckard)](https://pypi.org/project/deckard)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/badge/linting-Ruff-black?logo=ruff&logoColor=black)](https://github.com/astral-sh/ruff)
[![Pytest](https://img.shields.io/badge/testing-Pytest-red?logo=pytest&logoColor=red)](https://docs.pytest.org/)

> Deckard is a library of regular-expression patterns for extracting structured data (addresses, phone numbers, email addresses, etc.) and a small set of helper utilities that make using those patterns easier.

> Status: very early-stage project. Right now the repository contains mostly patterns for Poland. I am looking for contributors from around the world 🌍 — address formats, phone-number formats and other data representations differ by country, so the goal is to gather country-specific patterns for many regions.

## Key features ✨

- 🗂️ A collection of ready-to-use regex patterns organized by country (for example [`deckard/patterns/pl.py`](./deckard/patterns/pl.py)).
- 📦 Universal patterns (e.g. email) live in [`deckard/patterns/standard.py`](./deckard/patterns/standard.py).
- 🛠️ A small helper function `deckard.search` that combines multiple patterns and returns named-group matches ([deckard/main.py](./deckard/main.py)).

## Installation ⚙️

From PyPI:

```bash
pip install deckard
```

Editable / local development install:

```bash
pip install -e .
```

### For contributors — install dependencies with Poetry 🧑‍💻

This project uses Poetry to manage dependencies and development dependencies.

1. Install Poetry (see https://python-poetry.org for instructions).
2. From the project root run:

```bash
poetry install
```

This will create a virtual environment and install runtime and development dependencies (including `pytest`).

To run tests using Poetry:

```bash
poetry run pytest
```

Or start a shell in the created virtualenv and run tests directly:

```bash
poetry shell
pytest
```

## Quick usage 🧭

Example using the current public API:

```python
from deckard import search
from deckard.patterns import standard, pl

text = (
    "Hello, my email is spaceshaman@tuta.io and my phone number is "
    "+48 792 321 321 and my address is ul. Tesotowa 12/6A, 66-700 Bielsko-Biała."
)

result = search([standard.EMAIL, pl.MOBILE_PHONE, pl.ADDRESS], text)

# result.groupdict() will return a dict of named groups, for example:
# {
#   'email': 'spaceshaman@tuta.io',
#   'mobile_phone': '792 321 321',
#   'street': 'ul. Tesotowa',
#   'building': '12',
#   'apartment': '6A',
#   'zip_code': '66-700',
#   'city': 'Bielsko-Biała'
# }
```

The `search` helper composes the provided patterns into a single regex (using lookaheads) and returns the first match as a `regex.Match` object (or `None` if nothing matched).

## Repository layout

- [`deckard/`](./deckard/) — library code
  - [`deckard/main.py`](./deckard/main.py) — helper `search` function
  - [`deckard/patterns/standard.py`](./deckard/patterns/standard.py) — universal patterns (e.g. `EMAIL`)
  - [`deckard/patterns/pl.py`](./deckard/patterns/pl.py) — Poland-specific patterns (address, postal code, phone, etc.)
- [`tests/`](./tests/) — unit tests

Examples of existing tests:
- [`tests/test_standard_patterns.py`](./tests/test_standard_patterns.py) — test for `standard.EMAIL`
- [`tests/test_search_with_multiple_patterns.py`](./tests/test_search_with_multiple_patterns.py) — integration tests combining `standard.EMAIL` with patterns from `pl.py`
- [`tests/pl/test_search_address_pl.py`](./tests/pl/test_search_address_pl.py) — tests for Polish address patterns

Every new pattern must come with tests. Pull requests without tests will not be accepted.

## Contributing — how to add new patterns

1. Create a new file under [`deckard/patterns/`](./deckard/patterns/) named by the country code, e.g. `us.py`, `de.py`, `fr.py`.
2. Define constants (UPPERCASE) for each pattern, for example `MOBILE_PHONE`, `ADDRESS`, `ZIP_CODE`.
3. Add tests under `tests/`. Use the existing Polish tests (e.g. `tests/test_search_with_multiple_patterns.py`) as a template. Provide normal and edge-case examples.
4. In the PR description explain local rules (phone number format, postal code format, common street abbreviations, etc.).
5. PRs without tests will not be accepted.

Tips 💡:
- 🧾 Use clear, consistent named groups in regexes (`?P<name>`) so `groupdict()` returns a predictable structure.
- 📝 Document complex patterns with comments and example inputs if necessary.

## Discussion and roadmap 🚧

The project is not yet final — everything is open for discussion. Areas for contributors and discussion include:

- 📋 Defining a minimal set of patterns every country should provide (email, phone, address, postal code, national ID where applicable).
- 🔠 Standardizing group names (`street`, `building`, `apartment`, `zip_code`, `city`, `country`, `mobile_phone`, etc.).
- ⚖️ Tools for validation and normalization of extracted values.
- 🤖 Automating tests with sample documents in various languages.

If you want to help, open an issue or a PR — a short description of the local data format and one or two patterns with tests is a great place to start.

## License 📄

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for the full text.

---

Thanks for your interest — please join the effort. Together we can build an international library of patterns to extract structured data from arbitrary text using robust regular expressions. 🚀
