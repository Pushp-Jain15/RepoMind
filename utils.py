from urllib.parse import urlparse


def extract_repo_info(github_url):
    github_url = github_url.strip().rstrip("/")

    parsed_url = urlparse(github_url)

    # Check that URL uses HTTPS
    if parsed_url.scheme != "https":
        raise ValueError("GitHub URL must use HTTPS")

    # Check that URL belongs to GitHub
    if parsed_url.netloc.lower() != "github.com":
        raise ValueError("URL must be a GitHub repository URL")

    # Get repository path
    parts = parsed_url.path.strip("/").split("/")

    # GitHub repository URL should contain owner and repo
    if len(parts) != 2:
        raise ValueError("Invalid GitHub repository URL")

    owner = parts[0]
    repo = parts[1]

    # Remove .git if user enters a Git clone URL
    if repo.endswith(".git"):
        repo = repo[:-4]

    if not owner or not repo:
        raise ValueError("Invalid GitHub repository URL")

    return owner, repo