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
def docsug(content: str, filename: str):
    """Command for generating a document for the given suggestions of the content"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": f"suggest an intent for: {content}",
                }
            ],
        )

        doc_content = response["choices"][0]["message"]["content"]
        # typer.echo(f"Suggestion for ypur intent: {doc_content}")
        console.print(
            f"[bold purple underline]Suggestion for ypur intent:[/bold purple underline] {doc_content}"
        )
    except Exception as e:
        typer.echo(f"Error: {e}")

    if doc_content is not None:  # Vérifie si le contenu est valide
        with open(filename, "w") as f:
            f.write(doc_content)
        # typer.echo(f"{filename} has been generated with the content: {doc_content}")
        console.print(
            f"[bold brown]Document '{filename}' has been generated with the content:[/bold brown]\n{doc_content}"
        )
    else:
        typer.echo("Failed to generate document due to empty content.")


if __name__ == "__main__":
    app()
