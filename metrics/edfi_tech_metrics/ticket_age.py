# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
from datetime import datetime
from typing import List

import pandas as pd
from plotnine import (
    aes,
    geom_density,
    annotate,
    geom_vline,
    ggplot,
    theme_bw,
    labs,
)
import numpy as np
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


# From https://plotnine.org/reference/geom_density.html#plotnine.geom_density
class geom_density_highlight(geom_density):
    def __init__(self, *args, region=(-np.inf, np.inf), **kwargs):
        super().__init__(*args, **kwargs)
        self.region = region

    def setup_data(self, data):
        data = super().setup_data(data)
        s = f"{self.region[0]} <= x <= {self.region[1]}"
        data = data.query(s).reset_index(drop=True)
        return data


def build_report_components(
    projects: List[str], df: pd.DataFrame
) -> List[ReportProject]:

    stats = []
    teal = "#029386"

    for project in projects:
        filtered = df[df["project"] == project]

        s = filtered["age"].std()
        m = filtered["age"].mean()
        region = (m - s, m + s)

        p = (
            ggplot(filtered, aes(x="age"))
            + geom_density_highlight(region=region, fill=teal + "88", color="none")
            + geom_density(fill=teal + "44", color=teal, size=0.7)
            + annotate(geom_vline, xintercept=m)
            + annotate(geom_vline, xintercept=region, color=teal, size=0.7)  # type: ignore  # xintercept accepting a tuple instead of a float must be undocumented
            + labs(
                title=f"Unresolved Ticket Age for {project}", x="Age", y="Proportion"
            )
            + theme_bw()
        )

        t = filtered.rename(columns={"age": project})
        t = t.describe().transpose()

        stats.append(ReportProject(t, p))

    return stats
