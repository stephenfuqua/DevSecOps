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
    
    min_df = df[df.date == min_date][["project", "mean"]]
    max_df = df[df.date == max_date][["project", "mean"]]
    
    improvements = min_df.merge(max_df, on="project", suffixes=("_o", "_c"))
    improvements.rename(columns={"mean_o": "original", "mean_c": "current"}, inplace=True)
    improvements["delta"] = (improvements["original"] - improvements["current"]) / improvements["original"]
    return improvements