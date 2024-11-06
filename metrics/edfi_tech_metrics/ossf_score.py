# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import requests
import math as Math
import os
import pandas as pd
from datetime import datetime

CA_FILE = "c:\msdfrootca.cer"

# Function to fetch OSSF score
def get_ossf_score(organization, repository):
    url = f"https://api.securityscorecards.dev/projects/github.com/{organization}/{repository}"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        return data["score"]
    else:
        return None


# Function to report OSSF scores for multiple repositories
def report_ossf_scores(repositories):
    scores = {}
    for repo in repositories:
        organization, repository = repo.split("/")
        score = get_ossf_score(organization, repository)
        if score is not None:
            scores[repo] = score
        else:
            scores[repo] = Math.nan
    return scores


# Function to fetch repositories for an organization
def fetch_repositories(organization):
    url = f"https://api.github.com/orgs/{organization}/repos?per_page=100"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        repositories = [repo["full_name"] for repo in data]
        return repositories
    else:
        return []


def compare_with_previous_scores(current_scores):
    current_df = pd.DataFrame(list(current_scores.items()), columns=["Repository", "Current Score"])

    data_dir = "./data/ossf-scores/"
    today = datetime.now().strftime("%Y-%m-%d")
    csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv") and f != f"{today}.csv"]

    if not csv_files:
        print("No previous scores found for comparison.")
        return current_df, [], []

    previous_file = max(csv_files)
    previous_df = pd.read_csv(os.path.join(data_dir, previous_file))

    merged_df = pd.merge(current_df, previous_df, on="Repository", how="outer", suffixes=("", "_Previous"))

    merged_df["Score Difference"] = merged_df["Current Score"] - merged_df["Score"]
    merged_df["Percentage Change"] = (merged_df["Score Difference"] / merged_df["Score"]) * 100

    merged_df = merged_df[["Repository", "Current Score", "Score", "Score Difference", "Percentage Change"]]
    merged_df.columns = ["Repository", "Current Score", "Previous Score", "Score Difference", "Percentage Change"]

    # Identify repositories with significant changes
    improved_repos = merged_df[merged_df["Percentage Change"] >= 10]["Repository"].tolist()
    worsened_repos = merged_df[merged_df["Percentage Change"] <= -10]["Repository"].tolist()

    return merged_df, improved_repos, worsened_repos
