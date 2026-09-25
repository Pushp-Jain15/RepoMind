def calculate_file_metrics(file_analysis):
    """
    Calculate overall metrics from file-level Git history.
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

        total_changes += stats.get(
            "changes",
            0
        )

        total_additions += stats.get(
            "additions",
            0
        )

        total_deletions += stats.get(
            "deletions",
            0
        )

        total_churn += stats.get(
            "churn",
            0
        )


    total_files = len(
        file_analysis
    )


    average_churn = (

        total_churn / total_files

        if total_files > 0

        else 0
    )


    top_changed_files = sorted(

        file_analysis.items(),

        key=lambda item:
        item[1].get(
            "changes",
            0
        ),

        reverse=True

    )[:10]


    top_churn_files = sorted(

        file_analysis.items(),

        key=lambda item:
        item[1].get(
            "churn",
            0
        ),

        reverse=True

    )[:10]


    return {

        "total_files_analyzed":
            total_files,

        "total_changes":
            total_changes,

        "total_additions":
            total_additions,

        "total_deletions":
            total_deletions,

        "total_churn":
            total_churn,

        "average_churn_per_file":
            round(
                average_churn,
                2
            ),

        "top_changed_files": [

            {
                "file": filename,

                "changes": stats.get(
                    "changes",
                    0
                )
            }

            for filename, stats
            in top_changed_files
        ],

        "top_churn_files": [

            {
                "file": filename,

                "churn": stats.get(
                    "churn",
                    0
                ),

                "additions": stats.get(
                    "additions",
                    0
                ),

                "deletions": stats.get(
                    "deletions",
                    0
                )
            }

            for filename, stats
            in top_churn_files
        ]
    }


def calculate_repository_metrics(
    repository,
    contributors,
    commits,
    file_analysis
):
    """
    Calculate repository-level software metrics.
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

        "contributors":
            contributor_count,

        "commits_analyzed":
            commit_count,

        "open_issues":
            open_issues,

        "file_metrics":
            file_metrics
    }


def calculate_health_indicators(
    repository_metrics
):
    """
    Calculate rule-based repository
    activity indicators.

    These are heuristic indicators,
    not ML predictions.
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


    # Commit activity

    if commits >= 200:

        commit_activity = "HIGH"

    elif commits >= 50:

        commit_activity = "MEDIUM"

    else:

        commit_activity = "LOW"


    # Code churn

    if total_churn >= 10000:

        churn_activity = "HIGH"

    elif total_churn >= 3000:

        churn_activity = "MEDIUM"

    else:

        churn_activity = "LOW"


    # Contributor activity

    if contributors >= 20:

        contributor_activity = "HIGH"

    elif contributors >= 5:

        contributor_activity = "MEDIUM"

    else:

        contributor_activity = "LOW"


    # Issue activity

    if open_issues >= 100:

        issue_activity = "HIGH"

    elif open_issues >= 20:

        issue_activity = "MEDIUM"

    else:

        issue_activity = "LOW"


    # Change activity

    if total_changes >= 100:

        change_activity = "HIGH"

    elif total_changes >= 30:

        change_activity = "MEDIUM"

    else:

        change_activity = "LOW"


    return {

        "commit_activity":
            commit_activity,

        "code_churn":
            churn_activity,

        "contributor_activity":
            contributor_activity,

        "issue_activity":
            issue_activity,

        "change_activity":
            change_activity
    }


def calculate_health_score(
    health_indicators
):
    """
    Calculate a preliminary repository
    health score using rule-based penalties.

    This is NOT an ML prediction.
    """

    score = 100


    # Commit activity

    if health_indicators.get(
        "commit_activity"
    ) == "HIGH":

        score -= 10

    elif health_indicators.get(
        "commit_activity"
    ) == "MEDIUM":

        score -= 5


    # Code churn

    if health_indicators.get(
        "code_churn"
    ) == "HIGH":

        score -= 20

    elif health_indicators.get(
        "code_churn"
    ) == "MEDIUM":

        score -= 10


    # Contributor activity

    if health_indicators.get(
        "contributor_activity"
    ) == "HIGH":

        score -= 5

    elif health_indicators.get(
        "contributor_activity"
    ) == "MEDIUM":

        score -= 2


    # Issue activity

    if health_indicators.get(
        "issue_activity"
    ) == "HIGH":

        score -= 20

    elif health_indicators.get(
        "issue_activity"
    ) == "MEDIUM":

        score -= 10


    # Change activity

    if health_indicators.get(
        "change_activity"
    ) == "HIGH":

        score -= 15

    elif health_indicators.get(
        "change_activity"
    ) == "MEDIUM":

        score -= 7


    # Keep between 0 and 100

    score = max(
        0,
        min(
            100,
            score
        )
    )


    # Category

    if score >= 80:

        category = "HEALTHY"

    elif score >= 60:

        category = "MODERATE"

    else:

        category = "AT_RISK"


    return {

        "score": score,

        "category": category
    }


def calculate_file_risk_indicators(
    file_analysis
):
    """
    Identify potentially risky files using:

    - change frequency
    - code churn
    - contributor count

    This is a rule-based baseline.

    It is NOT an ML prediction.
    """

    if not file_analysis:

        return []


    risk_files = []


    for filename, stats in file_analysis.items():

        changes = stats.get(
            "changes",
            0
        )


        additions = stats.get(
            "additions",
            0
        )


        deletions = stats.get(
            "deletions",
            0
        )


        churn = stats.get(
            "churn",
            additions + deletions
        )


        contributors = stats.get(
            "contributors",
            []
        )


        contributor_count = stats.get(
            "contributor_count",
            len(contributors)
        )


        risk_points = 0


        reasons = []


        # -----------------------------------
        # Change frequency
        # -----------------------------------

        if changes >= 20:

            risk_points += 2

            reasons.append(
                "Frequently modified"
            )

        elif changes >= 10:

            risk_points += 1

            reasons.append(
                "Regularly modified"
            )


        # -----------------------------------
        # Code churn
        # -----------------------------------

        if churn >= 1000:

            risk_points += 3

            reasons.append(
                "Very high code churn"
            )

        elif churn >= 500:

            risk_points += 2

            reasons.append(
                "High code churn"
            )

        elif churn >= 200:

            risk_points += 1

            reasons.append(
                "Moderate code churn"
            )


        # -----------------------------------
        # Contributor count
        # -----------------------------------

        if contributor_count >= 5:

            risk_points += 2

            reasons.append(
                "Modified by many contributors"
            )

        elif contributor_count >= 3:

            risk_points += 1

            reasons.append(
                "Modified by multiple contributors"
            )


        # -----------------------------------
        # Maximum score
        # -----------------------------------

        # Change frequency = 2
        # Code churn = 3
        # Contributors = 2
        #
        # Maximum = 7

        risk_score = round(
            (risk_points / 7) * 100
        )


        # -----------------------------------
        # Risk level
        # -----------------------------------

        if risk_points >= 5:

            risk_level = "HIGH"

        elif risk_points >= 2:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"


        # -----------------------------------
        # Store risky files
        # -----------------------------------

        if risk_points > 0:

            risk_files.append({

                "file": filename,

                "changes": changes,

                "additions": additions,

                "deletions": deletions,

                "churn": churn,

                "contributor_count":
                    contributor_count,

                "contributors":
                    contributors,

                "risk_points":
                    risk_points,

                "risk_score":
                    risk_score,

                "risk_level":
                    risk_level,

                "reasons":
                    reasons

            })


    # -----------------------------------
    # Sort by risk
    # -----------------------------------

    risk_files.sort(

        key=lambda item: (

            item["risk_score"],

            item["churn"]

        ),

        reverse=True
    )


    return risk_files[:20]


def calculate_risk_summary(
    file_risk
):
    """
    Calculate a summary of file-level
    risk levels.
    """

    high_risk_files = 0

    medium_risk_files = 0

    low_risk_files = 0


    for file in file_risk:

        risk_level = file.get(
            "risk_level",
            "LOW"
        )


        if risk_level == "HIGH":

            high_risk_files += 1

        elif risk_level == "MEDIUM":

            medium_risk_files += 1

        else:

            low_risk_files += 1


    total_risky_files = (

        high_risk_files

        + medium_risk_files

        + low_risk_files
    )


    return {

        "total_risky_files":
            total_risky_files,

        "high_risk_files":
            high_risk_files,

        "medium_risk_files":
            medium_risk_files,

        "low_risk_files":
            low_risk_files
    }