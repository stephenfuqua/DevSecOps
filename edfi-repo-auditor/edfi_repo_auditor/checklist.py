# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from collections import namedtuple

CHECKLIST_DEFAULT_SUCCESS_MESSAGE = "OK"

checklist = namedtuple("checklist", [
                      "HAS_ACTIONS",
                      "CODEQL",
                      "APPROVED_ACTIONS",
                      "TEST_REPORTER",
                      "UNIT_TESTS",
                      "LINTER",
                      "SIGNED_COMMITS",
                      "CODE_REVIEW",
                      "REQUIRES_PR",
                      "ADMIN_PR",
                      "WIKI",
                      "ISSUES",
                      "PROJECTS",
                      "DISCUSSIONS",
                      "DELETES_HEAD",
                      "USES_SQUASH",
                      "LICENSE_INFORMATION",
                      "DEPENDABOT_ENABLED",
                      "DEPENDABOT_ALERTS",
                      "README",
                      "CONTRIBUTORS",
                      "NOTICES",
                      "LICENSE"
                    ])

CHECKLIST = checklist(
              HAS_ACTIONS={
                "description": "Has Actions",
                "fail": "Repo is not using GH Actions"
              },
              CODEQL={
                "description": "Uses CodeQL",
                "fail": "CodeQL not found"
              },
              APPROVED_ACTIONS={
                "description": "Uses only approved GitHub Actions",
                "fail": "No. Consider using only approved GH Actions"
              },
              TEST_REPORTER={
                "description": "Uses Test Reporter",
                "fail": "Not found"
              },
              UNIT_TESTS={
                "description": "Has Unit Tests",
                "fail": "Not found"
              },
              LINTER={
                "description": "Has Linter",
                "fail": "Linting step not found"
              },
              SIGNED_COMMITS={
                "description": "Requires Signed commits",
                "fail": "No. Commits should be signed"
              },
              CODE_REVIEW={
                "description": "Requires Code review",
                "fail": "Code reviews are not required"
              },
              REQUIRES_PR={
                "description": "Requires PR",
                "fail": "Does not require PR"
              },
              ADMIN_PR={
                "description": "Admin cannot bypass PR",
                "fail": "Admin can bypass without PR"
              },
              WIKI={
                "description": "Wiki Disabled",
                "fail": "WARNING: Wiki is enabled"
              },
              ISSUES={
                "description": "Issues Disabled",
                "fail": "WARNING: Issues are enabled"
              },
              PROJECTS={
                "description": "Projects Disabled",
                "fail": "WARNING: Projects are enabled"
              },
              DISCUSSIONS={
                "description": "Discussions Disabled",
                "fail": "WARNING: Discussions are enabled"
              },
              DELETES_HEAD={
                "description": "Deletes head branch",
                "fail": "No. Branch should be deleted on merge"
              },
              USES_SQUASH={
                "description": "Uses Squash Merge",
                "fail": "No. Should use squash merges"
              },
              LICENSE_INFORMATION={
                "description": "License Information",
                "fail": "License not found"
              },
              DEPENDABOT_ENABLED={
                "description": "Dependabot Enabled",
                "fail": "Dependabot is not enabled"
              },
              DEPENDABOT_ALERTS={
                "description": "Dependabot Alerts",
                "fail": "WARNING: Review existing alerts and dependabot status"
              },
              README={
                "description": "Has README",
                "filename": ["README.md"],
                "fail": "File not found"
              },
              CONTRIBUTORS={
                "description": "Has CONTRIBUTORS",
                "filename": ["CONTRIBUTORS.md"],
                "fail": "File not found"
              },
              NOTICES={
                "description": "Has NOTICES",
                "filename": ["NOTICES.md"],
                "fail": "File not found"
              },
              LICENSE={
                "description": "Has LICENSE",
                "filename": ["LICENSE.txt", "LICENSE"],
                "fail": "LICENSE or LICENSE.txt file not found"
              })


def get_message(property: dict, flag: bool) -> str:
    return CHECKLIST_DEFAULT_SUCCESS_MESSAGE if flag else property["fail"]
