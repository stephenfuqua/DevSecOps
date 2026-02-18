# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from unittest.mock import patch
from edfi_repo_auditor.auditor import get_repo_information

# from edfi_repo_auditor.checklist import CHECKLIST, CHECKLIST_DEFAULT_SUCCESS_MESSAGE

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"


def describe_when_getting_repo_info() -> None:
    def describe_rulesets() -> None:
        def describe_given_there_are_no_rulesets() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {"nodes": []},
                "rulesets": {"nodes": []},
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
                    str(results)
                    == "{'Wiki Disabled': 'OK', 'Issues Enabled': 'WARNING: Issues are not enabled', 'Projects Disabled': 'OK', 'Deletes head branch': 'No. Branch should be deleted on merge', 'Uses Squash Merge': 'OK', 'License Information': 'License not found'}"
                )

        def describe_given_there_are_active_rulesets_for_main_branch() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {"nodes": []},
                "rulesets": {
                    "nodes": [
                        {
                            "enforcement": "ACTIVE",
                            "conditions": {"refName": {"include": ["main"]}},
                            "rules": {"nodes": [{"type": "REQUIRED_SIGNATURES"}]},
                        }
                    ]
                },
                "hasWikiEnabled": False,
                "hasIssuesEnabled": True,
                "hasProjectsEnabled": False,
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
                    str(results)
                    == "{'Wiki Disabled': 'OK', 'Issues Enabled': 'OK', 'Projects Disabled': 'OK', 'Deletes head branch': 'No. Branch should be deleted on merge', 'Uses Squash Merge': 'OK', 'License Information': 'License not found'}"
                )

        def describe_given_there_are_active_rulesets_for_other_branch() -> None:
            RESPONSE = {
                "vulnerabilityAlerts": {"nodes": []},
                "rulesets": {
                    "nodes": [
                        {
                            "enforcement": "ACTIVE",
                            "conditions": {"refName": {"include": ["feature"]}},
                            "rules": {"nodes": [{"type": "REQUIRED_SIGNATURES"}]},
                        }
                    ]
                },
                "hasWikiEnabled": False,
                "hasIssuesEnabled": True,
                "hasProjectsEnabled": False,
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
                    str(results)
                    == "{'Wiki Disabled': 'OK', 'Issues Enabled': 'OK', 'Projects Disabled': 'OK', 'Deletes head branch': 'No. Branch should be deleted on merge', 'Uses Squash Merge': 'OK', 'License Information': 'OK'}"
                )
