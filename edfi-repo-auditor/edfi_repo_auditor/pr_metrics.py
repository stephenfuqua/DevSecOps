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
from datetime import datetime
from typing import Dict, List, Optional

from edfi_repo_auditor.github_client import GitHubClient


logger: logging.Logger = logging.getLogger(__name__)


def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse an ISO 8601 datetime string to datetime object."""
    if dt_str is None:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def audit_pr_duration(
    client: GitHubClient, owner: str, repository: str
) -> Dict[str, object]:
    """
    Compute average PR duration for merged PRs only.

    Duration is calculated as (closed_at - created_at) for PRs with merged_at != None.
    No date filters are applied - all available merged PRs are included.

    Args:
        client: GitHubClient instance
        owner: Repository owner
        repository: Repository name

    Returns:
        Dictionary with:
        - avg_pr_duration_days: Average duration in days (float or None if no merged PRs)
        - merged_pr_count: Number of merged PRs
    """
    prs = client.get_pull_requests(owner, repository, state="closed")
    logger.info(f"Retrieved {len(prs)} closed PRs for {owner}/{repository}")

    merged_prs = [pr for pr in prs if pr.get("merged_at") is not None]
    logger.info(f"Found {len(merged_prs)} merged PRs for {owner}/{repository}")

    if not merged_prs:
        return {
            "avg_pr_duration_days": None,
            "merged_pr_count": 0,
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
        "avg_pr_duration_days": round(avg_duration, 2),
        "merged_pr_count": len(merged_prs),
    }


def audit_lead_time_for_change(
    client: GitHubClient, owner: str, repository: str
) -> Dict[str, object]:
    """
    Compute average lead time for change (time from PR creation to merge).

    Lead time is calculated as (merged_at - created_at) for merged PRs only.
    This is a proxy metric for the time from code being written to deployment.

    Args:
        client: GitHubClient instance
        owner: Repository owner
        repository: Repository name

    Returns:
        Dictionary with:
        - avg_lead_time_days: Average lead time in days (float or None if no merged PRs)
        - merged_pr_count: Number of merged PRs
    """
    prs = client.get_pull_requests(owner, repository, state="closed")
    merged_prs = [pr for pr in prs if pr.get("merged_at") is not None]

    if not merged_prs:
        return {
            "avg_lead_time_days": None,
            "merged_pr_count": 0,
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
            "avg_lead_time_days": None,
            "merged_pr_count": len(merged_prs),
        }

    avg_lead_time = sum(lead_times) / len(lead_times)

    return {
        "avg_lead_time_days": round(avg_lead_time, 2),
        "merged_pr_count": len(merged_prs),
    }


def _fetch_pr_details(
    client: GitHubClient, owner: str, repository: str, prs: List[dict]
) -> List[dict]:
    """
    Fetch detailed information for a list of PRs (including additions, deletions).

    The list endpoint doesn't include additions/deletions,
    so we need to fetch details for each PR.
    """
    detailed_prs = []
    for pr in prs:
        try:
            detail = client.get_pull_request_detail(owner, repository, pr["number"])
            detailed_prs.append({**pr, **detail})
        except RuntimeError as e:
            logger.warning(f"Failed to fetch details for PR #{pr['number']}: {e}")
            detailed_prs.append(pr)
    return detailed_prs


def audit_pr_size_indicators(
    client: GitHubClient, owner: str, repository: str
) -> Dict[str, object]:
    """
    Compute PR size indicators (additions, deletions, changed files).

    Args:
        client: GitHubClient instance
        owner: Repository owner
        repository: Repository name

    Returns:
        Dictionary with:
        - median_additions: Median number of additions
        - median_deletions: Median number of deletions
        - median_changed_files: Median number of changed files
        - avg_additions: Average number of additions
        - avg_deletions: Average number of deletions
        - avg_changed_files: Average number of changed files
        - merged_pr_count: Number of merged PRs analyzed
    """
    prs = client.get_pull_requests(owner, repository, state="closed")
    merged_prs = [pr for pr in prs if pr.get("merged_at") is not None]

    if not merged_prs:
        return {
            "median_additions": None,
            "median_deletions": None,
            "median_changed_files": None,
            "avg_additions": None,
            "avg_deletions": None,
            "avg_changed_files": None,
            "merged_pr_count": 0,
        }

    # Fetch detailed info if needed
    detailed_prs = _fetch_pr_details(client, owner, repository, merged_prs)

    additions: List[int] = []
    deletions: List[int] = []
    changed_files: List[int] = []

    for pr in detailed_prs:
        if pr.get("additions") is not None:
            additions.append(int(pr["additions"]))
        if pr.get("deletions") is not None:
            deletions.append(int(pr["deletions"]))
        if pr.get("changed_files") is not None:
            changed_files.append(int(pr["changed_files"]))

    def _median(values: List[int]) -> Optional[float]:
        if not values:
            return None
        sorted_values = sorted(values)
        n = len(sorted_values)
        mid = n // 2
        if n % 2 == 0:
            return round((sorted_values[mid - 1] + sorted_values[mid]) / 2, 2)
        return round(float(sorted_values[mid]), 2)

    def _average_int(values: List[int]) -> Optional[float]:
        if not values:
            return None
        return round(sum(values) / len(values), 2)

    return {
        "median_additions": _median(additions),
        "median_deletions": _median(deletions),
        "median_changed_files": _median(changed_files),
        "avg_additions": _average_int(additions),
        "avg_deletions": _average_int(deletions),
        "avg_changed_files": _average_int(changed_files),
        "merged_pr_count": len(merged_prs),
    }


def audit_pr_review_cycle(
    client: GitHubClient, owner: str, repository: str
) -> Dict[str, object]:
    """
    Compute PR review cycle metrics.

    Args:
        client: GitHubClient instance
        owner: Repository owner
        repository: Repository name

    Returns:
        Dictionary with:
        - avg_time_to_first_approval_hours: Average time from PR open to first approval
        - avg_reviews_per_pr: Average number of reviews per PR
        - avg_approvals_per_pr: Average number of approvals per PR
        - merged_pr_count: Number of merged PRs analyzed
    """
    prs = client.get_pull_requests(owner, repository, state="closed")
    merged_prs = [pr for pr in prs if pr.get("merged_at") is not None]

    if not merged_prs:
        return {
            "avg_time_to_first_approval_hours": None,
            "avg_reviews_per_pr": None,
            "avg_approvals_per_pr": None,
            "merged_pr_count": 0,
        }

    times_to_first_approval: List[float] = []
    all_reviews_count: List[float] = []
    all_approvals_count: List[float] = []

    for pr in merged_prs:
        try:
            reviews = client.get_pull_request_reviews(owner, repository, pr["number"])
            all_reviews_count.append(float(len(reviews)))

            approvals = [r for r in reviews if r.get("state") == "APPROVED"]
            all_approvals_count.append(float(len(approvals)))

            if approvals:
                created_at = _parse_datetime(pr.get("created_at"))
                approval_times: List[datetime] = []
                for a in approvals:
                    submitted = a.get("submitted_at")
                    if submitted:
                        parsed = _parse_datetime(submitted)
                        if parsed:
                            approval_times.append(parsed)
                first_approval_time = min(approval_times) if approval_times else None
                if created_at and first_approval_time:
                    hours = (first_approval_time - created_at).total_seconds() / 3600
                    times_to_first_approval.append(hours)
        except RuntimeError as e:
            logger.warning(f"Failed to fetch reviews for PR #{pr['number']}: {e}")

    def _average(values: List[float]) -> Optional[float]:
        if not values:
            return None
        return round(sum(values) / len(values), 2)

    return {
        "avg_time_to_first_approval_hours": _average(times_to_first_approval),
        "avg_reviews_per_pr": _average(all_reviews_count),
        "avg_approvals_per_pr": _average(all_approvals_count),
        "merged_pr_count": len(merged_prs),
    }


def audit_reviewer_load_balance(
    client: GitHubClient, owner: str, repository: str
) -> Dict[str, object]:
    """
    Compute reviewer load balance metrics.

    Args:
        client: GitHubClient instance
        owner: Repository owner
        repository: Repository name

    Returns:
        Dictionary with:
        - top_reviewer_share_percent: Percentage of reviews done by top reviewer
        - top_3_reviewers_share_percent: Percentage of reviews done by top 3 reviewers
        - total_reviews: Total number of reviews
        - unique_reviewers: Number of unique reviewers
    """
    prs = client.get_pull_requests(owner, repository, state="closed")
    merged_prs = [pr for pr in prs if pr.get("merged_at") is not None]

    if not merged_prs:
        return {
            "top_reviewer_share_percent": None,
            "top_3_reviewers_share_percent": None,
            "total_reviews": 0,
            "unique_reviewers": 0,
        }

    reviewer_counts: Dict[str, int] = {}

    for pr in merged_prs:
        try:
            reviews = client.get_pull_request_reviews(owner, repository, pr["number"])
            for review in reviews:
                reviewer = review.get("user")
                if reviewer:
                    reviewer_counts[reviewer] = reviewer_counts.get(reviewer, 0) + 1
        except RuntimeError as e:
            logger.warning(f"Failed to fetch reviews for PR #{pr['number']}: {e}")

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


def audit_time_to_first_response(
    client: GitHubClient, owner: str, repository: str
) -> Dict[str, object]:
    """
    Compute time-to-first-response metrics.

    First response is the first comment or review from someone other than the author.

    Args:
        client: GitHubClient instance
        owner: Repository owner
        repository: Repository name

    Returns:
        Dictionary with:
        - avg_time_to_first_response_hours: Average hours from PR open to first response
        - merged_pr_count: Number of merged PRs analyzed
    """
    prs = client.get_pull_requests(owner, repository, state="closed")
    merged_prs = [pr for pr in prs if pr.get("merged_at") is not None]

    if not merged_prs:
        return {
            "avg_time_to_first_response_hours": None,
            "merged_pr_count": 0,
        }

    response_times = []

    for pr in merged_prs:
        pr_author = pr.get("user")
        created_at = _parse_datetime(pr.get("created_at"))
        if not created_at:
            continue

        first_response_time = None

        try:
            reviews = client.get_pull_request_reviews(owner, repository, pr["number"])
            for review in reviews:
                if review.get("user") != pr_author:
                    review_time = _parse_datetime(review.get("submitted_at"))
                    if review_time:
                        if (
                            first_response_time is None
                            or review_time < first_response_time
                        ):
                            first_response_time = review_time
        except RuntimeError as e:
            logger.warning(f"Failed to fetch reviews for PR #{pr['number']}: {e}")

        try:
            comments = client.get_pull_request_comments(owner, repository, pr["number"])
            for comment in comments:
                if comment.get("user") != pr_author:
                    comment_time = _parse_datetime(comment.get("created_at"))
                    if comment_time:
                        if (
                            first_response_time is None
                            or comment_time < first_response_time
                        ):
                            first_response_time = comment_time
        except RuntimeError as e:
            logger.warning(f"Failed to fetch comments for PR #{pr['number']}: {e}")

        if first_response_time:
            hours = (first_response_time - created_at).total_seconds() / 3600
            response_times.append(hours)

    if not response_times:
        return {
            "avg_time_to_first_response_hours": None,
            "merged_pr_count": len(merged_prs),
        }

    avg_response_time = sum(response_times) / len(response_times)

    return {
        "avg_time_to_first_response_hours": round(avg_response_time, 2),
        "merged_pr_count": len(merged_prs),
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

    duration = audit_pr_duration(client, owner, repository)
    lead_time = audit_lead_time_for_change(client, owner, repository)
    first_response = audit_time_to_first_response(client, owner, repository)
    balance = audit_reviewer_load_balance(client, owner, repository)

    # Combine metrics, avoiding duplicate merged_pr_count
    metrics = {
        "avg_pr_duration_days": duration.get("avg_pr_duration_days"),
        "avg_lead_time_days": lead_time.get("avg_lead_time_days"),
        "merged_pr_count": duration.get("merged_pr_count", 0),
        "first_response": first_response.get("avg_time_to_first_response_hours"),
        "top_reviewer_share_percent": balance.get("top_reviewer_share_percent"),
        "top_3_reviewers_share_percent": balance.get("top_3_reviewers_share_percent"),
        "total_reviewers": balance.get("total_reviewers"),
        "unique_reviewers": balance.get("unique_reviewers")
    }

    return metrics
