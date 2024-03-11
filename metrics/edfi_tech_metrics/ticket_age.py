# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
from datetime import datetime
from typing import List

import pandas as pd
from plotnine import aes, geom_histogram, ggplot, after_stat, theme_bw, labs
import tzlocal

from edfi_tech_metrics.jira import JiraBrowser
from edfi_tech_metrics.settings import Configuration


def get_age_unresolved_tickets(
    conf: Configuration, browser: JiraBrowser, projects: List[str]
) -> pd.DataFrame:
    now = datetime.now(tzlocal.get_localzone())

    data = []
    for p in projects:
        conf.info(f"Retrieving tickets for {p}")
        data.extend(browser.get_project(p))

    df = pd.DataFrame(columns=["project", "created"], data=data)

    df["created"] = pd.to_datetime(df["created"], utc=True)
    df["age"] = (now - df["created"]).dt.components.days

    return df


@dataclass
class ReportProject:
    stats: pd.DataFrame
    histogram: ggplot


def build_report_components(
    projects: List[str], df: pd.DataFrame
) -> List[ReportProject]:

    stats = []

    for project in projects:
        filtered = df[df["project"] == project]

        p = (
            ggplot(filtered, aes(x="age", y=after_stat("width*density")))
            + geom_histogram(bins=7)
            + labs(
                title=f"Unresolved Ticket Age for {project}", x="Age", y="Proportion"
            )
            + theme_bw()
        )

        t = filtered.rename(columns={"age": project})
        t = t.describe().transpose()

        stats.append(ReportProject(t, p))

    return stats
