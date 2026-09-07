import requests


# ==========================================
# 1. EXTRACT OWNER AND REPOSITORY FROM URL
# ==========================================

def extract_repo_info(github_url):

    github_url = github_url.rstrip("/")

    parts = github_url.split("/")

    owner = parts[-2]
    repo = parts[-1]

    return owner, repo


# ==========================================
# 2. GET BASIC REPOSITORY INFORMATION
# ==========================================

def get_repository(owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    else:
        print("Error getting repository:", response.status_code)
        return None


# ==========================================
# 3. GET LANGUAGES
# ==========================================

def get_languages(owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}/languages"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    else:
        print("Error getting languages:", response.status_code)
        return None


# ==========================================
# 4. GET CONTRIBUTORS
# ==========================================

def get_contributors(owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    else:
        print("Error getting contributors:", response.status_code)
        return None


# ==========================================
# 5. GET COMMITS WITH PAGINATION
# ==========================================

def get_commits(owner, repo):

    all_commits = []

    page = 1

    while page <= 3:

        url = (
            f"https://api.github.com/repos/"
            f"{owner}/{repo}/commits"
        )

        params = {
            "page": page,
            "per_page": 100
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print("Error getting commits:", response.status_code)
            break

        commits = response.json()

        if not commits:
            break

        all_commits.extend(commits)

        page += 1

    return all_commits


# ==========================================
# 6. GET ISSUES
# ==========================================

def get_issues(owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    params = {
        "state": "open",
        "per_page": 100
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()

    else:
        print("Error getting issues:", response.status_code)
        return None


# ==========================================
# MAIN PROGRAM
# ==========================================

print("\n===================================")
print("          REPOMIND")
print("===================================")

github_url = input("\nEnter GitHub repository URL: ")

try:

    owner, repo = extract_repo_info(github_url)

except:

    print("Invalid GitHub URL.")
    exit()


print("\nAnalyzing repository...")
print("Owner:", owner)
print("Repository:", repo)


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
# LANGUAGES
# ==========================================

print("\n===================================")
print("            LANGUAGES")
print("===================================")

if languages:

    for language, bytes_count in languages.items():

        print(language, ":", bytes_count, "bytes")


# ==========================================
# CONTRIBUTORS
# ==========================================

print("\n===================================")
print("          CONTRIBUTORS")
print("===================================")

if contributors:

    print("Contributors fetched:", len(contributors))

    for contributor in contributors[:5]:

        print("-", contributor["login"])


# ==========================================
# COMMITS
# ==========================================

print("\n===================================")
print("          COMMITS")
print("===================================")

if commits:

    print("Commits fetched:", len(commits))

    for commit in commits[:5]:

        author = commit["commit"]["author"]["name"]

        message = commit["commit"]["message"]

        print("-", author, ":", message)


# ==========================================
# ISSUES
# ==========================================

print("\n===================================")
print("           OPEN ISSUES")
print("===================================")

if issues:

    print("Open issues fetched:", len(issues))


print("\n===================================")
print("        ANALYSIS COMPLETE")
print("===================================")