import openai
import os
import typer
import sys

app = typer.Typer()
@app.command()
def generate_readme(project_title: str, project_description: str, username:str):
 #   openai.api_key = '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'  # Remplacez par votre clé API

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
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response['choices'][0]['message']['content']


######

@app.command()
def run (task: str):
    """Command for running tasks """
    typer.echo(f"{task} is running.")

   
@app.command()
def suggest(intent: str):
    """Command for suggesting an intent"""
    try:
        response= openai.ChatCompletion.create(
            model= "gpt-4.1",
            messages=[
                {"role": "user", "content": f"Suggest an intent for: {intent}"}
            ]
        )
        
        suggestion = response['choices'][0]['message']['content']
        typer.echo(f"Suggestion for your intent: {suggestion}")
    except Exception as e:
        typer.echo (f"Error: {e}")

@app.command()
def explain(path: str):
    """Command for explaining a path"""
    try:
        response= openai.ChatCompletion.create(
            model= "gpt-4.1",
            messages=[
                {"role": "user", "content": f"explain this path: {path}"}
            ]
        )
        
        explanation = response['choices'][0]['message']['content']
        typer.echo(f"Expalanation for your path: {explanation}")
    except Exception as e:
        typer.echo (f"Error: {e}")



@app.command()
def help():
    """Command for displaying help information"""
    typer.echo("Available commands:")
    typer.echo("  run <task> - Run a specific task")
    typer.echo("  suggest <intent> - Suggest an intent based on input")
    typer.echo("  explain <path> - Explain a given path")
    typer.echo("  generate <project_title> <project_description> <username> - Generate a README file for a project")

###3


@app.command()
def generate(title: str, description: str, username:str):
    """Generate a README file for a project."""
    readme_content = generate_readme(title, description, username)

    with open("README.md", "w") as f:
        f.write(readme_content)

    print("README.md has been generated.")

if __name__ == "__main__":
    app()




      
    