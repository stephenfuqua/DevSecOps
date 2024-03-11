# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
from typing import List, Tuple, Optional

from jira import JIRA


from edfi_tech_metrics.settings import Configuration


@dataclass
class IssuePage:
    issue_list: List[Tuple[str, Optional[str]]]
    last_key: str


class JiraBrowser():

    def __init__(self, conf: Configuration):
        self.conf = conf

        conf.info(f"Connecting to {conf.jira_base_url}")
        self.jira = JIRA(conf.jira_base_url, token_auth=conf.jira_token)

    def get_page_of_issues(self, project_key: str, begin: str) -> IssuePage:
        jql = f"project={project_key} AND key {begin} AND resolution = Unresolved order by created asc"
        self.conf.debug(jql)
        issues = self.jira.search_issues(jql, maxResults=self.conf.page_size)

        last = None
        if len(issues) == self.conf.page_size:
            last = issues[-1].key

        return IssuePage([(project_key, i.fields.created) for i in issues], last)

    def get_project(self, project: str) -> List[List[str]]:
        data = []

        begin = f">= {project}-1"

        # "Do...While" type loop to get all pages of data.
        while True:
            page = self.get_page_of_issues(project, begin)

            data.extend(page.issue_list)

            if page.last_key is None:
                break

            # Next request to get_issues needs to look for items _after_ the last one received
            begin = f"> {page.last_key}"

        return data
