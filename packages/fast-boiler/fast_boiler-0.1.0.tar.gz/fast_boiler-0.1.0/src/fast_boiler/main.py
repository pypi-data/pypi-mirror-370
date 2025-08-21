import typer
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

app = typer.Typer()

# Set up Jinja2 environment to load templates from the 'templates' directory
try:
    TEMPLATE_DIR = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True)
except Exception as e:
    typer.secho(f"Error setting up Jinja2 environment: {e}", fg=typer.colors.RED)
    raise typer.Exit()

def render_template(template_name: str, context: dict) -> str:
    """Renders a Jinja2 template with the given context."""
    return env.get_template(template_name).render(context)

def create_resource_files(name: str, base_path: Path):
    """Helper function to create all files for a new resource."""
    context = {
        "name": name,
        "ClassName": name.capitalize(),
        "plural_name": name + "s",
    }
    (base_path / f"models/{name}_model.py").write_text(render_template("model.py.j2", context))
    (base_path / f"schemas/{name}_schema.py").write_text(render_template("schema.py.j2", context))
    (base_path / f"repositories/{name}_repo.py").write_text(render_template("repo.py.j2", context))
    (base_path / f"services/{name}_service.py").write_text(render_template("service.py.j2", context))
    (base_path / f"controllers/{name}_controller.py").write_text(render_template("controller.py.j2", context))

@app.command()
def init(project_name: str):
    """
    Initializes a new FastAPI project with a Repo-Service-Controller structure.
    """
    typer.echo(f"🚀 Creating FastAPI project: {project_name}")
    root_path = Path(project_name)
    app_path = root_path / "app"
    
    # Create directory structure
    dirs = ["controllers", "models", "repositories", "schemas", "services"]
    app_path.mkdir(parents=True, exist_ok=True)
    for dir_name in dirs:
        (app_path / dir_name).mkdir(exist_ok=True)
        (app_path / dir_name / "__init__.py").touch()

    # Create core files
    (app_path / "database.py").write_text(render_template("database.py.j2", {}))
    (app_path / "__init__.py").touch()
    (root_path / ".gitignore").write_text(render_template("gitignore.j2", {}))
    (root_path / "requirements.txt").write_text(render_template("requirements.txt.j2", {}))

    # Generate the default 'user' resource and main.py
    create_resource_files("user", base_path=app_path)
    main_py_content = render_template("main.py.j2", {"default_resource": "user"})
    (app_path / "main.py").write_text(main_py_content)
    
    typer.secho(f"✅ Project '{project_name}' created successfully!", fg=typer.colors.GREEN)
    typer.echo("\nTo get started:")
    typer.echo(f"  cd {project_name}")
    typer.echo("  python -m venv venv")
    typer.echo("  source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`")
    typer.echo("  pip install -r requirements.txt")
    typer.echo("  uvicorn app.main:app --reload")

@app.command()
def generate(name: str):
    """
    Generates the files for a new resource (model, schema, repo, service, controller).
    """
    name = name.lower()
    base_path = Path("app") # Assumes running from project root

    if not base_path.exists() or not base_path.is_dir():
        typer.secho("Error: 'app' directory not found.", fg=typer.colors.RED)
        typer.secho("Please run this command from your project's root directory.", fg=typer.colors.RED)
        raise typer.Exit()
    
    typer.echo(f"📦 Generating resource: {name}")
    create_resource_files(name, base_path=base_path)
    
    typer.secho(f"✓ Generated files for '{name}'.", fg=typer.colors.GREEN)
    typer.echo("\n👉 Next step: Open 'app/main.py' and include the new router:")
    typer.secho(f"from app.controllers import {name}_controller", fg=typer.colors.YELLOW)
    typer.secho(f"app.include_router({name}_controller.router)", fg=typer.colors.YELLOW)

if __name__ == "__main__":
    app()