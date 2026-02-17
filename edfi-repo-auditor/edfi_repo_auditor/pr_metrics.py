# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

"""
PR Duration & Manager Metrics module.

This module provides functions to compute various metrics for pull requests,
including duration, lead time, review cycles, PR size, reviewer balance,
time-to-first-response, and more.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from edfi_repo_auditor.github_client import GitHubClient


logger: logging.Logger = logging.getLogger(__name__)

LAST_N_DAYS = 30


def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse an ISO 8601 datetime string to datetime object."""
    if dt_str is None:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def audit_pr_duration(
    merged_prs: List[Dict]
) -> Dict[str, object]:
    """
    Compute average PR duration for merged PRs only.

    Duration is calculated as (closed_at - created_at) for PRs with merged_at != None.
    No date filters are applied - all available merged PRs are included.

    Args:
        merged_prs: List of merged pull requests

    Returns:
        Dictionary with:
        - avg_pr_duration_days: Average duration in days (float or None if no merged PRs)
    """

    if len(merged_prs) == 0:
        return {
            "avg_pr_duration_days": None
        }

    durations = []
    for pr in merged_prs:
        created_at = _parse_datetime(pr.get("created_at"))
        closed_at = _parse_datetime(pr.get("closed_at"))

        if created_at is not None and closed_at is not None:
            duration = (closed_at - created_at).total_seconds() / 86400  # in days
            durations.append(duration)

    if not durations:
        return {
            "avg_pr_duration_days": None,
            "merged_pr_count": len(merged_prs),
        }

    avg_duration = sum(durations) / len(durations)

    return {
        "avg_pr_duration_days": round(avg_duration, 2)
    }


def audit_lead_time_for_change(
    merged_prs: List[Dict]
) -> Dict[str, object]:
    """
    Compute average lead time for change (time from PR creation to merge).

    Lead time is calculated as (merged_at - created_at) for merged PRs only.
    This is a proxy metric for the time from code being written to deployment.

    Args:
        merged_prs: List of merged pull requests

    Returns:
        Dictionary with:
        - avg_lead_time_days: Average lead time in days (float or None if no merged PRs)
    """

    if len(merged_prs) == 0:
        return {
            "avg_lead_time_days": None
        }

    lead_times = []
    for pr in merged_prs:
        created_at = _parse_datetime(pr.get("created_at"))
        merged_at = _parse_datetime(pr.get("merged_at"))

        if created_at is not None and merged_at is not None:
            lead_time = (merged_at - created_at).total_seconds() / 86400  # in days
            lead_times.append(lead_time)

    if not lead_times:
        return {
            "avg_lead_time_days": None
        }

    avg_lead_time = sum(lead_times) / len(lead_times)

    return {
        "avg_lead_time_days": round(avg_lead_time, 2)
    }



def audit_pr_review_cycle(
    reviews: Dict[int, Dict[str, object]]
) -> Dict[str, object]:
    """
    Compute PR review cycle metrics.

    Args:
        reviews: Mapping of PR number to PR metadata. Each value should include:
            - created_at: ISO 8601 timestamp for PR creation
            - reviews: List of review objects with state/submitted_at fields

    Returns:
        Dictionary with:
        - avg_time_to_first_approval_hours: Average time from PR open to first approval
        - avg_reviews_per_pr: Average number of reviews per PR
        - avg_approvals_per_pr: Average number of approvals per PR
    """

    if len(reviews) == 0:
        return {
            "avg_time_to_first_approval_hours": None,
            "avg_reviews_per_pr": None,
            "avg_approvals_per_pr": None
        }

    times_to_first_approval: List[float] = []
    review_counts: List[float] = []
    approval_counts: List[float] = []

    for pr_data in reviews.values():
        pr_reviews = pr_data.get("reviews", []) if isinstance(pr_data, dict) else []
        if not isinstance(pr_reviews, list):
            pr_reviews = []

        review_counts.append(float(len(pr_reviews)))

        approvals = [r for r in pr_reviews if r.get("state") == "APPROVED"]
        approval_counts.append(float(len(approvals)))

        created_at = None
        if isinstance(pr_data, dict):
            created_at = _parse_datetime(pr_data.get("created_at"))
            if created_at is None:
                pr_details = pr_data.get("pr")
                if isinstance(pr_details, dict):
                    created_at = _parse_datetime(pr_details.get("created_at"))

        if not approvals or created_at is None:
            continue

        approval_times: List[datetime] = []
        for approval in approvals:
            submitted = approval.get("submitted_at")
            if submitted is None:
                continue
            parsed = _parse_datetime(submitted)
            if parsed is not None:
                approval_times.append(parsed)

        if not approval_times:
            continue

        first_approval_time = min(approval_times)
        if first_approval_time >= created_at:
            hours = (first_approval_time - created_at).total_seconds() / 3600
            times_to_first_approval.append(hours)

    def _average(values: List[float]) -> Optional[float]:
        if not values:
            return None
        return round(sum(values) / len(values), 2)

    return {
        "avg_time_to_first_approval_hours": _average(times_to_first_approval),
        "avg_reviews_per_pr": _average(review_counts),
        "avg_approvals_per_pr": _average(approval_counts)
    }


def audit_reviewer_load_balance(
    reviews: Dict[int, List[Dict]]
) -> Dict[str, object]:
    """
    Compute reviewer load balance metrics

    Args:
        reviews: Dictionary of pull request reviews keyed by PR number

    Returns:
        Dictionary with:
        - top_reviewer_share_percent: Percentage of reviews done by top reviewer
        - top_3_reviewers_share_percent: Percentage of reviews done by top 3 reviewers
        - total_reviews: Total number of reviews
        - unique_reviewers: Number of unique reviewers
    """
    if len(reviews) == 0:
        return {
            "top_reviewer_share_percent": None,
            "top_3_reviewers_share_percent": None,
            "total_reviews": 0,
            "unique_reviewers": 0,
        }

    reviewer_counts: Dict[str, int] = {}

    for pr_reviews in reviews.values():
        for review in pr_reviews:
            reviewer = review.get("user")
            if reviewer:
                reviewer_counts[reviewer] = reviewer_counts.get(reviewer, 0) + 1

    total_reviewers = sum(reviewer_counts.values())
    if total_reviewers == 0:
        return {
            "top_reviewer_share_percent": None,
            "top_3_reviewers_share_percent": None,
            "total_reviews": 0,
            "unique_reviewers": 0,
        }

    sorted_reviewers = sorted(reviewer_counts.values(), reverse=True)

    top_reviewer_share = (sorted_reviewers[0] / total_reviewers) * 100
    top_3_sum = sum(sorted_reviewers[:3])
    top_3_share = (top_3_sum / total_reviewers) * 100

    return {
        "top_reviewer_share_percent": round(top_reviewer_share, 2),
        "top_3_reviewers_share_percent": round(top_3_share, 2),
        "total_reviewers": total_reviewers,
        "unique_reviewers": len(reviewer_counts),
    }


def get_pr_metrics(
    client: GitHubClient, owner: str, repository: str
) -> Dict[str, object]:
    """
    Get basic PR metrics (duration and lead time) combined into a single dictionary.

    For extended metrics (review cycle, size indicators, etc.), use the
    individual audit functions directly.

    Args:
        client: GitHubClient instance
        owner: Repository owner
        repository: Repository name

    Returns:
        Dictionary with basic PR metrics including avg_pr_duration_days,
        avg_lead_time_days, and merged_pr_count
    """
    logger.info(f"Computing PR metrics for {owner}/{repository}")

    prs: List[Dict] = client.get_pull_requests(owner, repository, state="closed")

    now_utc = datetime.now(timezone.utc)
    merged_prs: List[Dict] = []
    for pr in prs:
        merged_at_str = pr.get("merged_at")
        if merged_at_str is None:
            continue
        merged_at = _parse_datetime(merged_at_str)
        if merged_at is None:
            continue
        if (now_utc - merged_at).days <= LAST_N_DAYS:
            merged_prs.append(pr)

    reviews: Dict[int, List[Dict]] = {}
    for pr in merged_prs:
        try:
            reviews[pr.get("number")] = client.get_pull_request_reviews(owner, repository, pr["number"])
        except RuntimeError as e:
            logger.warning(f"Failed to fetch reviews for PR #{pr['number']}: {e}")

    duration = audit_pr_duration(merged_prs)
    review_cycle = audit_pr_review_cycle(reviews)
    lead_time = audit_lead_time_for_change(merged_prs)
    balance = audit_reviewer_load_balance(reviews)

    # Combine metrics
    return { "merged_pr_count": len(merged_prs) } | duration | review_cycle | lead_time | balance


