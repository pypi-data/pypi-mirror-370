import os

import openai
import typer
from dotenv import load_dotenv

# Load environment variables from .env file

load_dotenv()

# Access the OpenAI and GitHub tokens
openai_api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

app = typer.Typer()


@app.command()
def suggest(intent: str):
    """Command for suggesting an intent"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[
                {"role": "user", "content": f"Suggest an intent for: {intent}"}
            ],
        )
        suggestion = response["choices"][0]["message"]["content"]
        typer.echo(f"Suggestion for your intent: {suggestion}")
    except Exception as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()
