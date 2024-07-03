# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional

from jira import JIRA, Issue
from jira.client import ResultList
import pandas as pd
import tzlocal

from edfi_tech_metrics.settings import Configuration

# This value varies from one installation to the next. The following constant was discovered
# by inspecting the output from `GET https://tracker.ed-fi.org/rest/agile/1.0/board/167/backlog`
STORY_POINTS_FIELD = "customfield_10004"


@dataclass
class IssuePage:
    issue_list: List[Tuple[str, ...]]
    last_key: Optional[str]


class JiraBrowser:

    def __init__(self, conf: Configuration):
        self.conf = conf

        conf.info(f"Connecting to {conf.jira_base_url}")
        self.jira = JIRA(conf.jira_base_url, token_auth=conf.jira_token)

    def get_page_of_issues(self, project_key: str, begin: str) -> IssuePage:
        jql = f"project={project_key} {begin} AND resolution = Unresolved order by created asc"

        self.conf.debug(jql)
        fields = f"{STORY_POINTS_FIELD},key,created,fixVersions,issuetype"
        issues: ResultList[Issue] = self.jira.search_issues(jql, maxResults=self.conf.page_size, fields=fields)  # type: ignore  # have never seen it return the alternate dictionary

        last: str = ""
        if len(issues) == self.conf.page_size:
            last = f"AND key >= {str(issues[-1].key)}"

        return IssuePage(
            [
                (
                    project_key,
                    i.key,
                    i.fields.created,
                    i.fields.customfield_10004,
                    i.fields.fixVersions,
                    i.fields.issuetype.name,
                )
                for i in issues
            ],
            last,
        )

    def get_project(self, project: str) -> List[Tuple[str, ...]]:
        data = []

        begin = ""

        # "Do...While" type loop to get all pages of data.
        while True:
            page = self.get_page_of_issues(project, begin)

            data.extend(page.issue_list)

            if page.last_key == "":
                break

            # Next request to get_issues needs to look for items _after_ the last one received
            begin = page.last_key or ""

        return data

    def get_unresolved_tickets(self, projects: List[str]) -> pd.DataFrame:
        now = datetime.now(tzlocal.get_localzone())

        data = []
        for p in projects:
            self.conf.info(f"Retrieving tickets for {p}")
            data.extend(self.get_project(p))

        df = pd.DataFrame(
            columns=["project", "key", "created", "points", "fixVersions", "issuetype"],
            data=data,
        )

        df["created"] = pd.to_datetime(df["created"], utc=True)
        df["age"] = (now - df["created"]).dt.components.days

        return df
