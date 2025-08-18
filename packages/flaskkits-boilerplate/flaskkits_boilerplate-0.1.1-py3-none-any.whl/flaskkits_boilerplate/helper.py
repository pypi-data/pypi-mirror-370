import os
import subprocess
import secrets
from rich.console import Console

console = Console()

def run_build_css(project_dir="."):
    """Run Tailwind CSS build inside the given project directory."""
    console.print(f"[cyan]🔧 Running Tailwind build in:[/cyan] {os.path.abspath(project_dir)}\n")
    try:
        subprocess.run(
            ["npm", "run", "build:css"],
            cwd=project_dir,
            check=True
        )
        console.print("[bold green]✅ Tailwind CSS build complete![/bold green]")
    except subprocess.CalledProcessError:
        console.print("[bold red]❌ Failed to build CSS. Make sure npm and Tailwind are installed.[/bold red]")


def run_build_key(project_dir="."):
    """Generate a new SECRET_KEY and update the .env file."""
    env_path = os.path.join(project_dir, ".env")
    if not os.path.exists(env_path):
        console.print(f"[bold red]❌ File .env tidak ditemukan di direktori: {os.path.abspath(project_dir)}[/bold red]")
        return

    new_secret_key = secrets.token_hex(32)

    with open(env_path, "r", encoding="utf-8") as f:
        content = f.readlines()

    updated_content = []
    key_found = False
    for line in content:
        if line.startswith("SECRET_KEY="):
            updated_content.append(f"SECRET_KEY={new_secret_key}\n")
            key_found = True
        else:
            updated_content.append(line)

    if not key_found:
        updated_content.append(f"SECRET_KEY={new_secret_key}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(updated_content)

    console.print(f"[bold green]✅ Berhasil memperbarui SECRET_KEY di .env[/bold green]")