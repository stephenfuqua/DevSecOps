# JavaScript and TypeScript DevSecOps tools

These tools are appropriate in all JavaScript or TypeScript repositories.

## Code Quality and Style Configuration

Install the following packages as dev dependencies:

* `@types/eslint`
* `@typescript-eslint/eslint-plugin`
* `@typescript-eslint/parser`
* `eslint`
* `eslint-config-airbnb-base`
* `eslint-config-prettier`
* `eslint-config-typescript`
* `eslint-plugin-import`
* `eslint-plugin-jasmine`
* `eslint-plugin-json`
* `eslint-plugin-prettier`
* `prettier`

Use the following configuration files:

* [.editorconfig](.editorconfig)
* [.eslintigore](.eslintigore)
* [.eslintrc.js](.eslintrc.js)
* [.prettierrc](.prettierrc)

## GitHub Actions

* [Build and Test](test.yml)
* [CodeQL Scan](codeql.yml)
* [Dependency Review](../common/sample-dependencies-workflow.yml)
