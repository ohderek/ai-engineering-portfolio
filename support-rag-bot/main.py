"""
Support RAG Bot — CLI entry point.

Usage:
  # Step 1: ingest a document (run once)
  python main.py ingest data/flowdesk_faq.txt

  # Step 2: ask a single question
  python main.py ask "How do I cancel my subscription?"

  # Step 3: interactive chat session
  python main.py chat
"""

import typer
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

load_dotenv()

app = typer.Typer(help="RAG-powered support bot — ask questions about any document.")
console = Console()


@app.command()
def ingest(
    file: Path = typer.Argument(..., help="Path to the document to ingest (.txt)"),
) -> None:
    """
    Load, chunk, embed, and store a document in the local vector database.
    Run this once before using 'ask' or 'chat'.
    """
    from src.ingest import ingest as run_ingest
    run_ingest(str(file))
    console.print("[bold green]Ingestion complete.[/bold green] "
                  "You can now run: python main.py ask \"your question\"")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask about the document"),
    show_sources: bool = typer.Option(False, "--sources", "-s",
                                      help="Print the source chunks used"),
) -> None:
    """
    Ask a single question. The bot retrieves relevant chunks and answers.
    """
    from src.ingest import load_existing
    from src.chain import build_chain

    vectorstore = load_existing()
    chain, retriever = build_chain(vectorstore)

    console.print(f"\n[bold]Q:[/bold] {question}\n")
    console.print("[bold]A:[/bold]")

    answer = chain.invoke(question)
    console.print(Markdown(answer))

    if show_sources:
        docs = retriever.invoke(question)
        console.print("\n[dim]── Source chunks used ──[/dim]")
        for i, doc in enumerate(docs, 1):
            console.print(f"[dim][{i}] {doc.page_content[:200]}...[/dim]")


@app.command()
def chat() -> None:
    """
    Interactive Q&A session. Ask multiple questions about the document.
    Type 'exit' to quit.
    """
    from src.ingest import load_existing
    from src.chain import build_chain

    vectorstore = load_existing()
    chain, retriever = build_chain(vectorstore)

    console.print(
        Panel(
            "[bold cyan]Support RAG Bot[/bold cyan]\n"
            "Ask anything about the ingested document.\n"
            "Add [bold]--sources[/bold] to any question to see which chunks were used.\n"
            "Type [bold]exit[/bold] to quit.",
            expand=False,
        )
    )

    while True:
        question = console.input("\n[bold green]You:[/bold green] ").strip()
        if question.lower() in {"exit", "quit", "q"}:
            console.print("[dim]Goodbye![/dim]")
            break
        if not question:
            continue

        show_sources = question.endswith("--sources")
        question = question.replace("--sources", "").strip()

        console.print("\n[bold blue]Bot:[/bold blue]")
        answer = chain.invoke(question)
        console.print(Markdown(answer))

        if show_sources:
            docs = retriever.invoke(question)
            console.print("\n[dim]── Source chunks used ──[/dim]")
            for i, doc in enumerate(docs, 1):
                console.print(f"[dim][{i}] {doc.page_content[:200]}...[/dim]")


if __name__ == "__main__":
    app()
