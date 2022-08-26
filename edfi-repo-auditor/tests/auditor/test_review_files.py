# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from unittest.mock import patch
from edfi_repo_auditor.auditor import review_files
from edfi_repo_auditor.checklist import CHECKLIST, CHECKLIST_DEFAULT_SUCCESS_MESSAGE

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"
OWNER = "Ed-Fi-Alliance-OSS"
REPO = "Ed-Fi-ODS"


def describe_when_reviewing_files() -> None:
    def describe_given_all_files_found() -> None:
        FILES = {
            CHECKLIST.README["description"]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
            CHECKLIST.CONTRIBUTORS["description"]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
            CHECKLIST.NOTICES["description"]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
            CHECKLIST.LICENSE["description"]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
        }

        @pytest.fixture
        @patch('edfi_repo_auditor.github_client.GitHubClient')
        def results(mock_client) -> dict:
            mock_client.get_file_content.return_value = "Found"
            return review_files(mock_client, OWNER, REPO)

        def it_returns_success_message(results: dict) -> None:
            assert results == FILES

    def describe_given_files_not_found() -> None:
        FILES = {
            CHECKLIST.README["description"]: CHECKLIST.README["fail"],
            CHECKLIST.CONTRIBUTORS["description"]: CHECKLIST.CONTRIBUTORS["fail"],
            CHECKLIST.NOTICES["description"]: CHECKLIST.NOTICES["fail"],
            CHECKLIST.LICENSE["description"]: CHECKLIST.LICENSE["fail"],
        }

        @pytest.fixture
        @patch('edfi_repo_auditor.github_client.GitHubClient')
        def results(mock_client) -> dict:
            mock_client.get_file_content.return_value = None
            return review_files(mock_client, OWNER, REPO)

        def it_returns_fail_message(results: dict) -> None:
            print(results)
            assert results == FILES
