import os

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
def explain(path: str):
    """Command for explaining a path"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[
                {"role": "user", "content": f"explain this path: {path}"}
            ],
        )

        explanation = response["choices"][0]["message"]["content"]
        result = explanation.replace("**", "")

        # console.print(f"[bold purple underline]Explanation for your path:[/bold purple underline] {explanation}")
        console.print(
            f"[bold purple underline]Explanation for your path:[/bold purple underline] {result}"
        )
    # typer.echo(f"Expalanation for your path: {explanation}")
    except Exception as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()
