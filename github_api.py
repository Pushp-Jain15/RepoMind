import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# ============================================================
# GITHUB API HEADERS
# ============================================================

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


print("GitHub token loaded:", bool(GITHUB_TOKEN))


# ============================================================
# HELPER FUNCTION
# ============================================================

def github_get(url, params=None):
    """
    Send an authenticated GET request to GitHub API.
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
            print("GitHub API returned 403.")
            print("Response:", response.text[:300])
            return None

        if response.status_code == 404:
            print("GitHub resource not found:", url)
            return None

        print(
            f"GitHub API error: {response.status_code} "
            f"for {url}"
        )

        return None

    except requests.RequestException as error:
        print("GitHub request failed:", error)
        return None


# ============================================================
# REPOSITORY
# ============================================================

def get_repository(owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}"

    return github_get(url)


# ============================================================
# LANGUAGES
# ============================================================

def get_languages(owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}/languages"

    return github_get(url)


# ============================================================
# CONTRIBUTORS
# ============================================================

def get_contributors(owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"

    params = {
        "per_page": 100
    }

    return github_get(url, params=params)


# ============================================================
# COMMITS
# ============================================================

def get_commits(owner, repo):

    all_commits = []

    page = 1

    while page <= 3:

        url = f"https://api.github.com/repos/{owner}/{repo}/commits"

        params = {
            "page": page,
            "per_page": 100
        }

        commits = github_get(url, params=params)

        if commits is None:
            break

        if not commits:
            break

        all_commits.extend(commits)

        page += 1

    return all_commits


# ============================================================
# ISSUES
# ============================================================

def get_issues(owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    params = {
        "state": "open",
        "per_page": 100
    }

    return github_get(url, params=params)


# ============================================================
# COMMIT DETAILS
# ============================================================

def get_commit_details(owner, repo, sha):

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/commits/{sha}"
    )

    return github_get(url)


# ============================================================
# FILE CHANGE ANALYSIS
# ============================================================

def analyze_file_changes(owner, repo, commits):

    file_stats = {}

    # Analyze latest 30 commits
    for commit in commits[:30]:

        sha = commit.get("sha")

        if not sha:
            continue

        details = get_commit_details(
            owner,
            repo,
            sha
        )

        if not details:
            continue

        files = details.get("files", [])

        for file in files:

            filename = file.get("filename")

            if not filename:
                continue

            if filename not in file_stats:

                file_stats[filename] = {
                    "changes": 0,
                    "additions": 0,
                    "deletions": 0,
                    "churn": 0
                }

            additions = file.get("additions", 0)
            deletions = file.get("deletions", 0)

            file_stats[filename]["changes"] += 1

            file_stats[filename]["additions"] += additions

            file_stats[filename]["deletions"] += deletions

            file_stats[filename]["churn"] = (
                file_stats[filename]["additions"]
                +
                file_stats[filename]["deletions"]
            )

    return file_stats