# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
import logging
import os
import re
import time
from typing import List
from datetime import datetime, timedelta

from pprint import pformat
import pandas as pd

from edfi_repo_auditor.checklist import (
    CHECKLIST,
    CHECKLIST_DEFAULT_SUCCESS_MESSAGE,
    get_message,
)

from edfi_repo_auditor.config import Configuration
from edfi_repo_auditor.github_client import GitHubClient
from edfi_repo_auditor.html_report import convert_to_html
from edfi_repo_auditor.pr_metrics import get_basic_pr_metrics


logger: logging.Logger = logging.getLogger(__name__)

# Parameters to evaluate dependabot alerts
ALERTS_INCLUDED_SEVERITIES = ["CRITICAL", "HIGH"]
ALERTS_WEEKS_SINCE_CREATED = 3


def run_audit(config: Configuration) -> None:
    start = time.time()
    client = GitHubClient(config.personal_access_token)

    repositories = (
        config.repositories
        if len(config.repositories) > 0
        else client.get_repositories(config.organization)
    )

    report_json: dict = {}
    report_data = []
    for repo in repositories:
        logger.info(f"Scanning repository {repo}")
        repo_config = get_repo_information(client, config.organization, repo)
        logger.debug(f"Repo configuration: {repo_config}")
        actions = audit_actions(client, config.organization, repo)
        logger.debug(f"Actions {actions}")
        file_review = review_files(client, config.organization, repo)
        logger.debug(f"Files: {file_review}")

        # Get PR metrics
        pr_metrics = get_basic_pr_metrics(client, config.organization, repo)
        logger.debug(f"PR Metrics: {pr_metrics}")

        results = {**actions, **file_review, **repo_config}
        auditing_rules = get_file()
        score = get_result(results, auditing_rules["rules"])
        logger.debug(f"Rules to follow: {auditing_rules}")

        report_json[repo] = {
            "score": score,
            "result": (
                "OK" if score > auditing_rules["threshold"] else "Action required"
            ),
            "description": results,
            "metrics": pr_metrics,
        }

        report_data.append(
            {
                "repository": repo,
                "result": (
                    "OK" if score > auditing_rules["threshold"] else "Action required"
                ),
                **actions,
                **file_review,
                **repo_config,
                **pr_metrics,
            }
        )

    df = pd.DataFrame(report_data)

    if config.save_results is True:
        save_to_json(report_json, config.file_name)
        save_to_csv(df, config.file_name)
        convert_to_html()

    else:
        logger.info(pformat(report_json))

    logger.info(
        f"Finished auditing repositories for {config.organization} in {'{:.2f}'.format(time.time() - start)} seconds"
    )


def audit_actions(client: GitHubClient, organization: str, repository: str) -> dict:
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
        actions["workflows"]["path"] for actions["workflows"] in actions["workflows"]
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
    information = client.get_repository_information(organization, repository)

    dependabot_results = audit_alerts(
        client, organization, repository, information["vulnerabilityAlerts"]["nodes"]
    )

    rulesForMain = [
        rule
        for ruleset in information["rulesets"]["nodes"]
        if any(
            "main" in refName for refName in ruleset["conditions"]["refName"]["include"]
        )
        for rule in ruleset["rules"]["nodes"]
    ]
    rules = rulesForMain if rulesForMain else None

    logger.debug(f"Repository information: {information}")
    logger.debug(f"Rules for main: {rules}")

    requires_signed_commits = any(
        rule.get("type") == "REQUIRED_SIGNATURES"
        for ruleset in information.get("rulesets", {}).get("nodes", [])
        if any(
            refName == "main" or refName == "~DEFAULT_BRANCH" or "main" in refName
            for refName in ruleset["conditions"]["refName"].get("include", [])
        )
        for rule in ruleset.get("rules", {}).get("nodes", [])
    )

    return {
        **{
            CHECKLIST.SIGNED_COMMITS["description"]: get_message(
                CHECKLIST.SIGNED_COMMITS, requires_signed_commits
            ),
            CHECKLIST.WIKI["description"]: get_message(
                CHECKLIST.WIKI, not information["hasWikiEnabled"]
            ),
            CHECKLIST.ISSUES["description"]: get_message(
                CHECKLIST.DISCUSSIONS, not information["hasIssuesEnabled"]
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
    vulnerabilities = [
        alerts
        for alerts in alerts
        if (
            alerts["createdAt"]
            < (datetime.now() - timedelta(ALERTS_WEEKS_SINCE_CREATED * 7)).isoformat()
            and alerts["securityVulnerability"]["advisory"]["severity"]
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


def get_result(results: dict, rules: dict) -> int:
    score = 0

    for property in rules:
        try:
            if results[property] == CHECKLIST_DEFAULT_SUCCESS_MESSAGE:
                score += rules[property]
        except KeyError:
            logger.info(f"Unable to read property {property} in results")

    return score


def save_to_json(report: dict, file_name: str) -> None:
    folder_name = "reports"

    path: str = ""
    if file_name:
        _, ext = os.path.splitext(file_name)
        if (not ext) or (ext != ".json"):
            file_name += ".json"
        path = f"{folder_name}/{file_name}"
    else:
        path = f"{folder_name}/audit-result.json"

    logger.info(f"Saving report to {path}")
    json_report = json.dumps(report, indent=4)

    if not os.path.exists(f"{folder_name}/"):
        os.mkdir(folder_name)

    with open(path, "w") as outfile:
        outfile.write(json_report)


def save_to_csv(report: pd.DataFrame, file_name: str) -> None:
    folder_name = "reports"

    path: str = ""
    if file_name:
        _, ext = os.path.splitext(file_name)
        if (not ext) or (ext != ".csv"):
            file_name += ".csv"
        path = f"{folder_name}/{file_name}"
    else:
        path = f"{folder_name}/audit-result.csv"

    logger.info(f"Saving report to {path}")

    report.to_csv(path, index=False)


def get_file() -> dict:
    with open("scoring.json", "r") as file:
        return json.loads(file.read())
