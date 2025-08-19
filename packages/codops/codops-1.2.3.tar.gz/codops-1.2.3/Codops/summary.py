import git
import os
import typer
import openai
from dotenv import load_dotenv

# Load environment variables from .env file

load_dotenv()

# Access the OpenAI and GitHub tokens
openai.api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

app = typer.Typer()

def get_commits(repo_path):
    repo = git.Repo(repo_path)
    commits = repo.iter_commits()
    return commits

def summarize_features(commits):
    features = []
    for commit in commits:
        if 'feature' in commit.message.lower():
            features.append(commit.message)
    return features

def list_cli_commands(commits):
    commands = []
    for commit in commits:
        if 'command' in commit.message.lower():
            commands.append(commit.message)
    return commands


def generate_markdown_report(features, commands):
    prompt = f"""
    Generate a Markdown report for the following features and commands:

    ## Features Built
    {features}

    ## CLI Commands Contributed
    {commands}

    Please format this nicely in Markdown.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']

@app.command()
def generate_summary(repo_path):
    commits = get_commits(repo_path)
    features = summarize_features(commits)
    commands = list_cli_commands(commits)
    report = generate_markdown_report(features, commands)
    return report

if __name__ == "__main__":
    app()