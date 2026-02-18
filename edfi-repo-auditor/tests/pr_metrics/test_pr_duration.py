# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.


from typing import Dict, List

from edfi_repo_auditor.pr_metrics import (
    audit_pr_duration,
    audit_lead_time_for_change,
)


def describe_audit_pr_duration() -> None:
    def describe_given_merged_prs() -> None:
        def it_computes_correct_average_duration() -> None:
            merged_prs: List[Dict] = [
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

            result = audit_pr_duration(merged_prs)

            assert result["avg_pr_duration_days"] == 1.5

    def describe_given_no_prs() -> None:
        def it_returns_none_for_duration() -> None:
            result = audit_pr_duration([])

            assert result["avg_pr_duration_days"] is None

    def describe_given_prs_with_missing_timestamps() -> None:
        def it_skips_invalid_entries() -> None:
            merged_prs: List[Dict] = [
                {
                    "number": 1,
                    "created_at": None,
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

            result = audit_pr_duration(merged_prs)

            assert result["avg_pr_duration_days"] == 1.0


def describe_audit_lead_time_for_change() -> None:
    def describe_given_merged_prs() -> None:
        def it_computes_correct_average_lead_time() -> None:
            merged_prs = [
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

            result = audit_lead_time_for_change(merged_prs)

            assert result["avg_lead_time_days"] == 1.5

    def describe_given_no_merged_prs() -> None:
        def it_returns_none_for_lead_time() -> None:
            merged_prs: List[Dict] = [
                {
                    "number": 1,
                    "created_at": "2024-01-01T10:00:00Z",
                    "merged_at": None,
                    "user": "developer1",
                },
            ]

            result = audit_lead_time_for_change(merged_prs)

            assert result["avg_lead_time_days"] is None

    def describe_given_prs_with_missing_timestamps() -> None:
        def it_skips_entries_without_created_or_merged_at() -> None:
            merged_prs: List[Dict] = [
                {
                    "number": 1,
                    "created_at": None,
                    "merged_at": "2024-01-03T10:00:00Z",
                    "user": "developer1",
                },
                {
                    "number": 2,
                    "created_at": "2024-01-05T10:00:00Z",
                    "merged_at": None,
                    "user": "developer2",
                },
                {
                    "number": 3,
                    "created_at": "2024-01-05T10:00:00Z",
                    "merged_at": "2024-01-07T10:00:00Z",
                    "user": "developer3",
                },
            ]

            result = audit_lead_time_for_change(merged_prs)

            assert result["avg_lead_time_days"] == 2.0
