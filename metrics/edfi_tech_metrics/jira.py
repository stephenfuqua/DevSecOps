# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
from typing import List, Tuple, Optional

from jira import JIRA, Issue
from jira.client import ResultList


from edfi_tech_metrics.settings import Configuration


@dataclass
class IssuePage:
    issue_list: List[Tuple[str, Optional[str]]]
    last_key: Optional[str]


class JiraBrowser():

    def __init__(self, conf: Configuration):
        self.conf = conf

        conf.info(f"Connecting to {conf.jira_base_url}")
        self.jira = JIRA(conf.jira_base_url, token_auth=conf.jira_token)

    def get_page_of_issues(self, project_key: str, begin: str) -> IssuePage:
        jql = f"project={project_key} {begin} AND resolution = Unresolved order by created asc"
        self.conf.debug(jql)
        issues: ResultList[Issue] = self.jira.search_issues(jql, maxResults=self.conf.page_size)  # type: ignore  # have never seen it return the alternate dictionary

        last: str = ""
        if len(issues) == self.conf.page_size:
            last = f"AND key >= {str(issues[-1].key)}"

        return IssuePage([(project_key, i.fields.created) for i in issues], last)

    def get_project(self, project: str) -> List[Tuple[str, Optional[str]]]:
        data = []

        begin = ""

        # "Do...While" type loop to get all pages of data.
        while True:
            page = self.get_page_of_issues(project, begin)

            data.extend(page.issue_list)

            if page.last_key == "":
                break

            # Next request to get_issues needs to look for items _after_ the last one received
            begin = page.last_key

        return data
