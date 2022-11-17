# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from edfi_repo_auditor.auditor import get_result
from edfi_repo_auditor.checklist import CHECKLIST, CHECKLIST_DEFAULT_SUCCESS_MESSAGE


def describe_when_getting_results() -> None:
    def describe_given_no_rules() -> None:
        CHECKLIST = {"Has Actions": 5, "Uses Allowed list": 5, "README.md": 3}

        @pytest.fixture
        def results() -> int:
            return get_result(CHECKLIST, {})

        def it_returns_0(results: int) -> None:
            assert results == 0

    def describe_given_property_not_in_checklist() -> None:
        RESULT = {
            CHECKLIST.LICENSE_INFORMATION[
                "description"
            ]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
            CHECKLIST.README["description"]: CHECKLIST.README["fail"],
        }

        RULES = {
            CHECKLIST.HAS_ACTIONS["description"]: 5,
            CHECKLIST.LICENSE_INFORMATION["description"]: 5,
            CHECKLIST.README["description"]: 3,
        }

        @pytest.fixture
        def results() -> int:
            return get_result(RESULT, RULES)

        def it_adds_the_existing_properties(results: int) -> None:
            assert results == 5

    def describe_given_values_are_present() -> None:
        RESULT = {
            CHECKLIST.HAS_ACTIONS["description"]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
            CHECKLIST.APPROVED_ACTIONS["description"]: CHECKLIST.APPROVED_ACTIONS[
                "fail"
            ],
            CHECKLIST.README["description"]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
        }

        RULES = {
            CHECKLIST.HAS_ACTIONS["description"]: 5,
            CHECKLIST.APPROVED_ACTIONS["description"]: 5,
            CHECKLIST.README["description"]: 3,
        }

        @pytest.fixture
        def results() -> int:
            return get_result(RESULT, RULES)

        def it_adds_the_properties(results: int) -> None:
            assert results == 8
