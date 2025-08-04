## General

* Make only high confidence suggestions when reviewing code changes.
* Never change pyproject.toml or poetry.lock files unless explicitly asked to.

## Formatting

* Apply code-formatting style defined in `.editorconfig`.
* Do not change the formatting of code unless explicitly asked to.

## Python

* Use Poetry for dependency management.
* Use `poetry.lock` for locking dependencies.
* Follow PEP 8 style guide for Python code.
* Use `black` for code formatting.
* Use `pytest` for testing.
* Include type hints for all function signatures.
* Use `mypy` for type checking.
* Use `flake8` for linting.
