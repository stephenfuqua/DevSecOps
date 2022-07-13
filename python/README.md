# Python Tools

These tools are appropriate in all Python repositories.

## Code Quality and Style Configuration

Install the following packages as dev dependencies:

* `flake8`
* `mypy`
* `black`

Use the following configuration files:

* [.flake8](.flake8)
* [.mypy.ini](.mypy.ini) - add other types as needed, for libraries that do not
  have type stubs available.

## GitHub Actions

* [Build and Test](test.yml)
* [CodeQL Scan](codeql.yml)
* [Dependency Review](../common/sample-dependencies-workflow.yml)
