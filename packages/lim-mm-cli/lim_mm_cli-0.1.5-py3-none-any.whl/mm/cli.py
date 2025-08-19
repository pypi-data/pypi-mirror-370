import typer
from mm.core import init_project, start_project, push_project, validate_project

app = typer.Typer()


@app.command()
def init(name: str):
    """Initialize a LIM-compatible project."""
    init_project(name)


@app.command()
def validate():
    """Validate mms/meta.json structure and content."""
    validate_project()


@app.command()
def push():
    """Push m to lim."""
    push_project()


@app.command()
def start():
    """Run start.py, validate /meta output, and prepare project for deployment."""
    start_project()

if __name__ == "__main__":
    app()
