from urllib.parse import urlparse

def extract_repo_info(github_url):

    parsed_url = urlparse(github_url.strip())

    if parsed_url.scheme not in ("http", "https"):
        raise ValueError("Invalid GitHub URL")

    if parsed_url.hostname != "github.com":
        raise ValueError("Invalid GitHub URL")

    parts = [part for part in parsed_url.path.split("/") if part]

    if len(parts) != 2:
        raise ValueError("Invalid GitHub URL")

    owner = parts[0]
    repo = parts[1].removesuffix(".git")

    if not repo:
        raise ValueError("Invalid GitHub URL")

    return owner, repo