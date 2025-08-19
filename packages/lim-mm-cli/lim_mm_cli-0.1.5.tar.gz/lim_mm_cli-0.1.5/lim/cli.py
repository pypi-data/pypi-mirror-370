import typer
from lim.core import init_project, push_project, validate_project

app = typer.Typer()


@app.command()
def validate():
    """Validate meta.json structure and content."""
    validate_project()


@app.command()
def push():
    """Run start.py, validate /meta output, and prepare project for deployment."""
    push_project()


if __name__ == "__main__":
    app()
