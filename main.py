# ==========================================
# IMPORTS
# ==========================================

from github_api import (
    get_repository,
    get_languages,
    get_contributors,
    get_commits,
    get_issues
)

from utils import extract_repo_info


# ==========================================
# START REPOMIND
# ==========================================

print("\n===================================")
print("            REPOMIND")
print("===================================")


# ==========================================
# GET GITHUB URL FROM USER
# ==========================================

github_url = input("\nEnter GitHub repository URL: ")


# ==========================================
# EXTRACT OWNER AND REPOSITORY
# ==========================================

try:

    owner, repo = extract_repo_info(github_url)

except ValueError:

    print("Invalid GitHub URL.")
    exit()


print("\nAnalyzing repository...")
print("Owner:", owner)
print("Repository:", repo)


# ==========================================
# COLLECT DATA FROM GITHUB
# ==========================================

data = get_repository(owner, repo)

languages = get_languages(owner, repo)

contributors = get_contributors(owner, repo)

commits = get_commits(owner, repo)

issues = get_issues(owner, repo)


# ==========================================
# DISPLAY REPOSITORY INFORMATION
# ==========================================

if data:

    print("\n===================================")
    print("       REPOSITORY INFORMATION")
    print("===================================")

    print("Name:", data["name"])

    print("Owner:", data["owner"]["login"])

    print("Description:", data["description"])

    print("Stars:", data["stargazers_count"])

    print("Forks:", data["forks_count"])

    print("Open Issues:", data["open_issues_count"])

    print("Created:", data["created_at"])

    print("Updated:", data["updated_at"])

    print("URL:", data["html_url"])


# ==========================================
# DISPLAY LANGUAGES
# ==========================================

print("\n===================================")
print("            LANGUAGES")
print("===================================")

if languages:

    for language, bytes_count in languages.items():

        print(language, ":", bytes_count, "bytes")


# ==========================================
# DISPLAY CONTRIBUTORS
# ==========================================

print("\n===================================")
print("          CONTRIBUTORS")
print("===================================")

if contributors:

    print(
        "Contributors fetched:",
        len(contributors)
    )

    print("\nTop contributors:")

    for contributor in contributors[:5]:

        print("-", contributor["login"])


# ==========================================
# DISPLAY COMMITS
# ==========================================

print("\n===================================")
print("             COMMITS")
print("===================================")

if commits:

    print(
        "Commits fetched:",
        len(commits)
    )

    print("\nRecent commits:")

    for commit in commits[:5]:

        author = commit["commit"]["author"]["name"]

        message = commit["commit"]["message"]

        print("-", author, ":", message)


# ==========================================
# DISPLAY ISSUES
# ==========================================

print("\n===================================")
print("           OPEN ISSUES")
print("===================================")

if issues:

    print(
        "Open issues fetched:",
        len(issues)
    )


# ==========================================
# FINISH
# ==========================================

print("\n===================================")
print("        ANALYSIS COMPLETE")
print("===================================")