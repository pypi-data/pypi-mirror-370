#!/usr/bin/env python3
import argparse
import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from .generator import create_structure, get_starter_structure_js_tlwnd as jstlw
from .installer import install_python_requirements, install_npm_dependencies
from .helper import run_build_css, run_build_key

console = Console()
DEFAULT_PROJECT_NAME = "flask_kit"


def start_project(project_name=DEFAULT_PROJECT_NAME, auto_install=False):
    os.makedirs(project_name, exist_ok=True)

    # Header Section
    console.rule(f"[bold magenta]🚀 Flask Kit[/bold magenta]")
    console.print(f"[cyan]Creating project:[/cyan] [bold yellow]{project_name}[/bold yellow]\n")

    # Generate project structure
    for _ in track(range(1), description="[green]📂 Generating structure...[/green]"):
        starter_structure = jstlw()
        create_structure(project_name, starter_structure)

    # Install dependencies
    if auto_install:
        console.print("\n⚙️  [cyan]Installing Python dependencies...[/cyan]")
        install_python_requirements(project_name)

        console.print("\n🌐  [cyan]Installing Tailwind CSS via npm...[/cyan]")
        install_npm_dependencies(project_name)

    # Footer / Next steps
    console.print(
        Panel.fit(
            f"[bold green]✅ Setup complete![/bold green]\n\n"
            f"[white]Next steps:[/white]\n"
            f"   • [yellow]cd {project_name} && python main.py[/yellow]\n"
            f"   • [blue]flaskkit run build:css[/blue]   (build Tailwind CSS)",
            title="[bold magenta]Flask Kit[/bold magenta]",
            border_style="magenta"
        )
    )

def main():
    parser = argparse.ArgumentParser(prog="flaskkit", description="Flask Kit Project Generator")
    subparsers = parser.add_subparsers(dest="command")

    # flaskkit start <name> -y
    start_parser = subparsers.add_parser("start", help="Start a new Flask Kit project")
    start_parser.add_argument("name", nargs="?", default=DEFAULT_PROJECT_NAME, help="Project name (default: flask_kit)")
    start_parser.add_argument("-y", "--yes", help="Auto install dependencies", action="store_true")

    # flaskkit run <task>
    run_parser = subparsers.add_parser("run", help="Run helper commands")
    run_parser.add_argument("task", choices=["build:css", "build:key"], help="Task to run")
    run_parser.add_argument("-p", "--path", default=".", help="Project path (default: current directory)")

    args = parser.parse_args()

    if args.command == "start":
        start_project(project_name=args.name, auto_install=args.yes)
    elif args.command == "run":
        if args.task == "build:css":
            run_build_css(args.path)
        elif args.task == "build:key":
            run_build_key(args.path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()