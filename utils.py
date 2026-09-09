# ==========================================
# EXTRACT OWNER AND REPOSITORY
# FROM GITHUB URL
# ==========================================

def extract_repo_info(github_url):

    # Remove / from the end of the URL
    github_url = github_url.rstrip("/")

    # Split URL using /
    parts = github_url.split("/")

    # Check whether URL has enough parts
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")

    # Get owner and repository name
    owner = parts[-2]

    repo = parts[-1]

    return owner, repo