# RepoMind

> AI-powered Software Engineering Intelligence Platform

RepoMind analyzes GitHub repositories to extract development insights from code, commits, contributors, issues, and repository activity.

The project aims to predict file-level bug risk using software metrics and Git history, with AI-powered explanations for developers.

## Current Features

- GitHub repository analysis
- Language and contributor analysis
- Commit and issue analysis
- FastAPI backend
- REST API with interactive Swagger documentation

## Tech Stack

**Python · FastAPI · GitHub REST API · Requests**

## Run Locally

```bash
pip install -r requirements.txt
uvicorn api:app --reload
