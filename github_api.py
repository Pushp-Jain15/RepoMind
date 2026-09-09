import requests


# ==========================================
# GET BASIC REPOSITORY INFORMATION
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
# GET PROGRAMMING LANGUAGES
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
# GET CONTRIBUTORS
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
# GET COMMITS
# ==========================================

def get_commits(owner, repo):

    all_commits = []

    page = 1

    while page <= 3:

        url = f"https://api.github.com/repos/{owner}/{repo}/commits"

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
# GET OPEN ISSUES
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