# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

"""
GitHub Actions auditor that runs on a single repository and outputs
results to GitHub Actions job summary instead of generating HTML files.
"""

import json
import logging
import os
import re
import sys
from typing import List
from datetime import datetime, timedelta

from edfi_repo_auditor.checklist import (
    CHECKLIST,
    CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
    get_message,
)
from edfi_repo_auditor.config import Configuration
from edfi_repo_auditor.github_client import GitHubClient


logger: logging.Logger = logging.getLogger(__name__)

# Parameters to evaluate dependabot alerts
ALERTS_INCLUDED_SEVERITIES = ["CRITICAL", "HIGH"]
ALERTS_WEEKS_SINCE_CREATED = 3


def run_github_actions_audit(config: Configuration) -> None:
    """
    Run audit on a single repository and output results to GitHub Actions.

    Args:
        config: Configuration with repository details
    """
    client = GitHubClient(config.personal_access_token)

    # For GitHub Actions, we expect a single repository
    if len(config.repositories) != 1:
        logger.error("GitHub Actions auditor requires exactly one repository")
        sys.exit(1)

    repository = config.repositories[0]
    organization = config.organization

    logger.info(f"Auditing repository {organization}/{repository}")

    # Perform all audits
    repo_config = get_repo_information(client, organization, repository)
    actions = audit_actions(client, organization, repository)
    file_review = review_files(client, organization, repository)

    results = {**actions, **file_review, **repo_config}
    auditing_rules = get_scoring_rules()
    score = calculate_score(results, auditing_rules["rules"])

    # Determine overall result
    threshold = auditing_rules["threshold"]
    overall_result = "PASS" if score > threshold else "FAIL"

    # Output to GitHub Actions
    output_to_github_actions(repository, score, threshold, overall_result, results)

    logger.info(
        f"Audit complete. Score: {score}/{sum(auditing_rules['rules'].values())}, Result: {overall_result}"
    )


def audit_actions(client: GitHubClient, organization: str, repository: str) -> dict:
    """Audit GitHub Actions configuration."""
    audit_results: dict = {}

    actions = client.get_actions(organization, repository)

    logger.debug(f"Got {actions['total_count']} workflow files")

    audit_results[CHECKLIST.HAS_ACTIONS["description"]] = get_message(
        CHECKLIST.HAS_ACTIONS, actions["total_count"] > 0
    )

    ut_pattern = re.compile(r"unit.{0,2}test(s)?", flags=re.IGNORECASE)
    approved_actions_pattern = re.compile(
        r"uses:\s*ed-fi-alliance-oss/ed-fi-actions/.github/workflows/repository-scanner\.yml",
        flags=re.IGNORECASE,
    )
    workflow_paths = [
        workflow["path"] for workflow in actions["workflows"]
    ]

    for file_path in workflow_paths:
        file_content = client.get_file_content(organization, repository, file_path)
        if not file_content:
            logger.debug("File not found")
            continue

        if (
            CHECKLIST.APPROVED_ACTIONS["description"] not in audit_results
            or audit_results[CHECKLIST.APPROVED_ACTIONS["description"]]
            == CHECKLIST.APPROVED_ACTIONS["fail"]
        ):
            audit_results[CHECKLIST.APPROVED_ACTIONS["description"]] = get_message(
                CHECKLIST.APPROVED_ACTIONS,
                approved_actions_pattern.search(file_content) is not None,
            )

        if (
            CHECKLIST.TEST_REPORTER["description"] not in audit_results
            or audit_results[CHECKLIST.TEST_REPORTER["description"]]
            == CHECKLIST.TEST_REPORTER["fail"]
        ):
            audit_results[CHECKLIST.TEST_REPORTER["description"]] = get_message(
                CHECKLIST.TEST_REPORTER,
                "uses: dorny/test-reporter" in file_content
                or "uses: EnricoMi/publish-unit-test-result-action" in file_content,
            )

        if (
            CHECKLIST.UNIT_TESTS["description"] not in audit_results
            or audit_results[CHECKLIST.UNIT_TESTS["description"]]
            == CHECKLIST.UNIT_TESTS["fail"]
        ):
            audit_results[CHECKLIST.UNIT_TESTS["description"]] = get_message(
                CHECKLIST.UNIT_TESTS, ut_pattern.search(file_content) is not None
            )

    return audit_results


def get_repo_information(
    client: GitHubClient, organization: str, repository: str
) -> dict:
    """Get repository configuration information."""
    information = client.get_repository_information(organization, repository)

    dependabot_results = audit_alerts(
        client, organization, repository, information["vulnerabilityAlerts"]["nodes"]
    )

    # NOTE: We are NOT checking for signed commits as per requirements
    return {
        **{
            CHECKLIST.WIKI["description"]: get_message(
                CHECKLIST.WIKI, not information["hasWikiEnabled"]
            ),
            CHECKLIST.ISSUES["description"]: get_message(
                CHECKLIST.ISSUES, not information["hasIssuesEnabled"]
            ),
            CHECKLIST.PROJECTS["description"]: get_message(
                CHECKLIST.PROJECTS, not information["hasProjectsEnabled"]
            ),
            CHECKLIST.DISCUSSIONS["description"]: get_message(
                CHECKLIST.DISCUSSIONS, information["discussions"]["totalCount"] == 0
            ),
            CHECKLIST.DELETES_HEAD["description"]: get_message(
                CHECKLIST.DELETES_HEAD, information["deleteBranchOnMerge"]
            ),
            CHECKLIST.USES_SQUASH["description"]: get_message(
                CHECKLIST.USES_SQUASH, information["squashMergeAllowed"]
            ),
            CHECKLIST.LICENSE_INFORMATION["description"]: get_message(
                CHECKLIST.LICENSE_INFORMATION, information["licenseInfo"] is not None
            ),
        },
        **dependabot_results,
    }


def audit_alerts(
    client: GitHubClient, organization: str, repository: str, alerts: List[dict]
) -> dict:
    """Audit dependabot alerts."""
    vulnerabilities = [
        alert
        for alert in alerts
        if (
            alert["createdAt"]
            < (datetime.now() - timedelta(ALERTS_WEEKS_SINCE_CREATED * 7)).isoformat()
            and alert["securityVulnerability"]["advisory"]["severity"]
            in ALERTS_INCLUDED_SEVERITIES
        )
    ]
    total_vulnerabilities = len(vulnerabilities)

    dependabot_enabled = client.has_dependabot_enabled(organization, repository)
    return {
        CHECKLIST.DEPENDABOT_ENABLED["description"]: get_message(
            CHECKLIST.DEPENDABOT_ENABLED, dependabot_enabled
        ),
        CHECKLIST.DEPENDABOT_ALERTS["description"]: get_message(
            CHECKLIST.DEPENDABOT_ALERTS, total_vulnerabilities == 0
        ),
    }


def review_files(client: GitHubClient, organization: str, repository: str) -> dict:
    """Review required files in the repository."""
    file_audit: dict = {}

    files_to_review = [
        CHECKLIST.NOTICES,
        CHECKLIST.CODE_OF_CONDUCT,
    ]

    for file in files_to_review:
        file_found = False
        for filename in file["filename"]:
            if file_found:
                # There are multiple possible file names, and one of them was already detected
                break
            file_found = (
                client.get_file_content(organization, repository, filename) is not None
            )

        file_audit[file["description"]] = get_message(file, file_found)

    return file_audit


def calculate_score(results: dict, rules: dict) -> int:
    """Calculate the total score based on audit results."""
    score = 0

    for property in rules:
        try:
            if results[property] == CHECKLIST_DEFAULT_SUCCESS_MESSAGE:
                score += rules[property]
        except KeyError:
            logger.info(f"Unable to read property {property} in results")

    return score


def get_scoring_rules() -> dict:
    """Load scoring rules from scoring.json, excluding signed commits."""
    scoring_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "scoring.json"
    )

    with open(scoring_file, "r") as file:
        rules = json.loads(file.read())

    # Remove "Requires Signed commits" from the rules as per requirements
    if "Requires Signed commits" in rules["rules"]:
        del rules["rules"]["Requires Signed commits"]

    return rules


def output_to_github_actions(
    repository: str, score: int, threshold: int, overall_result: str, results: dict
) -> None:
    """
    Output audit results to GitHub Actions job summary.

    Args:
        repository: Repository name
        score: Calculated score
        threshold: Threshold for passing
        overall_result: PASS or FAIL
        results: Dictionary of all audit results
    """
    github_output = os.getenv("GITHUB_OUTPUT")
    github_step_summary = os.getenv("GITHUB_STEP_SUMMARY")

    # Set outputs for use in subsequent steps
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"score={score}\n")
            f.write(f"result={overall_result}\n")

    # Create a markdown summary
    summary = f"""# Repository Audit Results: {repository}

## Overall Result: {overall_result}

**Score:** {score} / {threshold} (threshold)

## Audit Details

| Check | Result |
|-------|--------|
"""

    # Sort results for consistent output
    for check, result in sorted(results.items()):
        status_emoji = "✅" if result == CHECKLIST_DEFAULT_SUCCESS_MESSAGE else "❌"
        summary += f"| {check} | {status_emoji} {result} |\n"

    # Write to job summary
    if github_step_summary:
        with open(github_step_summary, "a") as f:
            f.write(summary)

    # Also print to stdout
    print(summary)
