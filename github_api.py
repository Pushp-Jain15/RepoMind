import requests


def get_repository(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    print("Error getting repository:", response.status_code)

    return None


def get_languages(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    print("Error getting languages:", response.status_code)

    return None


def get_contributors(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    print("Error getting contributors:", response.status_code)

    return None


def get_commits(owner, repo):
    all_commits = []

    page = 1

    while page <= 3:

        url = f"https://api.github.com/repos/{owner}/{repo}/commits"

        params = {
            "page": page,
            "per_page": 100
        }

        response = requests.get(
            url,
            params=params
        )

        if response.status_code != 200:
            print(
                "Error getting commits:",
                response.status_code
            )
            break

        commits = response.json()

        if not commits:
            break

        all_commits.extend(commits)

        page += 1

    return all_commits


def get_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    params = {
        "state": "open",
        "per_page": 100
    }

    response = requests.get(
        url,
        params=params
    )

    if response.status_code == 200:
        return response.json()

    print("Error getting issues:", response.status_code)

    return None


# --------------------------------------------------
# Get details of a specific commit
# --------------------------------------------------

def get_commit_details(owner, repo, commit_sha):

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/commits/{commit_sha}"
    )

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    print(
        "Error getting commit details:",
        response.status_code
    )

    return None


# --------------------------------------------------
# Analyze changed files
# --------------------------------------------------

def analyze_file_changes(owner, repo, commits):

    file_stats = {}

    # Analyze first 30 commits
    for commit in commits[:30]:

        sha = commit["sha"]

        details = get_commit_details(
            owner,
            repo,
            sha
        )

        if not details:
            continue

        files = details.get("files", [])

        for file in files:

            filename = file["filename"]

            if filename not in file_stats:

                file_stats[filename] = {
                    "changes": 0,
                    "additions": 0,
                    "deletions": 0
                }

            file_stats[filename]["changes"] += 1

            file_stats[filename]["additions"] += (
                file.get("additions", 0)
            )

            file_stats[filename]["deletions"] += (
                file.get("deletions", 0)
            )

    return file_stats