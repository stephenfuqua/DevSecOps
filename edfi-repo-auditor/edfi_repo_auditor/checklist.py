# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from collections import namedtuple

CHECKLIST_DEFAULT_SUCCESS_MESSAGE = "✅ OK"

checklist = namedtuple(
    "checklist",
    [
        "HAS_ACTIONS",
        "APPROVED_ACTIONS",
        "TEST_REPORTER",
        "UNIT_TESTS",
        "WIKI",
        "ISSUES",
        "PROJECTS",
        "DELETES_HEAD",
        "USES_SQUASH",
        "LICENSE_INFORMATION",
        "DEPENDABOT_ENABLED",
        "DEPENDABOT_ALERTS",
        "NOTICES",
        "CODE_OF_CONDUCT",
    ],
)

CHECKLIST = checklist(
    HAS_ACTIONS={"description": "Has Actions", "fail": "❌ FAILED: Repo is not using GH Actions"},
    APPROVED_ACTIONS={
        "description": "Uses only approved GitHub Actions",
        "fail": "❌ FAILED: No. Consider using only approved GH Actions",
    },
    TEST_REPORTER={"description": "Uses Test Reporter", "fail": "❌ FAILED: Not found"},
    UNIT_TESTS={"description": "Has Unit Tests", "fail": "❌ FAILED: `Not found"},
    WIKI={"description": "Wiki Disabled", "fail": "⚠️ WARNING: Wiki is enabled"},
    ISSUES={"description": "Issues Enabled", "fail": "⚠️ WARNING: Issues are not enabled"},
    PROJECTS={
        "description": "Projects Disabled",
        "fail": "⚠️ WARNING: Projects are enabled",
    },
    DELETES_HEAD={
        "description": "Deletes head branch",
        "fail": "❌ FAILED: Branch should be deleted on merge",
    },
    USES_SQUASH={
        "description": "Uses Squash Merge",
        "fail": "❌ FAILED: Should use squash merges",
    },
    LICENSE_INFORMATION={
        "description": "License Information",
        "fail": "❌ FAILED: License not found",
    },
    DEPENDABOT_ENABLED={
        "description": "Dependabot Enabled",
        "fail": "❌ FAILED: Dependabot is not enabled",
    },
    DEPENDABOT_ALERTS={
        "description": "Dependabot Alerts",
        "fail": "⚠️ WARNING: Review existing alerts and dependabot status",
    },
    CODE_OF_CONDUCT={
        "description": "Has CODE_OF_CONDUCT",
        "filename": ["CODE_OF_CONDUCT.md"],
        "fail": "⚠️ WARNING: File not found",
    },
    NOTICES={
        "description": "Has NOTICES",
        "filename": ["NOTICES.md"],
        "fail": "⚠️ WARNING: File not found",
    },
)


def get_message(property: dict, flag: bool) -> str:
    return CHECKLIST_DEFAULT_SUCCESS_MESSAGE if flag else property["fail"]
