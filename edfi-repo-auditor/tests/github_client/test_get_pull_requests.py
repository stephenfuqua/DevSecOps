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
PRS_URL = f"{API_URL}/repos/{OWNER}/{REPO}/pulls"


def describe_when_getting_pull_requests() -> None:
    def describe_given_blank_owner() -> None:
        def it_raises_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_pull_requests("", REPO)

    def describe_given_blank_repository() -> None:
        def it_raises_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_pull_requests(OWNER, "")

    def describe_given_valid_information() -> None:
        def describe_given_single_page_of_prs() -> None:
            PRS_RESULT = """
[
    {
        "number": 123,
        "created_at": "2024-01-01T10:00:00Z",
        "closed_at": "2024-01-02T12:00:00Z",
        "merged_at": "2024-01-02T12:00:00Z",
        "user": {"login": "developer1"},
        "additions": 50,
        "deletions": 10,
        "changed_files": 3
    },
    {
        "number": 124,
        "created_at": "2024-01-03T10:00:00Z",
        "closed_at": "2024-01-04T14:00:00Z",
        "merged_at": null,
        "user": {"login": "developer2"},
        "additions": 100,
        "deletions": 20,
        "changed_files": 5
    }
]
""".strip()

            @pytest.fixture
            def results() -> list:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{PRS_URL}?state=closed&per_page=100&page=1",
                        status_code=HTTPStatus.OK,
                        text=PRS_RESULT,
                    )
                    return GitHubClient(ACCESS_TOKEN).get_pull_requests(OWNER, REPO)

            def it_returns_two_prs(results: list) -> None:
                assert len(results) == 2

            def it_returns_correct_first_pr_number(results: list) -> None:
                assert results[0]["number"] == 123

            def it_returns_merged_at_for_merged_pr(results: list) -> None:
                assert results[0]["merged_at"] == "2024-01-02T12:00:00Z"

            def it_returns_none_merged_at_for_non_merged_pr(results: list) -> None:
                assert results[1]["merged_at"] is None

            def it_returns_user_login(results: list) -> None:
                assert results[0]["user"] == "developer1"

        def describe_given_multiple_pages_of_prs() -> None:
            PAGE1_RESULT = """
[
    {
        "number": 1,
        "created_at": "2024-01-01T10:00:00Z",
        "closed_at": "2024-01-02T12:00:00Z",
        "merged_at": "2024-01-02T12:00:00Z",
        "user": {"login": "dev1"},
        "additions": 10,
        "deletions": 5,
        "changed_files": 1
    },
    {
        "number": 2,
        "created_at": "2024-01-03T10:00:00Z",
        "closed_at": "2024-01-04T12:00:00Z",
        "merged_at": "2024-01-04T12:00:00Z",
        "user": {"login": "dev2"},
        "additions": 20,
        "deletions": 10,
        "changed_files": 2
    }
]
""".strip()

            PAGE2_RESULT = """
[
    {
        "number": 3,
        "created_at": "2024-01-05T10:00:00Z",
        "closed_at": "2024-01-06T12:00:00Z",
        "merged_at": "2024-01-06T12:00:00Z",
        "user": {"login": "dev3"},
        "additions": 30,
        "deletions": 15,
        "changed_files": 3
    }
]
""".strip()

            @pytest.fixture
            def results() -> list:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{PRS_URL}?state=closed&per_page=2&page=1",
                        status_code=HTTPStatus.OK,
                        text=PAGE1_RESULT,
                    )
                    m.get(
                        f"{PRS_URL}?state=closed&per_page=2&page=2",
                        status_code=HTTPStatus.OK,
                        text=PAGE2_RESULT,
                    )
                    return GitHubClient(ACCESS_TOKEN).get_pull_requests(
                        OWNER, REPO, per_page=2
                    )

            def it_returns_all_three_prs(results: list) -> None:
                assert len(results) == 3

            def it_returns_pr_from_first_page(results: list) -> None:
                assert results[0]["number"] == 1
                assert results[1]["number"] == 2

            def it_returns_pr_from_second_page(results: list) -> None:
                assert results[2]["number"] == 3

        def describe_given_empty_result() -> None:
            @pytest.fixture
            def results() -> list:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{PRS_URL}?state=closed&per_page=100&page=1",
                        status_code=HTTPStatus.OK,
                        text="[]",
                    )
                    return GitHubClient(ACCESS_TOKEN).get_pull_requests(OWNER, REPO)

            def it_returns_empty_list(results: list) -> None:
                assert results == []

        def describe_given_internal_server_error() -> None:
            def it_raises_a_RuntimeError() -> None:
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{PRS_URL}?state=closed&per_page=100&page=1",
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        text="{}",
                    )
                    with pytest.raises(RuntimeError):
                        GitHubClient(ACCESS_TOKEN).get_pull_requests(OWNER, REPO)
