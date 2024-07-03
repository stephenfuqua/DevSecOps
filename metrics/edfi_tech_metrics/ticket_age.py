# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_tech_metrics.settings import Configuration

from datetime import datetime
from typing import List
from pathlib import Path
from os import listdir, path

import pandas as pd
from plotnine import aes, ggplot, theme_bw, labs, geom_text, geom_boxplot, coord_flip


def _write_stats_file(
    conf: Configuration, df: pd.DataFrame, today: str, directory: str
) -> None:
    stats_df = df[["project", "age"]].groupby(by="project").describe()
    stats_df.reset_index(inplace=True)

    stats_df.columns = stats_df.columns.to_flat_index()
    stats_df.columns = [
        "project",
        "count",
        "mean",
        "std",
        "min",
        "25%",
        "50%",
        "75%",
        "max",
    ]

    stats_df["date"] = today

    Path(f"./data/{directory}").mkdir(parents=True, exist_ok=True)

    file_name = f"./data/{directory}/{today}.csv"
    conf.info(f"Writing age data out to file: {file_name}")
    stats_df.to_csv(file_name)


def write_ticket_age_files(conf: Configuration, df: pd.DataFrame) -> None:
    today = datetime.today().strftime("%Y-%m-%d")
    _write_stats_file(conf, df, today, "ticket-age")

    filtered = df[(df["issuetype"] != "Test") & (df["fixVersions"].notnull())]
    _write_stats_file(conf, filtered, today, "ticket-age-filtered")


def generate_ticket_age_plots(base_dir: str, projects: List[str]) -> None:
    files = [path.join(base_dir, f) for f in listdir(base_dir) if f.endswith(".csv")]

    file_frames = []
    for f in files:
        file_frames.append(pd.read_csv(f))

    df = pd.concat(file_frames)
    df.drop(columns=["Unnamed: 0"], inplace=True)
    df = df.round({"mean": 2})

    for p in projects:
        filtered = df[df["project"] == p]

        (
            ggplot(filtered, aes(x="factor(date)", color="date"))
            + geom_boxplot(
                aes(ymin="min", lower="25%", middle="50%", upper="75%", ymax="max"),
                stat="identity",
                show_legend=False,
                fatten=3,
            )
            + geom_text(
                aes(label="mean", y="mean"),
                color="black",
                show_legend=False,
                nudge_x=0.5,
            )
            + coord_flip()
            + labs(
                title=f"Unresolved Ticket Age for {p}", y="Age (Days)", x="Query Date"
            )
            + theme_bw()
        ).show()
