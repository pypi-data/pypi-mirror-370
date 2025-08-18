import os
import sys
import platform
import subprocess
from pathlib import Path

import click
import questionary

# Preset “stacks” like a Next.js template list
STACKS = {
    "Data Science": [
        "numpy", "pandas", "matplotlib", "scipy", "scikit-learn", "seaborn",
        "jupyter"
    ],
    "Deep Learning": [
        "tensorflow", "torch", "torchvision", "torchaudio"
    ],
    "Web (FastAPI)": [
        "fastapi", "uvicorn[standard]", "pydantic", "python-dotenv"
    ],
    "Web (Flask)": [
        "flask", "python-dotenv"
    ],
    "Utils / Tooling": [
        "black", "isort", "ruff", "pytest", "ipykernel"
    ],
}

DEFAULT_FILES = {
    "README.md": "# {project}\n\nGenerated with py-create-app.\n",
    ".gitignore": """# Python
__pycache__/
*.py[cod]
.env
.venv
venv/
ENV/
env/
.ipynb_checkpoints/
dist/
build/
.pytest_cache/
.mypy_cache/
.coverage
*.egg-info/
""",
    "requirements.txt": "",
    "src/__init__.py": "",
    "src/main.py": """def main():
    print("Hello from {project}!")


if __name__ == "__main__":
    main()
""",
}


def _pip_path(venv_dir: Path) -> str:
    if platform.system().lower().startswith("win"):
        return str(venv_dir / "Scripts" / "pip.exe")
    return str(venv_dir / "bin" / "pip")


def _python_path(venv_dir: Path) -> str:
    if platform.system().lower().startswith("win"):
        return str(venv_dir / "Scripts" / "python.exe")
    return str(venv_dir / "bin" / "python")


def _run(cmd: list[str]) -> int:
    return subprocess.run(cmd, check=False).returncode


@click.command()
@click.argument("project_name", required=False)
@click.option("--no-venv", is_flag=True, help="Do not create a virtual environment.")
@click.option("--init-git/--no-init-git", default=True, help="Initialize a git repo.")
@click.option("--stack", type=click.Choice(list(STACKS.keys())), multiple=True,
              help="Preselect one or more stacks (can still edit interactively).")
def create_app(project_name: str | None, no_venv: bool, init_git: bool, stack: tuple[str, ...]):
    """
    Bootstrap a new Python project with venv + interactive library selection.
    Example:\n
        py-create-app myproj
    """
    # 1) Ask for project name if not provided
    if not project_name:
        project_name = questionary.text("Project name?").ask()
        if not project_name:
            click.secho("No project name provided. Aborting.", fg="red")
            sys.exit(1)

    project_dir = Path(project_name).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    # 2) Choose stacks
    preselected = set()
    for s in stack:
        preselected.update(STACKS.get(s, []))

    chosen_stacks = questionary.checkbox(
        "Select stacks to include (space to toggle, enter to confirm):",
        choices=list(STACKS.keys())
    ).ask()

    selected_libs = set(preselected)
    if chosen_stacks:
        for s in chosen_stacks:
            selected_libs.update(STACKS[s])

    # 3) Fine-grained library selection
    all_libs = sorted({lib for libs in STACKS.values() for lib in libs})
    defaults = [q for q in all_libs if q in selected_libs]

    kwargs = {"choices": all_libs}
    if defaults:  # ✅ only set default when non-empty
        kwargs["default"] = defaults

    final_libs = questionary.checkbox(
        "Pick libraries to install (you can adjust selection):",
        choices=all_libs
    ).ask()

    # 4) Extra libraries (custom)
    extra = questionary.text(
        "Any extra packages? (comma-separated, leave blank for none)"
    ).ask()
    if extra:
        for pkg in [p.strip() for p in extra.split(",") if p.strip()]:
            final_libs.append(pkg)

    # 5) Create venv (unless skipped)
    venv_dir = project_dir / ".venv"
    if not no_venv:
        click.secho("Creating virtual environment...", fg="cyan")
        rc = _run([sys.executable, "-m", "venv", str(venv_dir)])
        if rc != 0:
            click.secho("Failed to create venv.", fg="red")
            sys.exit(1)
        pip = _pip_path(venv_dir)
    else:
        pip = "pip"

    # 6) Write starter files
    click.secho("Creating starter files...", fg="cyan")
    for rel, content in DEFAULT_FILES.items():
        dest = project_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content.format(project=project_name), encoding="utf-8")

    # Populate requirements.txt with unpinned selections
    (project_dir / "requirements.txt").write_text(
        "\n".join(final_libs) + ("\n" if final_libs else ""),
        encoding="utf-8"
    )

    # 7) Install libraries
    if final_libs:
        click.secho(f"Installing: {', '.join(final_libs)}", fg="cyan")
        rc = _run([pip, "install"] + final_libs)
        if rc != 0:
            click.secho("Some packages failed to install. Check logs above.", fg="yellow")

    # 8) Optional: init git
    if init_git:
        click.secho("Initializing git repository...", fg="cyan")
        _run(["git", "init", str(project_dir)])
        _run(["git", "-C", str(project_dir), "add", "."])
        _run(["git", "-C", str(project_dir), "commit", "-m", "Initial commit"])

    # 9) Final instructions
    click.secho("\n✅ Project created!", fg="green")
    click.echo(f"Location: {project_dir}")
    if not no_venv:
        py = _python_path(venv_dir)
        if platform.system().lower().startswith("win"):
            activate_hint = f"{venv_dir}\\Scripts\\activate"
        else:
            activate_hint = f"source {venv_dir}/bin/activate"
        click.echo(f"\nNext steps:\n  cd {project_dir}\n  {activate_hint}\n  {py} src/main.py")
    else:
        click.echo(f"\nNext steps:\n  cd {project_dir}\n  pip install -r requirements.txt\n  python src/main.py")
