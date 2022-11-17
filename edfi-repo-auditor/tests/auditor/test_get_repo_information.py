# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from unittest.mock import patch
from edfi_repo_auditor.auditor import get_repo_information
from edfi_repo_auditor.checklist import CHECKLIST, CHECKLIST_DEFAULT_SUCCESS_MESSAGE

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"


def describe_when_getting_repo_info() -> None:
    def describe_branch_protection() -> None:
        def describe_given_there_are_no_protection_rules() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {"nodes": []},
                "branchProtectionRules": {"nodes": []},
                "hasWikiEnabled": False,
                "hasIssuesEnabled": False,
                "hasProjectsEnabled": False,
                "discussions": {"totalCount": 0},
                "deleteBranchOnMerge": False,
                "squashMergeAllowed": True,
                "licenseInfo": None,
            }

            @pytest.fixture
            @patch("edfi_repo_auditor.auditor.audit_alerts")
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_audit_alerts, mock_client) -> dict:
                mock_client.get_repository_information.return_value = RESPONSE
                mock_audit_alerts.return_value = {}
                return get_repo_information(mock_client, OWNER, REPO)

            def it_returns_no_rules(results: dict) -> None:
                assert (
                    results[CHECKLIST.SIGNED_COMMITS["description"]]
                    == CHECKLIST.SIGNED_COMMITS["fail"]
                )
                assert (
                    results[CHECKLIST.CODE_REVIEW["description"]]
                    == CHECKLIST.CODE_REVIEW["fail"]
                )
                assert (
                    results[CHECKLIST.REQUIRES_PR["description"]]
                    == CHECKLIST.REQUIRES_PR["fail"]
                )
                assert (
                    results[CHECKLIST.ADMIN_PR["description"]]
                    == CHECKLIST.ADMIN_PR["fail"]
                )

        def describe_given_there_are_protection_rules() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {"nodes": []},
                "branchProtectionRules": {
                    "nodes": [
                        {
                            "pattern": "main",
                            "requiresCommitSignatures": True,
                            "isAdminEnforced": True,
                            "requiresApprovingReviews": True,
                        }
                    ]
                },
                "hasWikiEnabled": False,
                "hasIssuesEnabled": False,
                "hasProjectsEnabled": False,
                "discussions": {"totalCount": 0},
                "deleteBranchOnMerge": False,
                "squashMergeAllowed": True,
                "licenseInfo": None,
            }

            @pytest.fixture
            @patch("edfi_repo_auditor.auditor.audit_alerts")
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_audit_alerts, mock_client) -> dict:
                mock_client.get_repository_information.return_value = RESPONSE
                mock_audit_alerts.return_value = {}
                return get_repo_information(mock_client, OWNER, REPO)

            def it_returns_rules_for_main(results: dict) -> None:
                assert (
                    results[CHECKLIST.SIGNED_COMMITS["description"]]
                    == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
                )
                assert (
                    results[CHECKLIST.CODE_REVIEW["description"]]
                    == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
                )
                assert (
                    results[CHECKLIST.REQUIRES_PR["description"]]
                    == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
                )
                assert (
                    results[CHECKLIST.ADMIN_PR["description"]]
                    == CHECKLIST.ADMIN_PR["fail"]
                )

        def describe_given_there_are_protection_rules_for_other_branch() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {"nodes": []},
                "branchProtectionRules": {
                    "nodes": [
                        {
                            "pattern": "feature",
                            "requiresCommitSignatures": True,
                            "isAdminEnforced": True,
                            "requiresApprovingReviews": True,
                        }
                    ]
                },
                "hasWikiEnabled": False,
                "hasIssuesEnabled": False,
                "hasProjectsEnabled": False,
                "discussions": {"totalCount": 0},
                "deleteBranchOnMerge": False,
                "squashMergeAllowed": True,
                "licenseInfo": {"key": "test-key"},
            }

            @pytest.fixture
            @patch("edfi_repo_auditor.auditor.audit_alerts")
            @patch("edfi_repo_auditor.github_client.GitHubClient")
            def results(mock_audit_alerts, mock_client) -> dict:
                mock_client.get_repository_information.return_value = RESPONSE
                mock_audit_alerts.return_value = {}
                return get_repo_information(mock_client, OWNER, REPO)

            def it_returns_rules_for_main(results: dict) -> None:
                assert (
                    results[CHECKLIST.SIGNED_COMMITS["description"]]
                    == CHECKLIST.SIGNED_COMMITS["fail"]
                )
                assert (
                    results[CHECKLIST.CODE_REVIEW["description"]]
                    == CHECKLIST.CODE_REVIEW["fail"]
                )
                assert (
                    results[CHECKLIST.REQUIRES_PR["description"]]
                    == CHECKLIST.REQUIRES_PR["fail"]
                )
                assert (
                    results[CHECKLIST.ADMIN_PR["description"]]
                    == CHECKLIST.ADMIN_PR["fail"]
                )
