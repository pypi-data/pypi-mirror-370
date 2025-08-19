import os

import requests
import typer
from dotenv import load_dotenv

# Load environment variables from .env file

load_dotenv()

# Access the OpenAI and GitHub tokens
openai_api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

app = typer.Typer()


GITHUB_TOKEN = (
    "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"  # Remplacez par votre token
)
GITHUB_API_URL = "https://api.github.com"


# Fonction pour déclencher un workflow GitHub Actions
def trigger_workflow(owner: str, repo: str, workflow_id: str):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.post(
        url, headers=headers, json={"ref": "main"}
    )  # Assurez-vous que 'ref' est correct
    # return response.json()
    if response.status_code == 204:
        return "Workflow triggered successfully, no content returned."
    else:
        return response.json()  # Pour les autres codes de statut


# Fonction pour obtenir le dernier commit
def get_last_commit(owner: str, repo: str):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits"
    response = requests.get(url)
    return response.json()[0]  # Dernier commit


# Fonction pour lister les PRs ouvertes
def list_open_prs(owner: str, repo: str):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls?state=open"
    response = requests.get(url)
    return response.json()


@app.command()
def run(owner: str, repo: str, workflow_id: str):
    """Run GitHub Actions workflow, show last commit, and list open PRs."""
    # Déclencher le workflow
    workflow_response = trigger_workflow(owner, repo, workflow_id)
    typer.echo(f"Workflow Trigger Response: {workflow_response}")

    # Obtenir le dernier commit
    last_commit = get_last_commit(owner, repo)
    typer.echo(
        f"Last Commit: {last_commit['commit']['message']} by {last_commit['commit']['author']['name']}"
    )

    # Lister les PRs ouvertes
    open_prs = list_open_prs(owner, repo)
    typer.echo("Open Pull Requests:")
    for pr in open_prs:
        typer.echo(
            f"- #{pr['number']}: {pr['title']} by {pr['user']['login']}"
        )


if __name__ == "__main__":
    app()
