from fastapi import FastAPI, HTTPException

from github_api import (
    get_repository,
    get_languages,
    get_contributors,
    get_commits,
    get_issues
)

from utils import extract_repo_info

from database import SessionLocal, Analysis


app = FastAPI(
    title="RepoMind API",
    description="AI-powered Software Engineering Intelligence Platform",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to RepoMind API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RepoMind API"
    }


@app.get("/analyze")
def analyze_repository(url: str):

    # Step 1: Validate GitHub URL
    try:
        owner, repo = extract_repo_info(url)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # Step 2: Get repository information
    data = get_repository(owner, repo)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found or unable to access repository"
        )

    # Step 3: Get additional information
    languages = get_languages(owner, repo)
    contributors = get_contributors(owner, repo)
    commits = get_commits(owner, repo)
    issues = get_issues(owner, repo)

    # Step 4: Save analysis to database
    db = SessionLocal()

    analysis = Analysis(
        repository_name=data["name"],
        owner=data["owner"]["login"],
        stars=data["stargazers_count"],
        forks=data["forks_count"],
        open_issues=data["open_issues_count"]
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    db.close()

    # Step 5: Prepare response
    result = {
        "repository": {
            "name": data["name"],
            "owner": data["owner"]["login"],
            "description": data["description"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "open_issues": data["open_issues_count"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
            "url": data["html_url"]
        },

        "languages": languages or {},

        "contributors": {
            "count": len(contributors) if contributors else 0,
            "top_contributors": [
                contributor["login"]
                for contributor in contributors[:5]
            ] if contributors else []
        },

        "commits": {
            "count": len(commits) if commits else 0,
            "recent_commits": [
                {
                    "author": commit["commit"]["author"]["name"],
                    "message": commit["commit"]["message"]
                }
                for commit in commits[:5]
            ] if commits else []
        },

        "issues": {
            "open_issues_fetched": len(issues) if issues else 0
        },

        "database": {
            "saved": True,
            "analysis_id": analysis.id
        }
    }

    return result


@app.get("/analyses")
def get_previous_analyses():

    db = SessionLocal()

    analyses = db.query(Analysis).all()

    result = []

    for analysis in analyses:
        result.append({
            "id": analysis.id,
            "repository": analysis.repository_name,
            "owner": analysis.owner,
            "stars": analysis.stars,
            "forks": analysis.forks,
            "open_issues": analysis.open_issues,
            "analyzed_at": analysis.analyzed_at
        })

    db.close()

    return {
        "count": len(result),
        "analyses": result
    }