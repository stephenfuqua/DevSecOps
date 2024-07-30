# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
from typing import List, Optional
from json import dumps

import base64
import pandas as pd
import requests
from requests import Response

from edfi_repo_auditor.log_helper import http_error

API_URL = "https://api.github.com"
GRAPHQL_ENDPOINT = f"{API_URL}/graphql"

REPO_TOKEN = "[REPOSITORY]"
ORG_TOKEN = "[OWNER]"

# Note that this doesn't handle paging and thus will not be sufficient if there
# are more than 100 repositories.
REPOSITORIES_TEMPLATE = """
{
  organization(login: "[OWNER]") {
    id
    repositories(first: 100) {
      totalCount
      nodes {
        name
      }
    }
  }
}
""".strip()

# Note that this doesn't handle paging and thus will not be sufficient if there
# are more than 100 alerts.
REPOSITORY_INFORMATION_TEMPLATE = """
{
  repository(name: "[REPOSITORY]", owner: "[OWNER]") {
    vulnerabilityAlerts(first: 100, states: [OPEN]) {
      nodes {
        createdAt
        securityVulnerability {
          package {
            name
          }
          advisory {
            severity
          }
        }
      }
    }
    rulesets(first: 10) {
      nodes {
        bypassActors(first: 10) {
          edges {
            node {
              organizationAdmin
              actor {
                __typename
              }
            }
          }
        }
        conditions {
          refName {
            include
          }
        }
        enforcement
        name
        rules(first: 20) {
          nodes {
            type
          }
        }
        target
      }
    }
    hasWikiEnabled
    hasIssuesEnabled
    hasProjectsEnabled
    discussions {
      totalCount
    }
    deleteBranchOnMerge
    squashMergeAllowed
    licenseInfo {
      key
    }
  }
}
""".strip()

logger: logging.Logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self, access_token: str):
        if len(access_token.strip()) == 0:
            raise ValueError("access_token cannot be blank")
        self.access_token = access_token

    def _execute_api_call(
        self, description: str, method: str, url: str, payload: str = ""
    ) -> dict:
        headers = {
            "Authorization": f"bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        logger.debug(f"{description}")

        response: Response = requests.request(
            method, url, headers=headers, data=payload
        )

        if response.status_code == requests.codes.ok:
            body = response.json()

            # GitHub API will return 200 with error messages if the query is malformed.
            if "errors" in body:
                msg = f"Query for {description}."
                raise http_error(msg, response)

            return body
        elif response.status_code == requests.codes.no_content:
            # There's a failure when attempting to convert a 204 response to JSON
            return {"status_code": response.status_code}
        else:
            msg = f"Query for {description}."
            raise http_error(msg, response)

    def _execute_graphql(self, description: str, query: str) -> dict:
        payload = dumps({"query": query, "variables": {}})

        body = self._execute_api_call(
            f"Querying for {description}", "POST", f"{GRAPHQL_ENDPOINT}", payload
        )

        return body

    def get_repositories(self, owner: str) -> List[str]:
        logger.info(f"Getting all repositories for organization {owner}")
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")

        query = REPOSITORIES_TEMPLATE.replace(ORG_TOKEN, owner)
        body = self._execute_graphql(f"repositories for {owner}", query)

        total_repos = body["data"]["organization"]["repositories"]["totalCount"]
        if total_repos > 100:
            logger.warning(
                f"There are over 100 repos in {owner}. Update the query to handle pagination"
            )

        df = pd.DataFrame(body["data"]["organization"]["repositories"]["nodes"])
        return df["name"].to_list()

    def get_actions(self, owner: str, repository: str) -> dict:
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        actions = self._execute_api_call(
            f"Getting actions for {owner}/{repository}",
            "GET",
            f"{API_URL}/repos/{owner}/{repository}/actions/workflows",
        )
        return actions

    def get_repository_information(self, owner: str, repository: str) -> dict:
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        query = REPOSITORY_INFORMATION_TEMPLATE.replace(ORG_TOKEN, owner).replace(
            REPO_TOKEN, repository
        )

        body = self._execute_graphql(
            f"protection rules for {owner}/{repository}", query
        )

        return body["data"]["repository"]

    def has_dependabot_enabled(self, owner: str, repository: str) -> bool:
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        has_dependabot = False
        try:
            dependabot = self._execute_api_call(
                f"Getting actions for {owner}/{repository}",
                "GET",
                f"{API_URL}/repos/{owner}/{repository}/vulnerability-alerts",
            )
            has_dependabot = dependabot["status_code"] == requests.codes.no_content
        except RuntimeError:
            has_dependabot = False

        return has_dependabot

    def get_file_content(self, owner: str, repository: str, path: str) -> Optional[str]:
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")
        if len(path.strip()) == 0:
            raise ValueError("path cannot be blank")

        file_result = None
        try:
            file_result = self._execute_api_call(
                f"Getting file {path} for {owner}/{repository}",
                "GET",
                f"{API_URL}/repos/{owner}/{repository}/contents/{path}",
            )
        except RuntimeError:
            pass

        return (
            base64.b64decode(file_result["content"]).decode("UTF-8")
            if file_result
            else None
        )
