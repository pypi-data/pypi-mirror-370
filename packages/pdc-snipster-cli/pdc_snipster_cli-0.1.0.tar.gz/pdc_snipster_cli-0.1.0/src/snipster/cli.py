import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from typing_extensions import Annotated

from . import cli_snippet_service
from .db import default_session_factory
from .exceptions import SnippetNotFoundError
from .models import Language as LanguageEnum
from .models import SnippetCreate

load_dotenv()

# Note: This uses the default session factory which is backed by postgres in production.
# In tests, this gets monkey patched to use an in-memory SQLite database via the
# test_session_factory fixture in tests/conftest.py. This allows tests to run quickly
# without requiring a real database while still testing the same code paths.
cli_session_factory = default_session_factory


app = typer.Typer(help="Snipster: A CLI for managing code snippets.")


@app.callback(invoke_without_command=True)
def setup(ctx: typer.Context):
    console = Console()
    # All commands will use the same session factory (interact with the same DB)
    ctx.obj = {"session_factory": cli_session_factory, "console": console}
    if ctx.invoked_subcommand is None:
        typer.echo("📘 Welcome to Snipster!\n")
        typer.echo("Use one of the following commands:")
        typer.echo(ctx.get_help())


@app.command()
def get(
    ctx: typer.Context,
    snippet_id: Annotated[int, typer.Argument(help="ID of the snippet to retrieve")],
):
    """
    Get and display a snippet by its ID.
    """
    session_factory = ctx.obj["session_factory"]
    console = ctx.obj["console"]

    try:
        snippet = cli_snippet_service.get_snippet(session_factory, snippet_id)
    except SnippetNotFoundError:
        console.print(f"[red]Error: Snippet with ID {snippet_id} not found.[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(code=1)

    title = Text(f"{snippet.title} ")
    if snippet.favorite:
        title.append("⭐️", style="yellow")

    description_panel = None
    if snippet.description:
        description_panel = Panel(
            snippet.description, title="Description", border_style="blue"
        )

    code = Syntax(
        snippet.code,
        snippet.language.value,
        theme="monokai",
        line_numbers=True,
        word_wrap=True,
    )

    console.print()
    console.print(title, style="bold blue")
    if description_panel:
        console.print(description_panel)
    console.print(code)
    console.print(f"\nTags: {', '.join(snippet.tags)}" if snippet.tags else "")


@app.command()
def add(
    ctx: typer.Context,
    title: Annotated[
        str, typer.Option(..., "--title", "-t", help="Title of the snippet")
    ],
    code: Annotated[str, typer.Option(..., "--code", "-c", help="The snippet code")],
    language: Annotated[
        LanguageEnum,
        typer.Option(
            ...,
            "--language",
            "--lang",
            "-l",
            help="Which language is your snippet written in? Javascript, Python, or Rust",
            case_sensitive=False,
            prompt="Choose a language",
            show_choices=True,
        ),
    ],
    description: Annotated[
        str,
        typer.Option(
            ...,
            "--description",
            "--desc",
            "-d",
            help="The snippet code",
            rich_help_panel="Optional",
        ),
    ] = "",
):
    """
    Add a new code snippet to the repository.
    """
    session_factory = ctx.obj["session_factory"]
    console = ctx.obj["console"]

    snippet = SnippetCreate(
        title=title, code=code, description=description, language=LanguageEnum(language)
    )
    cli_snippet_service.add_snippet(session_factory, snippet)
    console.print(f"Added snippet: {title}")


@app.command()
def list(ctx: typer.Context):
    """
    List all snippets
    """
    session_factory = ctx.obj["session_factory"]
    console = ctx.obj["console"]

    snippets = cli_snippet_service.list_snippets(session_factory)
    sorted_list = sorted(snippets, key=lambda x: x.id or 0)
    for snippet in sorted_list:
        console.print(snippet.__str__())


@app.command()
def toggle_favorite(ctx: typer.Context, id: Annotated[int, typer.Argument]):
    """
    Toggle the favorite status of a snippet.

    This command will mark a snippet as favorite if it's not already favorited,
    or remove the favorite status if it's already favorited.
    """
    session_factory = ctx.obj["session_factory"]
    console = ctx.obj["console"]

    try:
        snippet = cli_snippet_service.toggle_snippet_favorite(session_factory, id)
        if snippet.favorite:
            console.print(f"Favorited: {snippet}")
        else:
            console.print(f"Unfavorited: {snippet}")
    except SnippetNotFoundError:
        console.print(f"[red]Error: Snippet with ID {id} not found.[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(code=1)


@app.command()
def search(
    ctx: typer.Context,
    query: Annotated[
        str,
        typer.Argument(help="Search for snippets by title, description, or tags"),
    ],
):
    """
    Search for snippets by title, description, or tags.

    This command performs a case-insensitive search across snippet titles,
    descriptions, and tags. It will return all snippets that contain the
    search query in any of these fields.
    """
    session_factory = ctx.obj["session_factory"]
    console = ctx.obj["console"]

    snippets = cli_snippet_service.search_snippets(session_factory, query)
    sorted_list = sorted(snippets, key=lambda x: x.id or 0)
    for snippet in sorted_list:
        console.print(snippet.__str__())


@app.command()
def delete(
    ctx: typer.Context,
    id: Annotated[int, typer.Argument(help="The ID of the snippet to delete")],
):
    """
    Delete a snippet by its ID.

    This command permanently removes a snippet from the repository.
    The deletion cannot be undone, so use this command carefully.
    """
    session_factory = ctx.obj["session_factory"]
    console = ctx.obj["console"]

    try:
        cli_snippet_service.delete_snippet(session_factory, id)
        console.print(f"Deleted snippet with id #{id}")
    except SnippetNotFoundError:
        console.print(f"[red]Error: Snippet with ID {id} not found.[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(code=1)
