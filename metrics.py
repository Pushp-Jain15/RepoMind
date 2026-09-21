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
        "average_churn_per_file": round(average_churn, 2),

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


def calculate_repository_metrics(
    repository,
    contributors,
    commits,
    file_analysis
):
    """
    Calculate high-level repository metrics.
    """

    file_metrics = calculate_file_metrics(file_analysis)

    contributor_count = len(contributors) if contributors else 0
    commit_count = len(commits) if commits else 0

    open_issues = repository.get("open_issues_count", 0)

    return {
        "contributors": contributor_count,
        "commits_analyzed": commit_count,
        "open_issues": open_issues,
        "file_metrics": file_metrics
    }