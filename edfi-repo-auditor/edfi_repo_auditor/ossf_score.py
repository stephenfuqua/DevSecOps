# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

"""Helpers to retrieve OpenSSF Scorecard metrics."""

import logging
import re
from typing import Dict, Optional

import requests

logger: logging.Logger = logging.getLogger(__name__)

_SCORECARD_URL_TEMPLATE = (
    "https://img.shields.io/ossf-scorecard/github.com/{org}/{repo}?"
    "label=openssf+scorecard&style=flat"
)
_TITLE_SCORE_REGEX = re.compile(
    r"<title>openssf scorecard:\s*([0-9]+(?:\.[0-9]+)?)</title>", re.IGNORECASE
)


def _extract_score(svg: str) -> Optional[float]:
    if not svg:
        return None
    match = _TITLE_SCORE_REGEX.search(svg)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        logger.debug("Unable to parse score from title: %s", match.group(1))
        return None


def get_ossf_score(organization: str, repository: str) -> Dict[str, Optional[float]]:
    """Fetch the OpenSSF Scorecard value for the provided repository."""

    url = _SCORECARD_URL_TEMPLATE.format(org=organization, repo=repository)
    try:
        response = requests.get(url, timeout=10, headers={"Accept": "image/svg+xml"})
        response.raise_for_status()
        score = _extract_score(response.text)
        if score is None:
            logger.warning(
                "OpenSSF score missing from response for %s/%s",
                organization,
                repository,
            )
        return {"OSSF Score": score}
    except requests.RequestException as exc:
        logger.warning(
            "Failed to fetch OpenSSF score for %s/%s: %s", organization, repository, exc
        )
        return {"OSSF Score": None}
