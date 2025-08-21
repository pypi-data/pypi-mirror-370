#!/usr/bin/env python3
"""Create Smithery Python - CLI for scaffolding MCP servers."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

app = typer.Typer()
console = Console()


def run_command(cmd: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def clone_and_setup(project_name: str, template: str = "quickstart") -> None:
    """Clone the template and set up the project."""
    project_path = Path(project_name)
    
    # Check if directory already exists
    if project_path.exists():
        console.print(f"[red]Error: Directory '{project_name}' already exists![/red]")
        raise typer.Exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Clone the repository
        task = progress.add_task("Cloning template from GitHub...", total=None)
        
        # For now, let's just create the directory structure manually
        # In the future, we'll clone from a real repo
        project_path.mkdir()
        
        # Create basic files
        (project_path / "main.py").write_text("""import os
import uvicorn
from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

mcp = FastMCP(name=\"{project_name}\")

@mcp.tool
def greet(name: str) -> str:
    \"\"\"Greet a user by name.\"\"\"
    return f\"Hello, {{name}}!\"

# Workaround for Starlette Mount trailing slash behavior
class MCPPathRedirect:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get('type') == 'http' and scope.get('path') == '/mcp':
            scope['path'] = '/mcp/'
            scope['raw_path'] = b'/mcp/'
        await self.app(scope, receive, send)

if __name__ == \"__main__\":
    app = mcp.streamable_http_app()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[\"*\"],
        allow_credentials=True,
        allow_methods=[\"GET\", \"POST\", \"OPTIONS\"],
        allow_headers=[\"*\"],
        expose_headers=[\"mcp-session-id\"],
        max_age=86400,
    )

    app = MCPPathRedirect(app)
    port = int(os.environ.get(\"PORT\", 8080))

    uvicorn.run(
        app,
        host=\"0.0.0.0\",
        port=port,
        log_level=\"info\"
    )
""".format(project_name=project_name))
        
        # Create pyproject.toml
        (project_path / "pyproject.toml").write_text(f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "MCP server built with FastMCP"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastmcp>=2.10.6",
    "uvicorn>=0.35.0",
]
""")
        
        # Create smithery.yaml
        (project_path / "smithery.yaml").write_text("""runtime: "container"
build:
  dockerfile: "Dockerfile"
  dockerBuildPath: "."
startCommand:
  type: "http"
""")
        
        # Create Dockerfile
        (project_path / "Dockerfile").write_text("""# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install dependencies
COPY pyproject.toml ./
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY . /app

# Set port to 8080 as required by Smithery proxy
ENV PORT=8080
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]
""")
        
        # Create README
        (project_path / "README.md").write_text(f"""# {project_name}

A simple MCP server built with FastMCP for Smithery.

## Quick Start

1. Install dependencies:
   ```bash
   uv pip install -r pyproject.toml
   ```

2. Run the server:
   ```bash
   python main.py
   ```

3. Deploy to Smithery:
   - Push your code to GitHub
   - Connect your repository at https://smithery.ai/new

Your server will be available over HTTP!
""")
        
        progress.update(task, description="Template created", completed=True)
        
        # Install dependencies
        task = progress.add_task("Installing dependencies...", total=None)
        
        # Check if uv is available
        if shutil.which("uv"):
            cmd = ["uv", "pip", "install", "-r", "pyproject.toml"]
            result = run_command(cmd, cwd=project_path)
            if result.returncode != 0:
                console.print(f"[yellow]Warning: Failed to install dependencies: {result.stderr}[/yellow]")
        else:
            console.print("[yellow]Warning: uv not found. Please install dependencies manually.[/yellow]")
        
        progress.update(task, description="Dependencies installed", completed=True)


@app.command()
def main(
    project_name: Optional[str] = typer.Argument(None, help="Name of the project to create"),
) -> None:
    """Create a new Smithery MCP server in Python."""
    
    # Show unofficial notice
    console.print("[yellow]Note: This is an unofficial tool. For official Smithery tools, visit smithery.ai[/yellow]\n")
    
    # If no project name provided, ask for it
    if not project_name:
        project_name = typer.prompt("What is your project name?")
        if not project_name.strip():
            console.print("[red]Project name cannot be empty![/red]")
            raise typer.Exit(1)
    
    console.print(f"Creating project: [bold green]{project_name}[/bold green]")
    
    try:
        clone_and_setup(project_name)
        
        # Success message
        console.print("")
        console.print(Panel.fit(
            f"[bold green]Welcome to your MCP server! 🚀[/bold green]\n\n"
            f"To get started, run:\n\n"
            f"[bold cyan]cd {project_name} && python main.py[/bold cyan]\n\n"
            f"Try using the 'greet' tool to say hello!",
            title="Success",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
