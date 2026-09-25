import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# -----------------------------------
# Environment configuration
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(
    BASE_DIR / ".env"
)

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN"
)


# -----------------------------------
# GitHub API headers
# -----------------------------------

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}


if GITHUB_TOKEN:

    HEADERS["Authorization"] = (
        f"Bearer {GITHUB_TOKEN}"
    )


print(
    "GitHub token loaded:",
    bool(GITHUB_TOKEN)
)


# -----------------------------------
# Generic GitHub GET request
# -----------------------------------

def github_get(
    url,
    params=None
):
    """
    Send a GET request to the GitHub API.
    """

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=30
        )

        if response.status_code == 200:

            return response.json()

        if response.status_code == 403:

            print(
                "GitHub API returned 403."
            )

            print(
                "Response:",
                response.text[:300]
            )

            return None

        if response.status_code == 404:

            print(
                "GitHub resource not found:",
                url
            )

            return None

        print(
            f"GitHub API error: "
            f"{response.status_code} "
            f"for {url}"
        )

        return None

    except requests.RequestException as error:

        print(
            "GitHub request failed:",
            error
        )

        return None


# -----------------------------------
# Repository information
# -----------------------------------

def get_repository(
    owner,
    repo
):

    return github_get(
        f"https://api.github.com/repos/"
        f"{owner}/{repo}"
    )


# -----------------------------------
# Repository languages
# -----------------------------------

def get_languages(
    owner,
    repo
):

    return github_get(
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/languages"
    )


# -----------------------------------
# Repository contributors
# -----------------------------------

def get_contributors(
    owner,
    repo
):

    return github_get(

        f"https://api.github.com/repos/"
        f"{owner}/{repo}/contributors",

        params={
            "per_page": 100
        }
    )


# -----------------------------------
# Repository commits
# -----------------------------------

def get_commits(
    owner,
    repo
):

    all_commits = []

    page = 1

    while page <= 3:

        url = (
            f"https://api.github.com/repos/"
            f"{owner}/{repo}/commits"
        )

        commits = github_get(

            url,

            params={
                "page": page,
                "per_page": 100
            }
        )

        if commits is None:

            break

        if not commits:

            break

        all_commits.extend(
            commits
        )

        page += 1

    return all_commits


# -----------------------------------
# Repository issues
# -----------------------------------

def get_issues(
    owner,
    repo
):
    """
    Get open GitHub issues.

    GitHub's issues endpoint can also
    return pull requests.

    This function separates actual
    issues from pull requests.
    """

    items = github_get(

        f"https://api.github.com/repos/"
        f"{owner}/{repo}/issues",

        params={
            "state": "open",
            "per_page": 100
        }
    )


    if items is None:

        return {
            "issues": [],
            "pull_requests": []
        }


    actual_issues = []

    pull_requests = []


    for item in items:

        # Pull requests contain
        # a "pull_request" field.

        if "pull_request" in item:

            pull_requests.append(
                item
            )

        else:

            actual_issues.append(
                item
            )


    return {
        "issues": actual_issues,
        "pull_requests": pull_requests
    }


# -----------------------------------
# Commit details
# -----------------------------------

def get_commit_details(
    owner,
    repo,
    sha
):

    return github_get(

        f"https://api.github.com/repos/"
        f"{owner}/{repo}/commits/{sha}"
    )


# -----------------------------------
# Analyze changed files
# -----------------------------------

def analyze_file_changes(
    owner,
    repo,
    commits
):
    """
    Analyze file-level changes from
    recent Git commits.

    Tracks:

    - number of changes
    - additions
    - deletions
    - churn
    - contributors
    """

    file_stats = {}


    # Analyze latest 30 commits

    for commit in commits[:30]:

        sha = commit.get(
            "sha"
        )

        if not sha:

            continue


        details = get_commit_details(
            owner,
            repo,
            sha
        )

        if not details:

            continue


        files = details.get(
            "files",
            []
        )


        # -----------------------------------
        # Identify commit contributor
        # -----------------------------------

        author_login = None

        author_data = details.get(
            "author"
        )


        if author_data:

            author_login = author_data.get(
                "login"
            )


        # GitHub author may sometimes
        # be unavailable.

        if not author_login:

            commit_author = (
                details
                .get("commit", {})
                .get("author", {})
                .get("name")
            )

            author_login = commit_author


        # -----------------------------------
        # Process every changed file
        # -----------------------------------

        for file in files:

            filename = file.get(
                "filename"
            )


            if not filename:

                continue


            # -----------------------------------
            # Initialize file
            # -----------------------------------

            if filename not in file_stats:

                file_stats[filename] = {

                    "changes": 0,

                    "additions": 0,

                    "deletions": 0,

                    "churn": 0,

                    "contributors": set()
                }


            additions = file.get(
                "additions",
                0
            )

            deletions = file.get(
                "deletions",
                0
            )


            file_stats[filename][
                "changes"
            ] += 1


            file_stats[filename][
                "additions"
            ] += additions


            file_stats[filename][
                "deletions"
            ] += deletions


            file_stats[filename][
                "churn"
            ] = (

                file_stats[filename][
                    "additions"
                ]

                +

                file_stats[filename][
                    "deletions"
                ]
            )


            # -----------------------------------
            # Track contributor
            # -----------------------------------

            if author_login:

                file_stats[filename][
                    "contributors"
                ].add(
                    author_login
                )


    # -----------------------------------
    # Convert sets to JSON-safe lists
    # -----------------------------------

    for filename, stats in file_stats.items():

        contributors = stats.get(
            "contributors",
            set()
        )


        stats["contributors"] = sorted(
            contributors
        )


        stats["contributor_count"] = len(
            contributors
        )


    return file_stats