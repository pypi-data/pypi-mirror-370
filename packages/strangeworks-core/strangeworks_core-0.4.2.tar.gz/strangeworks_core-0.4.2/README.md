# Strangeworks Python Core Library

The Strangeworks Python Core Library provides common code used across SDK's and applications.

## Installation

Install using `poetry`

```
pip install poetry
poetry install
```

## Tests

Test using pytest

```
poetry run pytest tests
```

## Set up dev pre-commit hooks:

the pre-commit hook registered takes care of linting, formatting, etc.

```
 poetry run pre-commit install
```

## Bump version

Bump version with [poetry](https://python-poetry.org/docs/cli/#version).

```
poetry version [patch, minor, major]
```

## Update packages

Update <package> version

```
poetry update <package>
```

Update all packages

```
poetry update
```
