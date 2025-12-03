# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest
from unittest.mock import MagicMock

from edfi_repo_auditor.pr_metrics import (
    audit_pr_duration,
    audit_lead_time_for_change,
)

OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"


def describe_audit_pr_duration() -> None:
    def describe_given_merged_prs() -> None:
        @pytest.fixture
        def mock_client() -> MagicMock:
            client = MagicMock()
            client.get_pull_requests.return_value = [
                {
                    "number": 1,
                    "created_at": "2024-01-01T10:00:00Z",
                    "closed_at": "2024-01-03T10:00:00Z",
                    "merged_at": "2024-01-03T10:00:00Z",
                    "user": "developer1",
                },
                {
                    "number": 2,
                    "created_at": "2024-01-05T10:00:00Z",
                    "closed_at": "2024-01-06T10:00:00Z",
                    "merged_at": "2024-01-06T10:00:00Z",
                    "user": "developer2",
                },
            ]
            return client

        def it_computes_correct_average_duration(mock_client: MagicMock) -> None:
            result = audit_pr_duration(mock_client, OWNER, REPO)
            # First PR: 2 days, Second PR: 1 day -> avg = 1.5 days
            assert result["avg_pr_duration_days"] == 1.5

        def it_counts_merged_prs(mock_client: MagicMock) -> None:
            result = audit_pr_duration(mock_client, OWNER, REPO)
            assert result["merged_pr_count"] == 2

    def describe_given_mixed_merged_and_closed_prs() -> None:
        @pytest.fixture
        def mock_client() -> MagicMock:
            client = MagicMock()
            client.get_pull_requests.return_value = [
                {
                    "number": 1,
                    "created_at": "2024-01-01T10:00:00Z",
                    "closed_at": "2024-01-03T10:00:00Z",
                    "merged_at": "2024-01-03T10:00:00Z",  # merged
                    "user": "developer1",
                },
                {
                    "number": 2,
                    "created_at": "2024-01-05T10:00:00Z",
                    "closed_at": "2024-01-06T10:00:00Z",
                    "merged_at": None,  # closed but not merged
                    "user": "developer2",
                },
            ]
            return client

        def it_only_includes_merged_prs(mock_client: MagicMock) -> None:
            result = audit_pr_duration(mock_client, OWNER, REPO)
            # Only first PR (2 days) should be counted
            assert result["avg_pr_duration_days"] == 2.0
            assert result["merged_pr_count"] == 1

    def describe_given_no_prs() -> None:
        @pytest.fixture
        def mock_client() -> MagicMock:
            client = MagicMock()
            client.get_pull_requests.return_value = []
            return client

        def it_returns_none_for_duration(mock_client: MagicMock) -> None:
            result = audit_pr_duration(mock_client, OWNER, REPO)
            assert result["avg_pr_duration_days"] is None

        def it_returns_zero_count(mock_client: MagicMock) -> None:
            result = audit_pr_duration(mock_client, OWNER, REPO)
            assert result["merged_pr_count"] == 0

    def describe_given_no_merged_prs() -> None:
        @pytest.fixture
        def mock_client() -> MagicMock:
            client = MagicMock()
            client.get_pull_requests.return_value = [
                {
                    "number": 1,
                    "created_at": "2024-01-01T10:00:00Z",
                    "closed_at": "2024-01-03T10:00:00Z",
                    "merged_at": None,  # closed but not merged
                    "user": "developer1",
                },
            ]
            return client

        def it_returns_none_for_duration(mock_client: MagicMock) -> None:
            result = audit_pr_duration(mock_client, OWNER, REPO)
            assert result["avg_pr_duration_days"] is None

        def it_returns_zero_count(mock_client: MagicMock) -> None:
            result = audit_pr_duration(mock_client, OWNER, REPO)
            assert result["merged_pr_count"] == 0

    def describe_given_prs_with_missing_timestamps() -> None:
        @pytest.fixture
        def mock_client() -> MagicMock:
            client = MagicMock()
            client.get_pull_requests.return_value = [
                {
                    "number": 1,
                    "created_at": None,  # missing created_at
                    "closed_at": "2024-01-03T10:00:00Z",
                    "merged_at": "2024-01-03T10:00:00Z",
                    "user": "developer1",
                },
                {
                    "number": 2,
                    "created_at": "2024-01-05T10:00:00Z",
                    "closed_at": "2024-01-06T10:00:00Z",
                    "merged_at": "2024-01-06T10:00:00Z",
                    "user": "developer2",
                },
            ]
            return client

        def it_skips_prs_with_missing_timestamps(mock_client: MagicMock) -> None:
            result = audit_pr_duration(mock_client, OWNER, REPO)
            # Only second PR (1 day) should have valid calculation
            assert result["avg_pr_duration_days"] == 1.0
            # But both are merged
            assert result["merged_pr_count"] == 2


def describe_audit_lead_time_for_change() -> None:
    def describe_given_merged_prs() -> None:
        @pytest.fixture
        def mock_client() -> MagicMock:
            client = MagicMock()
            client.get_pull_requests.return_value = [
                {
                    "number": 1,
                    "created_at": "2024-01-01T10:00:00Z",
                    "merged_at": "2024-01-03T10:00:00Z",
                    "user": "developer1",
                },
                {
                    "number": 2,
                    "created_at": "2024-01-05T10:00:00Z",
                    "merged_at": "2024-01-06T10:00:00Z",
                    "user": "developer2",
                },
            ]
            return client

        def it_computes_correct_average_lead_time(mock_client: MagicMock) -> None:
            result = audit_lead_time_for_change(mock_client, OWNER, REPO)
            # First PR: 2 days, Second PR: 1 day -> avg = 1.5 days
            assert result["avg_lead_time_days"] == 1.5

        def it_counts_merged_prs(mock_client: MagicMock) -> None:
            result = audit_lead_time_for_change(mock_client, OWNER, REPO)
            assert result["merged_pr_count"] == 2

    def describe_given_no_merged_prs() -> None:
        @pytest.fixture
        def mock_client() -> MagicMock:
            client = MagicMock()
            client.get_pull_requests.return_value = [
                {
                    "number": 1,
                    "created_at": "2024-01-01T10:00:00Z",
                    "closed_at": "2024-01-03T10:00:00Z",
                    "merged_at": None,
                    "user": "developer1",
                },
            ]
            return client

        def it_returns_none_for_lead_time(mock_client: MagicMock) -> None:
            result = audit_lead_time_for_change(mock_client, OWNER, REPO)
            assert result["avg_lead_time_days"] is None

        def it_returns_zero_count(mock_client: MagicMock) -> None:
            result = audit_lead_time_for_change(mock_client, OWNER, REPO)
            assert result["merged_pr_count"] == 0
