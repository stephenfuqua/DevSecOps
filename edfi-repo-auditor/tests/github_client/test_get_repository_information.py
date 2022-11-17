# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from http import HTTPStatus
import pytest
import requests_mock

from edfi_repo_auditor.github_client import GitHubClient, GRAPHQL_ENDPOINT

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"


def describe_when_getting_repository_information() -> None:
    def describe_given_blank_owner() -> None:
        def it_raises_an_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_repository_information("", "")

    def describe_given_blank_repository() -> None:
        def it_raises_an_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_repository_information(OWNER, "")

    def describe_given_valid_information() -> None:
        def describe_given_valid_query() -> None:
            REPOSITORY_INFORMATION_RESULT = """
{
  "data": {
    "repository": {
      "vulnerabilityAlerts": {
        "nodes": [
          {
            "createdAt": "2022-04-18T23:42:19Z",
            "securityVulnerability": {
              "package": {
                "name": "minimist"
              },
              "advisory": {
                "severity": "CRITICAL"
              }
            }
          }
        ]
      },
      "branchProtectionRules": {
        "nodes": [
            {
                "pattern": "main",
                "requiresCommitSignatures": true,
                "isAdminEnforced": true,
                "requiresApprovingReviews": true
            }
        ]
      },
      "hasWikiEnabled": false,
      "hasIssuesEnabled": false,
      "hasProjectsEnabled": false,
      "discussions": {
        "totalCount": 0
      },
      "deleteBranchOnMerge": false,
      "squashMergeAllowed": true,
      "licenseInfo": {
        "key": "apache-2.0"
      }
    }
  }
}
""".strip()

            @pytest.fixture
            def results() -> dict:
                # Arrange
                with requests_mock.Mocker() as m:
                    m.post(
                        GRAPHQL_ENDPOINT,
                        status_code=HTTPStatus.OK,
                        text=REPOSITORY_INFORMATION_RESULT,
                    )
                    return GitHubClient(ACCESS_TOKEN).get_repository_information(
                        OWNER, REPO
                    )

            def it_returns_the_branch_protection_rules(results: dict) -> None:
                assert len(results["branchProtectionRules"]["nodes"]) == 1

            def it_returns_if_requires_signatures(results: dict) -> None:
                assert (
                    results["branchProtectionRules"]["nodes"][0][
                        "requiresCommitSignatures"
                    ]
                    is True
                )

            def it_returns_if_requires_approving_reviews(results: dict) -> None:
                assert (
                    results["branchProtectionRules"]["nodes"][0][
                        "requiresApprovingReviews"
                    ]
                    is True
                )

            def it_returns_license_info(results: dict) -> None:
                assert results["licenseInfo"]["key"] == "apache-2.0"

        def describe_given_bad_query() -> None:
            REPOSITORY_INFORMATION_RESULT = """
{
  "data": {
    "repository": null
  },
  "errors": [
    {
      "type": "NOT_FOUND",
      "path": [
        "repository"
      ],
      "locations": [
        {
          "line": 3,
          "column": 3
        }
      ],
      "message": "Could not resolve to a Repository with the name 'Ed-Fi-Alliance-OSS/Ed-Fi-ODS'."
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
                        text=REPOSITORY_INFORMATION_RESULT,
                    )

                    with pytest.raises(RuntimeError):
                        GitHubClient(ACCESS_TOKEN).get_repository_information(
                            OWNER, REPO
                        )
