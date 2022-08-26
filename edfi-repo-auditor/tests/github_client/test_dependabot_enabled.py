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
DEPENDABOT_URL = f"{API_URL}/repos/{OWNER}/{REPO}/vulnerability-alerts"


def describe_when_checking_for_dependabot() -> None:
    def describe_given_blank_owner() -> None:
        def it_raises_an_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).has_dependabot_enabled("", "")

    def describe_given_blank_repository() -> None:
        def it_raises_an_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).has_dependabot_enabled(OWNER, "")

    def describe_given_valid_information() -> None:
        def describe_given_has_dependabot() -> None:

            @pytest.fixture
            def result() -> bool:
                with requests_mock.Mocker() as m:
                    m.get(
                        DEPENDABOT_URL,
                        status_code=HTTPStatus.NO_CONTENT
                    )
                    return GitHubClient(ACCESS_TOKEN).has_dependabot_enabled(
                        OWNER,
                        REPO
                    )

            def it_returns_true(result: bool) -> None:
                assert result is True

        def describe_given_no_dependabot() -> None:

            @pytest.fixture
            def result() -> bool:
                with requests_mock.Mocker() as m:
                    m.get(
                        DEPENDABOT_URL,
                        status_code=HTTPStatus.NOT_FOUND
                    )

                    return GitHubClient(ACCESS_TOKEN).has_dependabot_enabled(
                            OWNER,
                            REPO
                        )

            def it_returns_false(result: bool) -> None:
                assert result is False

        def describe_given_no_admin_permission() -> None:

            @pytest.fixture
            def result() -> bool:
                with requests_mock.Mocker() as m:
                    m.get(
                        DEPENDABOT_URL,
                        status_code=HTTPStatus.NOT_FOUND
                    )

                    return GitHubClient("non-@dm!nT0Ken").has_dependabot_enabled(
                            OWNER,
                            REPO
                        )

            def it_returns_false(result: bool) -> None:
                assert result is False
