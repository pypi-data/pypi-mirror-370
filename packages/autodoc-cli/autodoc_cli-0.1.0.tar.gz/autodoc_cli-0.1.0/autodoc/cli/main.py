import sys
from pathlib import Path
from typing import Optional

import typer

from autodoc.scanner import process_directory
from autodoc.db.sqlite import HashDatabase
from autodoc.llm.ollama import OllamaClient


app = typer.Typer(add_completion=False, help="Generate documentation comments using Tree-sitter and a local Ollama model.")


@app.command()
def run(
    target: str = typer.Argument(..., help="Target directory to scan (recursively)"),
    model: str = typer.Option("qwen2.5-coder:7b", "--model", help="Ollama model name/tag"),
    db_path: Optional[str] = typer.Option(None, "--db", help="Path to SQLite database (defaults to .autodoc.sqlite in project root)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not modify files; print planned changes"),
):
    target_path = Path(target).resolve()
    if not target_path.exists() or not target_path.is_dir():
        typer.echo(f"Target directory not found: {target_path}")
        raise typer.Exit(code=2)

    database_path = Path(db_path).resolve() if db_path else (target_path / ".autodoc.sqlite")
    db = HashDatabase(database_path)
    db.initialize()

    llm = OllamaClient(model=model)
    if not dry_run and not llm.is_available():
        typer.echo("Ollama is not reachable at http://localhost:11434. Start it with 'ollama serve' and ensure the model is pulled (e.g., 'ollama pull ' + model).", err=True)
        raise typer.Exit(code=2)

    summary = process_directory(target_path, db=db, llm=llm, dry_run=dry_run)

    if dry_run:
        plans = summary.get("plans", [])
        if isinstance(plans, list):
            for line in plans:
                typer.echo(line)

    typer.echo(
        f"Processed files: {summary['files']} | functions: {summary['functions']} | new: {summary['new']} | updated: {summary['updated']} | skipped: {summary['skipped']}"
    )


def main() -> int:
    app()
    return 0


if __name__ == "__main__":
    sys.exit(main())


