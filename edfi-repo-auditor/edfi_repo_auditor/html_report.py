# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

# This is a stand-alone script for converting JSON output files to HTML

from datetime import datetime
import json
import os
from typing import Dict, List

# Enable running from this directory or from parent
DIRECTORY = "../reports" if os.path.exists("../reports") else "reports"


def convert(file_name: str, file_contents: str, lines: List[str]) -> List[str]:
    file_name = file_name.split(".")[0]
    lines.append(f"<h2>{file_name}</h2>")

    doc: Dict[str, dict] = json.loads(file_contents)
    for repository in doc.keys():
        lines.append(f"<h3>{repository}</h3>")
        repo_data: dict = doc[repository]
        score: int = repo_data["score"]
        result: str = repo_data["result"]

        if result == "OK":
            lines.append(f"<p>🟢 Score: {score}")
        else:
            lines.append(f"<p>🔴 Score: {score}")

        lines.append("<p>Findings:</p>")
        lines.append("<ul>")
        description: Dict[str, str] = repo_data["description"]
        for key in description.keys():
            value = description[key]
            if value == "OK":
                continue
            else:
                lines.append(f"<li>{key}: {value}")
        lines.append("</ul>")

    return lines


def read_files() -> str:
    lines: List[str] = []

    for file_entry in os.scandir(f"{DIRECTORY}"):
        if file_entry.is_file() and file_entry.name.endswith(".json"):
            with open(file_entry.path) as f:
                lines = convert(file_entry.path, f.read(), lines)

    return "\n".join(lines)


def write_consolidated_file(contents: str) -> None:
    now = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M-%S")
    with open(f"{DIRECTORY}/{now}.html", mode="w", encoding="utf-8") as f:
        f.write(
            f"""
<html>
<head>
    <title>Consolidated Repo Scan, {datetime.now()}</title>
</head>
<body>
{contents}
</body>
</html>
"""
        )


def convert_to_html():
    contents = read_files()
    write_consolidated_file(contents)


if __name__ == "__main__":
    convert_to_html()
