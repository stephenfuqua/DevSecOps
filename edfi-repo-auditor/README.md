# Ed-Fi Repo Auditor

Python script to get a report of the compliance of the repositories to the
checklist provided in [Repository
Scoring](https://techdocs.ed-fi.org/pages/viewpage.action?spaceKey=EDFIODS&title=Repository+Scoring).

The file [scoring.json](./scoring.json) provides the guidelines to be followed.
The property names are in the same format that the code will follow to assign a
value. This file provides a value for each property, this file can be modified
accordingly. Additionally, the `threshold` property specifies the limit that
will be tolerated to indicate if the repository needs to make adjustments
according to the scoring.

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
