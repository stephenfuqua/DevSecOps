# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from unittest.mock import patch
from edfi_repo_auditor.auditor import audit_actions
from edfi_repo_auditor.checklist import CHECKLIST, CHECKLIST_DEFAULT_SUCCESS_MESSAGE

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"


def describe_when_auditing_actions() -> None:
    def describe_given_reviewing_allowed_list() -> None:
        @pytest.fixture
        def actions() -> dict:
            return {"total_count": 1, "workflows": [{"path": "test-action.yml"}]}

        @patch("edfi_repo_auditor.github_client.GitHubClient")
        def it_returns_fail_message_when_uses_any_action(
            mock_client, actions: dict
        ) -> None:
            file_content = """
                - name: Scan
                  uses: fake-action/allowed-list
            """
            mock_client.get_actions.return_value = actions
            mock_client.get_file_content.return_value = file_content
            results = audit_actions(mock_client, OWNER, REPO)
            assert (
                results[CHECKLIST.APPROVED_ACTIONS["description"]]
                == CHECKLIST.APPROVED_ACTIONS["fail"]
            )

        @patch("edfi_repo_auditor.github_client.GitHubClient")
        def it_returns_success_message_when_uses_approved_actions(
            mock_client, actions: dict
        ) -> None:
            file_content = """
                - name: Scan
                  uses: ed-fi-alliance-oss/ed-fi-actions/.github/workflows/repository-scanner.yml
            """
            mock_client.get_actions.return_value = actions
            mock_client.get_file_content.return_value = file_content
            results = audit_actions(mock_client, OWNER, REPO)
            assert (
                results[CHECKLIST.APPROVED_ACTIONS["description"]]
                == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
            )

    def describe_given_reviewing_test_reporter() -> None:
        @pytest.fixture
        def actions() -> dict:
            return {"total_count": 1, "workflows": [{"path": "test-action.yml"}]}

        @patch("edfi_repo_auditor.github_client.GitHubClient")
        def it_returns_fail_message_when_no_test_reporter(
            mock_client, actions: dict
        ) -> None:
            file_content = """
                - name: Integration Tests
            """
            mock_client.get_actions.return_value = actions
            mock_client.get_file_content.return_value = file_content
            results = audit_actions(mock_client, OWNER, REPO)
            assert (
                results[CHECKLIST.TEST_REPORTER["description"]]
                == CHECKLIST.TEST_REPORTER["fail"]
            )

        @patch("edfi_repo_auditor.github_client.GitHubClient")
        def it_returns_success_message_when_has_test_reporter(
            mock_client, actions: dict
        ) -> None:
            file_content = """
                - name: Integration Tests Report
                uses: dorny/test-reporter
            """
            mock_client.get_actions.return_value = actions
            mock_client.get_file_content.return_value = file_content
            results = audit_actions(mock_client, OWNER, REPO)
            assert (
                results[CHECKLIST.TEST_REPORTER["description"]]
                == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
            )

    def describe_given_reviewing_unit_tests() -> None:
        @pytest.fixture
        def actions() -> dict:
            return {"total_count": 1, "workflows": [{"path": "test-action.yml"}]}

        @patch("edfi_repo_auditor.github_client.GitHubClient")
        def it_returns_success_message_when_has_unit_tests(
            mock_client, actions: dict
        ) -> None:
            file_content = """
                - name: Unit Tests with coverage
            """

            mock_client.get_actions.return_value = actions
            mock_client.get_file_content.return_value = file_content
            results = audit_actions(mock_client, OWNER, REPO)
            assert (
                results[CHECKLIST.UNIT_TESTS["description"]]
                == CHECKLIST_DEFAULT_SUCCESS_MESSAGE
            )

        @patch("edfi_repo_auditor.github_client.GitHubClient")
        def it_returns_fail_message_when_no_unit_tests(
            mock_client, actions: dict
        ) -> None:
            file_content = """
                - name: Integration Tests
            """
            mock_client.get_actions.return_value = actions
            mock_client.get_file_content.return_value = file_content
            results = audit_actions(mock_client, OWNER, REPO)
            assert (
                results[CHECKLIST.UNIT_TESTS["description"]]
                == CHECKLIST.UNIT_TESTS["fail"]
            )
