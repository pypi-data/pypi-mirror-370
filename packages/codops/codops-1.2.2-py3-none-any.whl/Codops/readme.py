import os
import sys

import openai
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
def generate(project_title, project_description, username):
    # openai.api_key = 'your-api-key'  # Remplacez par votre clé API

    prompt = f"""
    Generate a README file for a project with the following details:
    
    Project Title: {project_title}
    Project Description: {project_description}
    
    The README should include sections such as:
    - Project Title
    - Description
    - Username: {username}
    - Installation Instructions
    - Usage
    - Contributing
    - License
    """

    response = openai.ChatCompletion.create(
        model="gpt-4.1", messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python doc.py <project_title> <project_description> <username>"
        )
        sys.exit(1)

    title = sys.argv[1]
    description = sys.argv[2]
    username = sys.argv[3]
    readme_content = generate(title, description, username)

    with open("README.md", "w") as f:
        f.write(readme_content)

    print("README.md has been generated.")
