import os

import typer
from dotenv import load_dotenv
from rich.console import Console

# Load environment variables from .env file

load_dotenv()

# Access the OpenAI and GitHub tokens
openai_api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")


console = Console()
app = typer.Typer()


@app.command()
def help():
    """Command for displaying help information"""
    typer.echo("Available commands:")
    typer.echo(
        "  python -m run <Username> <Repository> <Workflow_id>  - Trigger GitHub Actions workflows,Show last commit for repo,List open PRs"
    )
    typer.echo(
        "  python -m suggest <intent> - Suggest an intent based on input"
    )
    typer.echo("  python -m explain <path> - Explain a given path")
    typer.echo(
        "  python -m readme <project_title> <project_description> <username> - Generate a README file for a project"
    )
    typer.echo(
        "  python -m doc doc_explain <path> - Generate a document for explaining a path"
    )
    typer.echo(
        "  python -m doc doc_suggest <intent> - Generate a document for suggesting an intent"
    )


if __name__ == "__main__":
    app()
