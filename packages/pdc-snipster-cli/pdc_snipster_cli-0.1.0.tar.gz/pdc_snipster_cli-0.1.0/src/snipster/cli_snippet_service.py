from typing import Sequence

from .db import SessionFactory
from .models import Snippet, SnippetCreate
from .repo import DatabaseBackedSnippetRepo


def get_snippet(session_factory: SessionFactory, snippet_id: int) -> Snippet:
    """Get a snippet by its ID."""
    with session_factory.get_session() as session:
        repo = DatabaseBackedSnippetRepo(session=session)
        snippet = repo.get(snippet_id)
        # Properly detach the object from the session
        session.expunge(snippet)
        return snippet


def add_snippet(
    session_factory: SessionFactory, snippet_data: SnippetCreate
) -> Snippet:
    """Add a new snippet."""
    with session_factory.get_session() as session:
        repo = DatabaseBackedSnippetRepo(session=session)
        return repo.add(snippet_data)


def list_snippets(session_factory: SessionFactory) -> Sequence[Snippet]:
    """List all snippets."""
    with session_factory.get_session() as session:
        repo = DatabaseBackedSnippetRepo(session=session)
        snippets = repo.list()
        # Properly detach all objects from the session
        for snippet in snippets:
            session.expunge(snippet)
        return snippets


def delete_snippet(session_factory: SessionFactory, snippet_id: int) -> None:
    """Delete a snippet by its ID."""
    with session_factory.get_session() as session:
        repo = DatabaseBackedSnippetRepo(session=session)
        repo.delete(snippet_id)


def toggle_snippet_favorite(
    session_factory: SessionFactory, snippet_id: int
) -> Snippet:
    """Toggle the favorite status of a snippet and return the updated snippet."""
    with session_factory.get_session() as session:
        repo = DatabaseBackedSnippetRepo(session=session)
        snippet = repo.get(snippet_id)
        snippet.favorite = not snippet.favorite
        session.commit()
        session.refresh(snippet)
        # Properly detach the object from the session
        session.expunge(snippet)
        return snippet


def search_snippets(session_factory: SessionFactory, query: str) -> Sequence[Snippet]:
    """Search for snippets by query."""
    with session_factory.get_session() as session:
        repo = DatabaseBackedSnippetRepo(session=session)
        snippets = repo.search(query)
        # Properly detach all objects from the session
        for snippet in snippets:
            session.expunge(snippet)
        return snippets


def add_tag_to_snippet(
    session_factory: SessionFactory, snippet_id: int, tag: str
) -> None:
    """Add a tag to a snippet."""
    with session_factory.get_session() as session:
        repo = DatabaseBackedSnippetRepo(session=session)
        repo.add_tag(snippet_id, tag)


def remove_tag_from_snippet(
    session_factory: SessionFactory, snippet_id: int, tag: str
) -> None:
    """Remove a tag from a snippet."""
    with session_factory.get_session() as session:
        repo = DatabaseBackedSnippetRepo(session=session)
        repo.remove_tag(snippet_id, tag)


def fuzzy_search_snippets(
    session_factory: SessionFactory, query: str
) -> Sequence[Snippet]:
    """Fuzzy search for snippets by query."""
    with session_factory.get_session() as session:
        repo = DatabaseBackedSnippetRepo(session=session)
        snippets = repo.fuzzy_search(query)
        # Properly detach all objects from the session
        for snippet in snippets:
            session.expunge(snippet)
        return snippets
