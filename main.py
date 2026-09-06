import requests


# ==========================================
# GITHUB API FUNCTIONS
# ==========================================

def get_repository(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error getting repository:", response.status_code)
        return None


def get_languages(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error getting languages:", response.status_code)
        return None


def get_contributors(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error getting contributors:", response.status_code)
        return None


def get_commits(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error getting commits:", response.status_code)
        return None


def get_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error getting issues:", response.status_code)
        return None


# ==========================================
# REPOSITORY TO ANALYZE
# ==========================================

owner = "facebook"
repo = "react"


# ==========================================
# COLLECT DATA
# ==========================================

data = get_repository(owner, repo)

languages = get_languages(owner, repo)

contributors = get_contributors(owner, repo)

commits = get_commits(owner, repo)

issues = get_issues(owner, repo)


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\n===================================")
print("          REPOMIND ANALYSIS")
print("===================================")


# ------------------------------------------
# Repository information
# ------------------------------------------

print("\n--- REPOSITORY INFORMATION ---")

if data:

    print("Repository:", data["name"])
    print("Owner:", data["owner"]["login"])
    print("Description:", data["description"])
    print("Stars:", data["stargazers_count"])
    print("Forks:", data["forks_count"])
    print("Open Issues:", data["open_issues_count"])
    print("Created:", data["created_at"])
    print("Updated:", data["updated_at"])
    print("URL:", data["html_url"])


# ------------------------------------------
# Languages
# ------------------------------------------

print("\n--- LANGUAGES ---")

if languages:

    for language, bytes_count in languages.items():

        print(language, ":", bytes_count, "bytes")


# ------------------------------------------
# Contributors
# ------------------------------------------

print("\n--- CONTRIBUTORS ---")

if contributors:

    print("Number of contributors fetched:", len(contributors))

    print("\nTop contributors:")

    for contributor in contributors[:5]:

        print("-", contributor["login"])


# ------------------------------------------
# Commits
# ------------------------------------------

print("\n--- RECENT COMMITS ---")

if commits:

    print("Commits fetched:", len(commits))

    for commit in commits[:5]:

        author = commit["commit"]["author"]["name"]

        message = commit["commit"]["message"]

        print("-", author, ":", message)


# ------------------------------------------
# Issues
# ------------------------------------------

print("\n--- ISSUES ---")

if issues:

    print("Issues fetched:", len(issues))


# ==========================================
# COMPLETION
# ==========================================

print("\n===================================")
print("       ANALYSIS COMPLETE")
print("===================================")