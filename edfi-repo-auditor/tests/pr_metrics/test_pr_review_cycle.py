# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_repo_auditor.pr_metrics import audit_pr_review_cycle


def describe_audit_pr_review_cycle() -> None:
    def describe_given_metadata_with_reviews() -> None:
        def it_computes_expected_averages() -> None:
            pr_review_data = {
                1: [
                    {"state": "COMMENTED", "submitted_at": "2024-01-01T13:00:00Z", "created_at": "2024-01-01T12:00:00Z"},
                    {"state": "APPROVED", "submitted_at": "2024-01-01T14:00:00Z", "created_at": "2024-01-01T12:00:00Z"},
                ],
                2: [
                    {"state": "APPROVED", "submitted_at": "2024-01-02T12:00:00Z", "created_at": "2024-01-02T10:00:00Z"},
                    {"state": "APPROVED", "submitted_at": "2024-01-02T13:00:00Z", "created_at": "2024-01-02T10:00:00Z"},
                    {"state": "COMMENTED", "submitted_at": "2024-01-02T14:00:00Z", "created_at": "2024-01-02T10:00:00Z"},
                ],
            }

            result = audit_pr_review_cycle(pr_review_data)

            assert result["Avg Reviews per PR"] == 2.5
            assert result["Avg Approvals per PR"] == 1.5
            assert result["Avg Time to First Approval (hours)"] == 2.0

    def describe_given_missing_creation_timestamp() -> None:
        def it_skips_time_to_first_approval_when_unknown() -> None:
            pr_review_data = {
                1: [
                    {"state": "APPROVED", "submitted_at": "2024-01-01T14:00:00Z"},
                ],
                2: [],
            }

            result = audit_pr_review_cycle(pr_review_data)

            assert result["Avg Reviews per PR"] == 0.5
            assert result["Avg Approvals per PR"] == 0.5
            assert result["Avg Time to First Approval (hours)"] is None

    def describe_given_top_level_created_at_only() -> None:
        def it_uses_top_level_created_at_when_present() -> None:
            pr_review_data = {
                10: [
                        {"state": "APPROVED", "submitted_at": "2024-01-03T11:00:00Z", "created_at": "2024-01-03T09:00:00Z"},
                    ],
            }

            result = audit_pr_review_cycle(pr_review_data)

            assert result["Avg Time to First Approval (hours)"] == 2.0

    def describe_given_no_reviews() -> None:
        def it_returns_none_metrics() -> None:
            result = audit_pr_review_cycle({})

            assert result["Avg Reviews per PR"] is None
            assert result["Avg Approvals per PR"] is None
            assert result["Avg Time to First Approval (hours)"] is None
