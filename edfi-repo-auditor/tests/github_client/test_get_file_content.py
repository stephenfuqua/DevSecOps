# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from http import HTTPStatus
from typing import Optional
import pytest
import requests_mock

from edfi_repo_auditor.github_client import GitHubClient, API_URL

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"
FILES_URL = f"{API_URL}/repos/{OWNER}/{REPO}/contents"


def describe_when_getting_file() -> None:
    def describe_given_blank_owner() -> None:
        def it_raises_an_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_file_content("", "", "")

    def describe_given_blank_repository() -> None:
        def it_raises_an_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_file_content(OWNER, "", "")

    def describe_given_blank_path() -> None:
        def it_raises_an_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_file_content(OWNER, REPO, "")

    def describe_given_valid_information() -> None:
        def describe_getting_file() -> None:
            FILE_RESULT = """
{
    "name": "README.md",
    "size": 1533,
    "type": "file",
    "content": "VGVzdA==",
    "encoding": "base64"
}
""".strip()

            @pytest.fixture
            def results() -> Optional[str]:
                # Arrange
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{FILES_URL}/README.md",
                        status_code=HTTPStatus.OK,
                        text=FILE_RESULT,
                    )
                    return GitHubClient(ACCESS_TOKEN).get_file_content(
                        OWNER, REPO, "README.md"
                    )

            def it_returns_the_decoded_file_content(results: str) -> None:
                assert "Test" == results

        def describe_given_internal_server_error() -> None:
            FILE_RESULT = """
{
    "name": "README.md",
    "size": 1533,
    "type": "file",
    "content": "VGVzdA==",
    "encoding": "base64"
}
""".strip()

            @pytest.fixture
            def results() -> None:
                # Arrange
                with requests_mock.Mocker() as m:
                    m.get(
                        f"{FILES_URL}/README.md",
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        text=FILE_RESULT,
                    )
                    with pytest.raises(RuntimeError):
                        GitHubClient(ACCESS_TOKEN).get_file_content(
                            OWNER, REPO, "README.md"
                        )
