# ============================================================
# FILE-LEVEL METRICS
# ============================================================

def calculate_file_metrics(file_analysis):
    """
    Calculate software metrics from file-level Git history.
    """

    if not file_analysis:
        return {
            "total_files_analyzed": 0,
            "total_changes": 0,
            "total_additions": 0,
            "total_deletions": 0,
            "total_churn": 0,
            "average_churn_per_file": 0,
            "top_changed_files": [],
            "top_churn_files": []
        }

    total_changes = 0
    total_additions = 0
    total_deletions = 0
    total_churn = 0

    for filename, stats in file_analysis.items():

        total_changes += stats.get("changes", 0)

        total_additions += stats.get("additions", 0)

        total_deletions += stats.get("deletions", 0)

        total_churn += stats.get("churn", 0)

    total_files = len(file_analysis)

    average_churn = total_churn / total_files

    top_changed_files = sorted(
        file_analysis.items(),
        key=lambda item: item[1].get("changes", 0),
        reverse=True
    )[:10]

    top_churn_files = sorted(
        file_analysis.items(),
        key=lambda item: item[1].get("churn", 0),
        reverse=True
    )[:10]

    return {
        "total_files_analyzed": total_files,

        "total_changes": total_changes,

        "total_additions": total_additions,

        "total_deletions": total_deletions,

        "total_churn": total_churn,

        "average_churn_per_file": round(
            average_churn,
            2
        ),

        "top_changed_files": [
            {
                "file": filename,
                "changes": stats.get("changes", 0)
            }

            for filename, stats in top_changed_files
        ],

        "top_churn_files": [
            {
                "file": filename,
                "churn": stats.get("churn", 0),
                "additions": stats.get("additions", 0),
                "deletions": stats.get("deletions", 0)
            }

            for filename, stats in top_churn_files
        ]
    }


# ============================================================
# REPOSITORY METRICS
# ============================================================

def calculate_repository_metrics(
    repository,
    contributors,
    commits,
    file_analysis
):
    """
    Calculate high-level repository metrics.
    """

    file_metrics = calculate_file_metrics(
        file_analysis
    )

    contributor_count = (
        len(contributors)
        if contributors
        else 0
    )

    commit_count = (
        len(commits)
        if commits
        else 0
    )

    open_issues = repository.get(
        "open_issues_count",
        0
    )

    return {
        "contributors": contributor_count,

        "commits_analyzed": commit_count,

        "open_issues": open_issues,

        "file_metrics": file_metrics
    }


# ============================================================
# HEALTH INDICATORS
# ============================================================

def calculate_health_indicators(
    repository_metrics
):
    """
    Convert raw repository metrics into
    simple software health indicators.

    These indicators are currently
    rule-based and will later be improved
    using statistical and ML-based methods.
    """

    file_metrics = repository_metrics.get(
        "file_metrics",
        {}
    )

    total_churn = file_metrics.get(
        "total_churn",
        0
    )

    total_changes = file_metrics.get(
        "total_changes",
        0
    )

    contributors = repository_metrics.get(
        "contributors",
        0
    )

    commits = repository_metrics.get(
        "commits_analyzed",
        0
    )

    open_issues = repository_metrics.get(
        "open_issues",
        0
    )


    # --------------------------------------------------------
    # Commit Activity
    # --------------------------------------------------------

    if commits >= 200:
        commit_activity = "HIGH"

    elif commits >= 50:
        commit_activity = "MEDIUM"

    else:
        commit_activity = "LOW"


    # --------------------------------------------------------
    # Code Churn
    # --------------------------------------------------------

    if total_churn >= 10000:
        churn_activity = "HIGH"

    elif total_churn >= 3000:
        churn_activity = "MEDIUM"

    else:
        churn_activity = "LOW"


    # --------------------------------------------------------
    # Contributor Activity
    # --------------------------------------------------------

    if contributors >= 20:
        contributor_activity = "HIGH"

    elif contributors >= 5:
        contributor_activity = "MEDIUM"

    else:
        contributor_activity = "LOW"


    # --------------------------------------------------------
    # Issue Activity
    # --------------------------------------------------------

    if open_issues >= 100:
        issue_activity = "HIGH"

    elif open_issues >= 20:
        issue_activity = "MEDIUM"

    else:
        issue_activity = "LOW"


    # --------------------------------------------------------
    # Change Activity
    # --------------------------------------------------------

    if total_changes >= 100:
        change_activity = "HIGH"

    elif total_changes >= 30:
        change_activity = "MEDIUM"

    else:
        change_activity = "LOW"


    return {
        "commit_activity": commit_activity,

        "code_churn": churn_activity,

        "contributor_activity": contributor_activity,

        "issue_activity": issue_activity,

        "change_activity": change_activity
    }