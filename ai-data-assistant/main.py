"""
AI Data Assistant — CLI entry point.

Usage:
  python main.py review examples/fct_orders.sql
  python main.py docs examples/fct_orders.sql --model fct_orders
  python main.py chat
"""

import typer
from pathlib import Path
from rich.console import Console

app = typer.Typer(help="AI-powered assistant for data engineers.")
console = Console()


@app.command()
def review(
    sql_file: Path = typer.Argument(..., help="Path to a .sql file to review"),
) -> None:
    """Review a SQL model for best practices and performance issues."""
    from src.sql_reviewer import review_sql

    sql = sql_file.read_text()
    review_sql(sql, model_name=sql_file.stem)


@app.command()
def docs(
    sql_file: Path = typer.Argument(..., help="Path to a .sql file"),
    model: str = typer.Option(None, "--model", "-m", help="dbt model name (defaults to filename)"),
) -> None:
    """Generate dbt schema.yml documentation from a SQL model."""
    from src.doc_generator import generate_docs

    sql = sql_file.read_text()
    model_name = model or sql_file.stem
    generate_docs(sql, model_name=model_name)


@app.command()
def chat() -> None:
    """Start an interactive data engineering chat session."""
    from src.chat import run_chat

    run_chat()


if __name__ == "__main__":
    app()
