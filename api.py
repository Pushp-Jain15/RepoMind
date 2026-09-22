from fastapi import FastAPI, HTTPException

from github_api import (
    get_repository,
    get_languages,
    get_contributors,
    get_commits,
    get_issues,
    analyze_file_changes
)

from utils import extract_repo_info

from metrics import (
    calculate_repository_metrics,
    calculate_health_indicators,
    calculate_health_score,
    calculate_file_risk_indicators
)

from database import SessionLocal, Repository, Analysis


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
        "status": "healthy"
    }


@app.get("/analyze")
def analyze_repository(url: str):

    # -----------------------------------
    # Step 1: Validate GitHub URL
    # -----------------------------------

    try:
        owner, repo = extract_repo_info(url)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    # -----------------------------------
    # Step 2: Get repository information
    # -----------------------------------

    data = get_repository(owner, repo)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found or unable to access repository"
        )


    # -----------------------------------
    # Step 3: Collect GitHub data
    # -----------------------------------

    languages = get_languages(owner, repo)

    contributors = get_contributors(owner, repo)

    commits = get_commits(owner, repo)

    issues = get_issues(owner, repo)


    # -----------------------------------
    # Step 4: Analyze file changes
    # -----------------------------------

    file_stats = analyze_file_changes(
        owner,
        repo,
        commits
    )


    # -----------------------------------
    # Step 5: Calculate file risk
    # -----------------------------------

    file_risk = calculate_file_risk_indicators(
        file_stats
    )


    # -----------------------------------
    # Step 6: Calculate repository metrics
    # -----------------------------------

    repository_metrics = calculate_repository_metrics(
        data,
        contributors,
        commits,
        file_stats
    )


    # -----------------------------------
    # Step 7: Calculate health indicators
    # -----------------------------------

    health_indicators = calculate_health_indicators(
        repository_metrics
    )


    # -----------------------------------
    # Step 8: Calculate health score
    # -----------------------------------

    health_score = calculate_health_score(
        health_indicators
    )


    # -----------------------------------
    # Step 9: Save analysis to database
    # -----------------------------------

    db = SessionLocal()

    try:

        repository = db.query(
            Repository
        ).filter(
            Repository.url == data["html_url"]
        ).first()


        # Create repository if it doesn't exist
        if repository is None:

            repository = Repository(
                owner=data["owner"]["login"],
                name=data["name"],
                url=data["html_url"]
            )

            db.add(repository)

            db.commit()

            db.refresh(repository)


        # Create analysis record
        analysis = Analysis(
            repository_id=repository.id,
            stars=data["stargazers_count"],
            forks=data["forks_count"],
            open_issues=data["open_issues_count"]
        )

        db.add(analysis)

        db.commit()


    finally:

        db.close()


    # -----------------------------------
    # Step 10: Prepare API response
    # -----------------------------------

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


        "languages": languages,


        "contributors": {

            "count": len(contributors)
            if contributors
            else 0,

            "top_contributors": [

                contributor["login"]

                for contributor in contributors[:5]

            ]
            if contributors
            else []
        },


        "commits": {

            "count": len(commits)
            if commits
            else 0,

            "recent_commits": [

                {
                    "author": commit["commit"]["author"]["name"],

                    "message": commit["commit"]["message"]
                }

                for commit in commits[:5]

            ]
            if commits
            else []
        },


        "issues": {

            "open_issues_fetched": len(issues)
            if issues
            else 0
        },


        # Raw file change information
        "file_analysis": file_stats,


        # NEW — File-level risk analysis
        "file_risk": file_risk,


        # Repository-level metrics
        "metrics": repository_metrics,


        # Repository health indicators
        "health_indicators": health_indicators,


        # Repository health score
        "health_score": health_score
    }


    return result


@app.get("/repositories")
def get_all_repositories():

    db = SessionLocal()

    try:

        repositories = db.query(
            Repository
        ).all()


        return [

            {
                "id": repository.id,

                "owner": repository.owner,

                "name": repository.name,

                "url": repository.url
            }

            for repository in repositories
        ]


    finally:

        db.close()


@app.get("/analyses")
def get_all_analyses():

    db = SessionLocal()

    try:

        analyses = db.query(
            Analysis
        ).all()


        return [

            {
                "id": analysis.id,

                "repository_id": analysis.repository_id,

                "stars": analysis.stars,

                "forks": analysis.forks,

                "open_issues": analysis.open_issues,

                "analyzed_at": analysis.analyzed_at
            }

            for analysis in analyses
        ]


    finally:

        db.close()