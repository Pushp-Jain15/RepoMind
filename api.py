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
    calculate_health_score
)

from database import SessionLocal, Repository, Analysis


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="RepoMind API",
    description="AI-powered Software Engineering Intelligence Platform",
    version="1.0.0"
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Welcome to RepoMind API",
        "status": "running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ============================================================
# ANALYZE REPOSITORY
# ============================================================

@app.get("/analyze")
def analyze_repository(url: str):

    # --------------------------------------------------------
    # 1. Validate and extract repository information
    # --------------------------------------------------------

    try:

        owner, repo = extract_repo_info(url)

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    # --------------------------------------------------------
    # 2. Get repository information from GitHub
    # --------------------------------------------------------

    data = get_repository(
        owner,
        repo
    )

    if data is None:

        raise HTTPException(
            status_code=404,
            detail="Repository not found or unable to access repository"
        )


    # --------------------------------------------------------
    # 3. Collect GitHub data
    # --------------------------------------------------------

    languages = get_languages(
        owner,
        repo
    )

    contributors = get_contributors(
        owner,
        repo
    )

    commits = get_commits(
        owner,
        repo
    )

    issues = get_issues(
        owner,
        repo
    )


    # --------------------------------------------------------
    # 4. Analyze changed files
    # --------------------------------------------------------

    file_stats = analyze_file_changes(
        owner,
        repo,
        commits
    )


    # --------------------------------------------------------
    # 5. Calculate software metrics
    # --------------------------------------------------------

    repository_metrics = calculate_repository_metrics(
        data,
        contributors,
        commits,
        file_stats
    )


    # --------------------------------------------------------
    # 6. Calculate health indicators
    # --------------------------------------------------------

    health_indicators = calculate_health_indicators(
        repository_metrics
    )


    # --------------------------------------------------------
    # 7. Calculate health score
    # --------------------------------------------------------

    health_score = calculate_health_score(
        health_indicators
    )


    # ========================================================
    # DATABASE
    # ========================================================

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # 8. Check if repository already exists
        # ----------------------------------------------------

        repository = db.query(
            Repository
        ).filter(
            Repository.url == data["html_url"]
        ).first()


        # ----------------------------------------------------
        # 9. Create repository if it doesn't exist
        # ----------------------------------------------------

        if repository is None:

            repository = Repository(
                owner=data["owner"]["login"],
                name=data["name"],
                url=data["html_url"]
            )

            db.add(repository)

            db.commit()

            db.refresh(repository)


        # ----------------------------------------------------
        # 10. Store analysis
        # ----------------------------------------------------

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


    # ========================================================
    # API RESPONSE
    # ========================================================

    result = {

        # ----------------------------------------------------
        # REPOSITORY
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # LANGUAGES
        # ----------------------------------------------------

        "languages": languages,


        # ----------------------------------------------------
        # CONTRIBUTORS
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # COMMITS
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # ISSUES
        # ----------------------------------------------------

        "issues": {

            "open_issues_fetched": len(issues)
            if issues
            else 0

        },


        # ----------------------------------------------------
        # FILE ANALYSIS
        # ----------------------------------------------------

        "file_analysis": file_stats,


        # ----------------------------------------------------
        # SOFTWARE METRICS
        # ----------------------------------------------------

        "metrics": repository_metrics,


        # ----------------------------------------------------
        # HEALTH INDICATORS
        # ----------------------------------------------------

        "health_indicators": health_indicators,


        # ----------------------------------------------------
        # HEALTH SCORE
        # ----------------------------------------------------

        "health_score": health_score

    }


    return result


# ============================================================
# GET ALL REPOSITORIES
# ============================================================

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


# ============================================================
# GET ALL ANALYSES
# ============================================================

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