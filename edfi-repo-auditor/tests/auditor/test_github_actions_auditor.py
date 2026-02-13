# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from edfi_repo_auditor.github_actions_auditor import (
    get_scoring_rules,
    calculate_score,
)
from edfi_repo_auditor.checklist import CHECKLIST, CHECKLIST_DEFAULT_SUCCESS_MESSAGE


def describe_when_getting_scoring_rules() -> None:
    @pytest.fixture
    def rules() -> dict:
        return get_scoring_rules()

    def it_loads_rules_from_json(rules: dict) -> None:
        assert "rules" in rules
        assert "threshold" in rules

    def it_excludes_signed_commits(rules: dict) -> None:
        assert "Requires Signed commits" not in rules["rules"]

    def it_includes_other_checks(rules: dict) -> None:
        assert "Has Actions" in rules["rules"]
        assert "Dependabot Enabled" in rules["rules"]


def describe_when_calculating_score() -> None:
    def describe_given_all_passing_results() -> None:
        RESULT = {
            CHECKLIST.HAS_ACTIONS["description"]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
            CHECKLIST.APPROVED_ACTIONS["description"]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
            CHECKLIST.LICENSE_INFORMATION[
                "description"
            ]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
        }

        RULES = {
            CHECKLIST.HAS_ACTIONS["description"]: 5,
            CHECKLIST.APPROVED_ACTIONS["description"]: 5,
            CHECKLIST.LICENSE_INFORMATION["description"]: 3,
        }

        @pytest.fixture
        def score() -> int:
            return calculate_score(RESULT, RULES)

        def it_sums_all_scores(score: int) -> None:
            assert score == 13

    def describe_given_mixed_results() -> None:
        RESULT = {
            CHECKLIST.HAS_ACTIONS["description"]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
            CHECKLIST.APPROVED_ACTIONS["description"]: CHECKLIST.APPROVED_ACTIONS[
                "fail"
            ],
            CHECKLIST.LICENSE_INFORMATION[
                "description"
            ]: CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
        }

        RULES = {
            CHECKLIST.HAS_ACTIONS["description"]: 5,
            CHECKLIST.APPROVED_ACTIONS["description"]: 5,
            CHECKLIST.LICENSE_INFORMATION["description"]: 3,
        }

        @pytest.fixture
        def score() -> int:
            return calculate_score(RESULT, RULES)

        def it_only_counts_passing_checks(score: int) -> None:
            assert score == 8
