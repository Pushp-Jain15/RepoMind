from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import (
    SessionLocal,
    Repository,
    Analysis
)

from github_api import (
    get_repository,
    get_languages,
    get_contributors,
    get_commits,
    get_issues,
    analyze_file_changes,
    analyze_repository_files,
    analyze_code_metrics
)

from metrics import (
    calculate_repository_metrics,
    calculate_health_indicators,
    calculate_health_score,
    calculate_file_risk_indicators,
    calculate_risk_summary,
    calculate_risk_reason_summary
)

from utils import extract_repo_info


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="RepoMind API",
    description=(
        "AI-powered Software Engineering "
        "Intelligence Platform"
    ),
    version="0.1.0"
)


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Welcome to RepoMind API",
        "status": "running"
    }


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# Repository analysis endpoint
# ---------------------------------------------------------

@app.get("/analyze")
def analyze_repository(
    github_url: str
):

    # -----------------------------------------------------
    # Extract repository information
    # -----------------------------------------------------

    try:

        owner, repo = extract_repo_info(
            github_url
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    # -----------------------------------------------------
    # Repository information
    # -----------------------------------------------------

    data = get_repository(
        owner,
        repo
    )

    if not data:

        raise HTTPException(
            status_code=404,
            detail=(
                "Repository not found "
                "or GitHub API request failed."
            )
        )


    # -----------------------------------------------------
    # Languages
    # -----------------------------------------------------

    languages = get_languages(
        owner,
        repo
    )

    if languages is None:

        languages = {}


    # -----------------------------------------------------
    # Contributors
    # -----------------------------------------------------

    contributors = get_contributors(
        owner,
        repo
    )

    if contributors is None:

        contributors = []


    # -----------------------------------------------------
    # Commits
    # -----------------------------------------------------

    commits = get_commits(
        owner,
        repo
    )

    if commits is None:

        commits = []


    # -----------------------------------------------------
    # Issues and pull requests
    # -----------------------------------------------------

    issues_data = get_issues(
        owner,
        repo
    )

    actual_issues = issues_data.get(
        "issues",
        []
    )

    pull_requests = issues_data.get(
        "pull_requests",
        []
    )


    # -----------------------------------------------------
    # File change analysis
    # -----------------------------------------------------

    file_stats = analyze_file_changes(
        owner,
        repo,
        commits
    )


    # -----------------------------------------------------
    # Repository file structure
    # -----------------------------------------------------

    default_branch = data.get(
        "default_branch",
        "main"
    )

    file_structure = (
        analyze_repository_files(
            owner,
            repo,
            default_branch
        )
    )


    # -----------------------------------------------------
    # Code-level metrics
    # -----------------------------------------------------

    code_metrics = analyze_code_metrics(
        owner,
        repo,
        file_structure[
            "source_files"
        ],
        default_branch,
        max_files=30
    )


    # -----------------------------------------------------
    # File risk analysis
    # -----------------------------------------------------

    file_risk = (
        calculate_file_risk_indicators(
            file_stats
        )
    )


    # -----------------------------------------------------
    # Risk summary
    # -----------------------------------------------------

    risk_summary = (
        calculate_risk_summary(
            file_risk
        )
    )


    # -----------------------------------------------------
    # Risk reason summary
    # -----------------------------------------------------

    risk_reason_summary = (
        calculate_risk_reason_summary(
            file_risk
        )
    )


    # -----------------------------------------------------
    # Repository metrics
    # -----------------------------------------------------

    repository_metrics = (
        calculate_repository_metrics(
            data,
            contributors,
            commits,
            file_stats,
            open_issues=len(
                actual_issues
            )
        )
    )


    # -----------------------------------------------------
    # Health indicators
    # -----------------------------------------------------

    health_indicators = (
        calculate_health_indicators(
            repository_metrics
        )
    )


    # -----------------------------------------------------
    # Health score
    # -----------------------------------------------------

    health_score = (
        calculate_health_score(
            health_indicators
        )
    )


    # -----------------------------------------------------
    # Database
    # -----------------------------------------------------

    db: Session = SessionLocal()

    try:

        repository = (
            db.query(Repository)
            .filter(
                Repository.url
                ==
                github_url.strip().rstrip("/")
            )
            .first()
        )

        if repository is None:

            repository = Repository(
                owner=owner,
                name=repo,
                url=(
                    github_url
                    .strip()
                    .rstrip("/")
                )
            )

            db.add(repository)

            db.commit()

            db.refresh(
                repository
            )


        analysis = Analysis(
            repository_id=repository.id,

            stars=data.get(
                "stargazers_count",
                0
            ),

            forks=data.get(
                "forks_count",
                0
            ),

            open_issues=len(
                actual_issues
            )
        )

        db.add(
            analysis
        )

        db.commit()

    finally:

        db.close()


    # -----------------------------------------------------
    # Final API response
    # -----------------------------------------------------

    return {

        "repository": {

            "name": data.get(
                "name"
            ),

            "full_name": data.get(
                "full_name"
            ),

            "owner": owner,

            "url": data.get(
                "html_url"
            ),

            "description": data.get(
                "description"
            ),

            "default_branch": (
                default_branch
            ),

            "stars": data.get(
                "stargazers_count",
                0
            ),

            "forks": data.get(
                "forks_count",
                0
            ),

            "language": data.get(
                "language"
            )
        },


        "languages": languages,


        "contributors": {

            "total": len(
                contributors
            ),

            "data": contributors
        },


        "commits": {

            "analyzed": len(
                commits
            )
        },


        "issues": {

            "actual_open_issues": len(
                actual_issues
            ),

            "open_pull_requests": len(
                pull_requests
            ),

            "total_items_fetched": (
                len(actual_issues)
                +
                len(pull_requests)
            )
        },


        "file_structure": (
            file_structure
        ),


        "code_metrics": (
            code_metrics
        ),


        "file_analysis": (
            file_stats
        ),


        "file_risk": (
            file_risk
        ),


        "risk_summary": (
            risk_summary
        ),


        "risk_reason_summary": (
            risk_reason_summary
        ),


        "metrics": (
            repository_metrics
        ),


        "health_indicators": (
            health_indicators
        ),


        "health_score": (
            health_score
        )
    }