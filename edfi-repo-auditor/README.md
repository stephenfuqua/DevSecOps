# Ed-Fi Repo Auditor

Python script to report on compliance with Ed-Fi repository guidance. The file
[scoring.json](./scoring.json) provides the guidelines to be followed; see below
for a detailed description in plain text. The property names are in the same
format that the code will follow to assign a value. This file provides a value
for each property, this file can be modified accordingly. Additionally, the
`threshold` property specifies the limit that will be tolerated to indicate if
the repository needs to make adjustments according to the scoring.

## Run

To run, install [poetry](https://python-poetry.org/) and run:

```bash
poetry run python edfi_repo_auditor -p {TOKEN} -s True -o {ORGANIZATION} -r {REPOSITORY}
```

Parameters:
| Parameter          | Description          | Required?                                                                                                                   |
| ------------------ | -------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| --access_token  -p | GitHub Access Token  | To call private repos and get branch protection info                                                                        |
| --organization -o  | Organization Name    | Yes                                                                                                                         |
| --repositories -r  | Repositories         | No. If not specified, will get all repos for the organization. Can specify multiple repositories separated by a blank space |
| --log_level -r     | Log level            | No. Default: INFO. Can be: ERROR, WARNING, INFO, DEBUG                                                                      |
| --save_results -s  | Save results to file | No. Default: console. If specified, will save the
results to a file |
| --file_name -f  | Filename | No. Default: `audit-results`. If specified,
will save the results with given name. |

## Test

Run `poetry run pytest` to execute unit tests

## Detailed Guidance

* **Has Actions**: There is at least one Action in the repository.
* **Uses CodeQL**: The repository runs CodeQL; detected by looking for "uses: github/codeql-action/analyze" in an Actions yml file.
* **Uses only approved GitHub Actions**: The repository only uses approved GitHub Actions; detected by looking for "repository-scanner.yml" in an Actions yml file.
* **Uses Test Reporter**: Unit tests results are uploaded directly into GitHub Actions; detected by looking for "uses: dorny/test-reporter" in an Actions yml file.
* **Has README**: There is a README.md file.
* **Has CONTRIBUTORS**: There is a CONTRIBUTORS.md file.
* **Has NOTICES**: There is a NOTICES.md file.
* **Has LICENSE**: There is either a LICENSE or LICENSE.md file.
* **Requires Signed commits**: Branch protection for `main` requires signed commits.
* **Requires Code review**: Branch protection for `main` requires code reviews.
* **Requires PR**: Branch protection for `main` requires a pull request.
* **Admin cannot bypass PR**: Branch protection for `main` cannot be bypassed by an admin.
* **Wiki Disabled**: Wikis are disabled.
* **Issues Disabled**: Issues are disabled.
* **Projects Disabled**: Projects are disabled.
* **Discussions Disabled**: Discussions are disabled.
* **Has Unit Tests**: There is an action step with "unit test" in the name.
* **Has Linter**: There is an action step with "lint" / "linter" / "linting" in the name.
* **Deletes head branch**: Automatically deletes head branches on merge.
* **Uses Squash Merge**: Squash merge is the default.
* **License Information**: The repo settings specify a license (this is different than the license file).
* **Dependabot Enabled**: DependaBot is enabled.
* **Dependabot Alerts**: There are no _critical_ or _high_ severity DependaBot alerts that have remained open for greater than three weeks.
