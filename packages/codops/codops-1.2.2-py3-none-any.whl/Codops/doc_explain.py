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
# from explain import explain  # Assurez-vous que cette fonction existe dans explain.py
# from suggest import suggest    # Assurez-vous que cette fonction existe dans suggest.py


app = typer.Typer()


@app.command()
def docexp(content: str, filename: str):
    """Command for generating a document for the given explanations of the content"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[
                {"role": "user", "content": f"explain this path: {content}"}
            ],
        )

        doc_content = response["choices"][0]["message"]["content"]

        # typer.echo(f"Expalanation for your path: {doc_content}")
        console.print(
            f"[bold purple underline]Explanation for your path:[/bold purple underline] {doc_content}"
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

    # print(f"doc content: {doc_content}")
    # doc_name = filename if filename else "document.txt"
    # with open(doc_name, "w") as f:
    #     f.write(doc_content)
    # print(f"the document '{doc_name}' has been generated with the content: {doc_content}")


# @app.command()
# def generateexplain(
#     concept: str,
#     filename: str
# ):
#     """Generate a document with the explanation of the concept."""

#     explanation = explain(concept)
#     document(explanation, filename)
#     typer.echo(f"Document '{filename}' with explanation has been generated.")


"""
 def generate_document(content: str, filename: str):
    with open(filename, "w") as f:
        f.write(content)
    if __name__ == "__main__":
     if len(sys.argv) != 2:
        print("Usage: python doc.py <content> <filename>")
        sys.exit(1)
    generate_document(sys.argv[1], sys.argv[2])
"""


if __name__ == "__main__":
    app()
