# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from datetime import datetime
from pathlib import Path
from typing import List

import ipywidgets as widgets
from IPython.display import display
import pandas as pd

# TODO: refactor out these globals, using proper function closures.
tickets_df = pd.DataFrame()
portfolio_list: List[str] = []


def get_portfolio_health(team: str, velocity: float) -> dict:
    global tickets_df
    global portfolio_list

    total_points = tickets_df[
        tickets_df["project"].isin(portfolio_list[team])  # type: ignore
    ].points.sum()

    return {
        "points": total_points,
        "velocity": velocity,
        "health": round(total_points / velocity),
    }


def build_health_report(
    data_standard: str, edfi_tools: str, ods_platform: str, team_b: str
) -> None:
    ds_v = float(data_standard)
    tools_v = float(edfi_tools)
    ods_v = float(ods_platform)
    b_v = float(team_b)

    health = {}
    health["Data Standard"] = get_portfolio_health("Data Standard", ds_v)
    health["Ed-Fi Tools"] = get_portfolio_health("Ed-Fi Tools", tools_v)
    health["ODS Platform"] = get_portfolio_health("ODS Platform", ods_v)
    health["Team B"] = get_portfolio_health("Team B", b_v)

    df_health = pd.DataFrame(health).transpose()

    display(df_health)

    path = "./data/backlog-health"
    Path(path).mkdir(parents=True, exist_ok=True)

    today = datetime.today().strftime("%Y-%m-%d")
    file_name = f"{path}/{today}.csv"
    # conf.info(f"Writing health data out to file: {file_name}")
    df_health.to_csv(file_name)


def run_backlog_health_ui(df: pd.DataFrame, portfolios: List[str]) -> None:
    global tickets_df
    global portfolio_list

    tickets_df = df
    portfolio_list = portfolios

    # Default to 1.0 to avoid temporary divide by zero
    _ = widgets.interact_manual(
        build_health_report,
        data_standard="1.0",
        edfi_tools="1.0",
        ods_platform="1.0",
        team_b="1.0",
    )
