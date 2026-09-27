import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# ---------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# ---------------------------------------------------------
# GitHub API headers
# ---------------------------------------------------------

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


print("GitHub token loaded:", bool(GITHUB_TOKEN))


# ---------------------------------------------------------
# Generic GitHub GET request
# ---------------------------------------------------------

def github_get(url, params=None):
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
            f"GitHub API error: "
            f"{response.status_code} for {url}"
        )

        return None

    except requests.RequestException as error:
        print("GitHub request failed:", error)
        return None


# ---------------------------------------------------------
# Repository information
# ---------------------------------------------------------

def get_repository(owner, repo):
    return github_get(
        f"https://api.github.com/repos/{owner}/{repo}"
    )


# ---------------------------------------------------------
# Repository languages
# ---------------------------------------------------------

def get_languages(owner, repo):
    return github_get(
        f"https://api.github.com/repos/{owner}/{repo}/languages"
    )


# ---------------------------------------------------------
# Repository contributors
# ---------------------------------------------------------

def get_contributors(owner, repo):
    return github_get(
        f"https://api.github.com/repos/{owner}/{repo}/contributors",
        params={"per_page": 100}
    )


# ---------------------------------------------------------
# Repository commits
# ---------------------------------------------------------

def get_commits(owner, repo):
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

        all_commits.extend(commits)

        page += 1

    return all_commits


# ---------------------------------------------------------
# Repository issues and pull requests
# ---------------------------------------------------------

def get_issues(owner, repo):
    """
    Get open GitHub issues.

    GitHub's issues endpoint can also
    return pull requests.
    """

    items = github_get(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
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

        if "pull_request" in item:
            pull_requests.append(item)

        else:
            actual_issues.append(item)

    return {
        "issues": actual_issues,
        "pull_requests": pull_requests
    }


# ---------------------------------------------------------
# Commit details
# ---------------------------------------------------------

def get_commit_details(owner, repo, sha):
    return github_get(
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/commits/{sha}"
    )


# ---------------------------------------------------------
# File change analysis
# ---------------------------------------------------------

def analyze_file_changes(owner, repo, commits):
    """
    Analyze file-level changes from recent Git commits.

    Tracks:
    - number of changes
    - additions
    - deletions
    - churn
    - contributors
    """

    file_stats = {}

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

        # Try GitHub username first
        author_login = None

        author_data = details.get("author")

        if author_data:
            author_login = author_data.get("login")

        # Fall back to commit author name
        if not author_login:

            commit_author = (
                details
                .get("commit", {})
                .get("author", {})
                .get("name")
            )

            author_login = commit_author

        for file in files:

            filename = file.get("filename")

            if not filename:
                continue

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

            file_stats[filename]["changes"] += 1

            file_stats[filename]["additions"] += additions

            file_stats[filename]["deletions"] += deletions

            file_stats[filename]["churn"] = (
                file_stats[filename]["additions"]
                + file_stats[filename]["deletions"]
            )

            if author_login:

                file_stats[filename][
                    "contributors"
                ].add(author_login)

    # Convert sets to JSON-friendly lists
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


# ---------------------------------------------------------
# Repository file tree
# ---------------------------------------------------------

def get_repository_tree(owner, repo, branch):
    """
    Get the complete file tree of a GitHub repository.

    GitHub returns both files and directories.
    We keep only files.
    """

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/git/trees/{branch}"
    )

    tree_data = github_get(
        url,
        params={"recursive": "1"}
    )

    if not tree_data:
        return []

    tree = tree_data.get(
        "tree",
        []
    )

    files = []

    for item in tree:

        if item.get("type") == "blob":

            path = item.get("path")

            if path:
                files.append(path)

    return files


# ---------------------------------------------------------
# Source-code file detection
# ---------------------------------------------------------

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".kts",
    ".scala",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".sql",
    ".r",
    ".R",
    ".vue"
}


IGNORED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".mp4",
    ".mp3",
    ".wav",
    ".zip",
    ".rar",
    ".7z",
    ".exe",
    ".dll",
    ".so",
    ".pdf"
}


IGNORED_FILENAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "composer.lock",
    "poetry.lock",
    "pipfile.lock"
}


# ---------------------------------------------------------
# Filter source-code files
# ---------------------------------------------------------

def filter_source_files(files):
    """
    Keep source-code files and remove
    binaries, images, lock files, etc.
    """

    source_files = []

    for file_path in files:

        filename = Path(file_path).name

        if filename in IGNORED_FILENAMES:
            continue

        extension = Path(file_path).suffix.lower()

        if extension in IGNORED_EXTENSIONS:
            continue

        if extension in SOURCE_EXTENSIONS:
            source_files.append(file_path)

    return sorted(source_files)


# ---------------------------------------------------------
# Analyze repository file structure
# ---------------------------------------------------------

def analyze_repository_files(owner, repo, branch):
    """
    Fetch and analyze repository file structure.

    Returns:
    - total files
    - source files
    - source file count
    - file extension distribution
    """

    all_files = get_repository_tree(
        owner,
        repo,
        branch
    )

    source_files = filter_source_files(
        all_files
    )

    extension_counts = {}

    for file_path in source_files:

        extension = (
            Path(file_path)
            .suffix
            .lower()
        )

        if not extension:
            continue

        extension_counts[extension] = (
            extension_counts.get(
                extension,
                0
            ) + 1
        )

    return {
        "total_files": len(all_files),

        "source_files": source_files,

        "source_file_count": len(
            source_files
        ),

        "extension_counts": dict(
            sorted(
                extension_counts.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )
    }