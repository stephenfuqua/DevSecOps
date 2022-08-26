# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from http import HTTPStatus
import pytest
import requests_mock

from edfi_repo_auditor.github_client import GitHubClient, API_URL

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"
ACTIONS_URL = f"{API_URL}/repos/{OWNER}/{REPO}/actions/workflows"


def describe_when_getting_actions() -> None:
    def describe_given_blank_owner() -> None:
        def it_raises_an_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_actions("", "")

    def describe_given_blank_repository() -> None:
        def it_raises_an_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_actions(OWNER, "")

    def describe_given_valid_information() -> None:
        def describe_getting_actions() -> None:
            ACTIONS_RESULT = """
{
    "total_count": 1,
    "workflows": [
        {
            "id": 15,
            "node_id": "W_kwDOC9HpBs4A8xqR",
            "name": "A workflow file",
            "path": ".github/workflows/workflow.yml",
            "state": "active",
            "created_at": "2021-12-03T20:03:08.000Z",
            "updated_at": "2021-12-03T20:20:38.000Z"
        }
    ]
}
""".strip()

            @pytest.fixture
            def results() -> dict:
                # Arrange
                with requests_mock.Mocker() as m:
                    m.get(
                        ACTIONS_URL,
                        status_code=HTTPStatus.OK,
                        text=ACTIONS_RESULT,
                    )
                    return GitHubClient(ACCESS_TOKEN).get_actions(
                        OWNER,
                        REPO
                    )

            def it_returns_one_action(results: dict) -> None:
                assert results["total_count"] == 1

            def it_returns_the_path_for_the_workflow(results: dict) -> None:
                assert ".github/workflows/workflow.yml" == results["workflows"][0]["path"]

            def it_returns_the_name_of_the_workflow(results: dict) -> None:
                assert "A workflow file" == results["workflows"][0]["name"]

        def describe_given_internal_server_error() -> None:
            ACTIONS_RESULT = """
{
    "total_count": 1,
    "workflows": [
        {
            "id": 15,
            "node_id": "W_kwDOC9HpBs4A8xqR",
            "name": "A workflow file",
            "path": ".github/workflows/workflow.yml",
            "state": "active",
            "created_at": "2021-12-03T20:03:08.000Z",
            "updated_at": "2021-12-03T20:20:38.000Z"
        }
    ]
}
""".strip()

            def it_raises_a_RuntimeError() -> None:
                # Arrange
                with requests_mock.Mocker() as m:
                    m.get(
                        ACTIONS_URL,
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        text=ACTIONS_RESULT,
                    )

                    with pytest.raises(RuntimeError):
                        GitHubClient(ACCESS_TOKEN).get_actions(
                            OWNER,
                            REPO
                        )
