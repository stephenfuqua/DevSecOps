# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import List
from os import listdir, path
import pandas as pd


def calculate_improvements(base_dir: str, projects: List[str]) -> None:
    files = [path.join(base_dir, f) for f in listdir(base_dir) if f.endswith(".csv")]

    file_frames = []
    for f in files:
        file_frames.append(pd.read_csv(f))

    df = pd.concat(file_frames)

    min_date = df.date.min()
    max_date = df.date.max()

    delta_frames = []
    for p in projects:
        filtered = df.loc[df["project"] == p]
        original = filtered.loc[filtered["date"] == min_date, "mean"]
        current = filtered.loc[filtered["date"] == max_date, "mean"]
        delta = (original - current) / original
        # delta = round(delta, 2)

        delta_frames.append(
            pd.DataFrame(
                {"project": p, "original": original, "current": current, "delta": delta}
            )
        )

    delta_df = pd.concat(delta_frames)
    return delta_df
