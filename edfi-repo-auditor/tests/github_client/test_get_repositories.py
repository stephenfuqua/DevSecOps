# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from http import HTTPStatus
from typing import List
import pytest
import requests_mock

from edfi_repo_auditor.github_client import GitHubClient, GRAPHQL_ENDPOINT

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"


def describe_when_getting_repositories() -> None:
    def describe_given_blank_owner() -> None:
        def it_raises_an_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_repositories("")

    def describe_given_valid_owner() -> None:
        def describe_given_valid_query() -> None:
            REPOSITORIES_RESULT = """
{
  "data": {
    "organization": {
      "id": "MDEyOk9yZ2FuaXphdGlvbjYyNzIyMzIw",
      "repositories": {
        "totalCount": 2,
        "nodes": [
          {
            "name": "Ed-Fi-Standard"
          },
          {
            "name": "Ed-Fi-ODS"
          }
        ]
      }
    }
  }
}
""".strip()

            @pytest.fixture
            def results() -> List[str]:
                # Arrange
                with requests_mock.Mocker() as m:
                    m.post(
                        GRAPHQL_ENDPOINT,
                        status_code=HTTPStatus.OK,
                        text=REPOSITORIES_RESULT,
                    )
                    return GitHubClient(ACCESS_TOKEN).get_repositories(OWNER)

            def it_returns_two_repositories(results: List[str]) -> None:
                assert len(results) == 2

            def it_returns_Ed_Fi_Standard(results: List[str]) -> None:
                assert "Ed-Fi-Standard" in results

            def it_returns_Ed_Fi_ODS(results: List[str]) -> None:
                assert "Ed-Fi-ODS" in results

        def describe_given_bad_query() -> None:
            REPOSITORIES_RESULT = """
{
  "data": {
    "organization": null
  },
  "errors": [
    {
      "type": "NOT_FOUND",
      "path": [
        "organization"
      ],
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "message": "Could not resolve to an Organization with the login of 'Ed-Fi-Alliance-OSSe'."
    }
  ]
}
""".strip()

            def it_raises_a_RuntimeError() -> None:
                # Arrange
                with requests_mock.Mocker() as m:
                    m.post(
                        GRAPHQL_ENDPOINT,
                        status_code=HTTPStatus.OK,
                        text=REPOSITORIES_RESULT,
                    )

                    with pytest.raises(RuntimeError):
                        GitHubClient(ACCESS_TOKEN).get_repositories(OWNER)
