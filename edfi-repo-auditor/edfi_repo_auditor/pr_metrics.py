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

AVG_PR_DURATION_DAYS_KEY = "Avg PR Duration (days)"
MERGED_PR_COUNT_KEY = "Merged PR Count"
AVG_LEAD_TIME_DAYS_KEY = "Avg Lead Time (days)"
AVG_TIME_TO_FIRST_APPROVAL_HOURS_KEY = "Avg Time to First Approval (hours)"
AVG_REVIEWS_PER_PR_KEY = "Avg Reviews per PR"
AVG_APPROVALS_PER_PR_KEY = "Avg Approvals per PR"
TOP_REVIEWER_SHARE_PERCENT_KEY = "Top Reviewer Share (%)"
TOP_THREE_REVIEWERS_SHARE_PERCENT_KEY = "Top 3 Reviewers Share (%)"
TOTAL_REVIEWS_KEY = "Total Reviews"
UNIQUE_REVIEWERS_KEY = "Unique Reviewers"
MERGED_PRS_LAST_30_DAYS_KEY = "Number of Merged PRs (last 30 days)"


def _parse_datetime(dt_str: Optional[object]) -> Optional[datetime]:
    """Parse an ISO 8601 datetime string to datetime object."""
    if dt_str is None:
        return None
    try:
        return datetime.fromisoformat(str(dt_str).replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def audit_pr_duration(merged_prs: List[Dict]) -> Dict[str, object]:
    """
    Compute average PR duration for merged PRs only.

    Duration is calculated as (closed_at - created_at) for PRs with merged_at != None.
    No date filters are applied - all available merged PRs are included.

    Args:
        merged_prs: List of merged pull requests

    Returns:
        Dictionary with:
        - Avg PR Duration (days): Average duration in days (float or None if no merged PRs)
    """

    if len(merged_prs) == 0:
        return {AVG_PR_DURATION_DAYS_KEY: None}

    durations = []
    for pr in merged_prs:
        created_at = _parse_datetime(pr.get("created_at"))
        closed_at = _parse_datetime(pr.get("closed_at"))

        if created_at is not None and closed_at is not None:
            duration = (closed_at - created_at).total_seconds() / 86400  # in days
            durations.append(duration)

    if not durations:
        return {
            AVG_PR_DURATION_DAYS_KEY: None,
            MERGED_PR_COUNT_KEY: len(merged_prs),
        }

    avg_duration = sum(durations) / len(durations)

    return {AVG_PR_DURATION_DAYS_KEY: round(avg_duration, 2)}


def audit_lead_time_for_change(merged_prs: List[Dict]) -> Dict[str, object]:
    """
    Compute average lead time for change (time from PR creation to merge).

    Lead time is calculated as (merged_at - created_at) for merged PRs only.
    This is a proxy metric for the time from code being written to deployment.

    Args:
        merged_prs: List of merged pull requests

    Returns:
        Dictionary with:
        - Avg Lead Time (days): Average lead time in days (float or None if no merged PRs)
    """

    if len(merged_prs) == 0:
        return {AVG_LEAD_TIME_DAYS_KEY: None}

    lead_times = []
    for pr in merged_prs:
        created_at = _parse_datetime(pr.get("created_at"))
        merged_at = _parse_datetime(pr.get("merged_at"))

        if created_at is not None and merged_at is not None:
            lead_time = (merged_at - created_at).total_seconds() / 86400  # in days
            lead_times.append(lead_time)

    if not lead_times:
        return {AVG_LEAD_TIME_DAYS_KEY: None}

    avg_lead_time = sum(lead_times) / len(lead_times)

    return {AVG_LEAD_TIME_DAYS_KEY: round(avg_lead_time, 2)}


def audit_pr_review_cycle(reviews: Dict[int, List[Dict]]) -> Dict[str, object]:
    """
    Compute PR review cycle metrics.

    Args:
        reviews: Mapping of PR number to PR metadata. Each value should include:
            - reviews: List of review objects with state/submitted_at fields, plus the created_at field

    Returns:
        Dictionary with:
        - Avg Time to First Approval (hours): Average time from PR open to first approval
        - Avg Reviews per PR: Average number of reviews per PR
        - Avg Approvals per PR: Average number of approvals per PR
    """

    if len(reviews) == 0:
        return {
            AVG_TIME_TO_FIRST_APPROVAL_HOURS_KEY: None,
            AVG_REVIEWS_PER_PR_KEY: None,
            AVG_APPROVALS_PER_PR_KEY: None,
        }

    times_to_first_approval: List[float] = []
    review_counts: List[float] = []
    approval_counts: List[float] = []

    for pr_data in reviews.values():
        normalized_reviews: List[Dict] = []
        pr_created_at: Optional[datetime] = None

        if isinstance(pr_data, dict):
            potential_reviews = pr_data.get("reviews")
            if isinstance(potential_reviews, list):
                normalized_reviews = [r for r in potential_reviews if isinstance(r, dict)]
            elif pr_data.get("state"):
                normalized_reviews = [pr_data]
            pr_created_at = _parse_datetime(pr_data.get("created_at"))
        elif isinstance(pr_data, list):
            normalized_reviews = [r for r in pr_data if isinstance(r, dict)]

        review_counts.append(float(len(normalized_reviews)))

        approvals = [r for r in normalized_reviews if r.get("state") == "APPROVED"]
        approval_counts.append(float(len(approvals)))

        if pr_created_at is None:
            for review in normalized_reviews:
                pr_created_at = _parse_datetime(review.get("created_at"))
                if pr_created_at is not None:
                    break

        if not approvals or pr_created_at is None:
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
        if first_approval_time >= pr_created_at:
            hours = (first_approval_time - pr_created_at).total_seconds() / 3600
            times_to_first_approval.append(hours)

    def _average(values: List[float]) -> Optional[float]:
        if not values:
            return None
        return round(sum(values) / len(values), 2)

    return {
        AVG_TIME_TO_FIRST_APPROVAL_HOURS_KEY: _average(times_to_first_approval),
        AVG_REVIEWS_PER_PR_KEY: _average(review_counts),
        AVG_APPROVALS_PER_PR_KEY: _average(approval_counts),
    }


def audit_reviewer_load_balance(reviews: Dict[int, List[Dict]]) -> Dict[str, object]:
    """
    Compute reviewer load balance metrics

    Args:
        reviews: Dictionary of pull request reviews keyed by PR number

    Returns:
        Dictionary with:
        - Top Reviewer Share (%): Percentage of reviews done by top reviewer
        - Top 3 Reviewers Share (%): Percentage of reviews done by top 3 reviewers
        - Total Reviews: Total number of reviews
        - Unique Reviewers: Number of unique reviewers
    """
    if len(reviews) == 0:
        return {
            TOP_REVIEWER_SHARE_PERCENT_KEY: None,
            TOP_THREE_REVIEWERS_SHARE_PERCENT_KEY: None,
            TOTAL_REVIEWS_KEY: 0,
            UNIQUE_REVIEWERS_KEY: 0,
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
            TOP_REVIEWER_SHARE_PERCENT_KEY: None,
            TOP_THREE_REVIEWERS_SHARE_PERCENT_KEY: None,
            TOTAL_REVIEWS_KEY: 0,
            UNIQUE_REVIEWERS_KEY: 0,
        }

    sorted_reviewers = sorted(reviewer_counts.values(), reverse=True)

    top_reviewer_share = (sorted_reviewers[0] / total_reviewers) * 100
    top_3_sum = sum(sorted_reviewers[:3])
    top_3_share = (top_3_sum / total_reviewers) * 100

    return {
        TOP_REVIEWER_SHARE_PERCENT_KEY: round(top_reviewer_share, 2),
        TOP_THREE_REVIEWERS_SHARE_PERCENT_KEY: round(top_3_share, 2),
        TOTAL_REVIEWS_KEY: total_reviewers,
        UNIQUE_REVIEWERS_KEY: len(reviewer_counts),
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
        merged_at = _parse_datetime(merged_at_str)
        if merged_at is None:
            continue
        if (now_utc - merged_at).days <= LAST_N_DAYS:
            merged_prs.append(pr)

    reviews: Dict[int, List[Dict]] = {}
    for pr in merged_prs:
        pr_number = int(pr.get("number", 0))
        try:
            reviews[pr_number] = client.get_pull_request_reviews(
                owner, repository, pr_number
            )
            for review in reviews[pr_number]:
                if "created_at" not in review or review["created_at"] is None:
                    review["created_at"] = pr.get("created_at")
        except RuntimeError as e:
            logger.warning(f"Failed to fetch reviews for PR #{pr_number}: {e}")

    duration = audit_pr_duration(merged_prs)
    review_cycle = audit_pr_review_cycle(reviews)
    lead_time = audit_lead_time_for_change(merged_prs)
    balance = audit_reviewer_load_balance(reviews)

    # Combine metrics
    return (
        {MERGED_PRS_LAST_30_DAYS_KEY: len(merged_prs)}
        | duration
        | review_cycle
        | lead_time
        | balance
    )
