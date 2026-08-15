import requests
def get_repository(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        return None
data = get_repository("octocat", "Hello-World")
if data:
    print("Repository:", data["name"])
    print("Owner:", data["owner"]["login"])
    print("Stars:", data["stargazers_count"])
    print("Forks:", data["forks_count"])
    print("Issues:", data["open_issues_count"])
    print("Language:", data["language"])