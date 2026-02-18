# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import requests_mock

from edfi_repo_auditor.ossf_score import get_ossf_score


def _build_url(org: str, repo: str) -> str:
    return (
        f"https://img.shields.io/ossf-scorecard/github.com/{org}/{repo}?"
        "label=openssf+scorecard&style=flat"
    )


def describe_get_ossf_score() -> None:
    def describe_given_valid_response() -> None:
        def it_returns_float_value() -> None:
            with requests_mock.Mocker() as mock:
                org = "Ed-Fi"
                repo = "Repo"
                mock.get(
                    _build_url(org, repo),
                    status_code=200,
                    text="""
                    <svg><title>openssf scorecard: 8.2</title></svg>
                    """,
                )

                result = get_ossf_score(org, repo)

            assert result == {"OSSF Score": 8.2}

    def describe_given_missing_title() -> None:
        def it_returns_none() -> None:
            with requests_mock.Mocker() as mock:
                org = "Ed-Fi"
                repo = "Repo"
                mock.get(
                    _build_url(org, repo),
                    status_code=200,
                    text="<svg></svg>",
                )

                result = get_ossf_score(org, repo)

            assert result == {"OSSF Score": None}

    def describe_given_http_error_500() -> None:
        def it_gracefully_handles_failure() -> None:
            with requests_mock.Mocker() as mock:
                org = "Ed-Fi"
                repo = "Repo"
                mock.get(_build_url(org, repo), status_code=500)

                result = get_ossf_score(org, repo)

            assert result == {"OSSF Score": None}

    def describe_given_http_error_404() -> None:
        def it_gracefully_handles_failure() -> None:
            with requests_mock.Mocker() as mock:
                org = "Ed-Fi"
                repo = "Repo"
                mock.get(_build_url(org, repo), status_code=404)

                result = get_ossf_score(org, repo)

            assert result == {"OSSF Score": None}
