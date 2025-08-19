from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Sequence

from rapidfuzz import process as rapidfuzz_process
from sqlalchemy import Text, or_
from sqlmodel import Session, select

from .exceptions import SnippetNotFoundError
from .models import Snippet, SnippetCreate


class AbstractSnippetRepo(ABC):  # pragma: no cover
    @abstractmethod
    def add(self, snippet: SnippetCreate) -> Snippet | None:
        pass

    @abstractmethod
    def get(self, snippet_id) -> Snippet | None:
        pass

    @abstractmethod
    def list(self) -> Sequence[Snippet]:
        pass

    @abstractmethod
    def delete(self, snippet_id: int) -> None:
        pass

    @abstractmethod
    def toggle_favorite(self, snippet_id: int) -> Snippet | None:
        pass

    @abstractmethod
    def add_tag(self, snippet_id: int, tag: str) -> Snippet | None:
        pass

    @abstractmethod
    def remove_tag(self, snippet_id: int, tag: str) -> Snippet | None:
        pass

    @abstractmethod
    def search(self, query: str) -> Sequence[Snippet]:
        pass


class DatabaseBackedSnippetRepo(AbstractSnippetRepo):
    # Good to use a single session across calls incase
    # there are multiple operations called at call site
    # Therefore, let the call site handle session management
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, snippet: SnippetCreate) -> Snippet:
        stored_snippet = Snippet.create_snippet(**snippet.model_dump())
        self.session.add(stored_snippet)
        self.session.commit()
        self.session.refresh(stored_snippet)
        return stored_snippet

    def get(self, snippet_id: int) -> Snippet:
        snippet = self.session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError
        return snippet

    def list(self) -> Sequence[Snippet]:
        return list(self.session.exec(select(Snippet)).all())

    def delete(self, snippet_id: int):
        snippet = self.session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        self.session.delete(snippet)
        self.session.commit()

    def toggle_favorite(self, snippet_id: int) -> Snippet:
        snippet = self.session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        snippet.favorite = not snippet.favorite
        self.session.commit()
        self.session.refresh(snippet)
        return snippet

    def add_tag(self, snippet_id: int, tag: str) -> Snippet | None:
        snippet = self.session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        norm = tag.strip().lower()
        if norm not in snippet.tags:
            snippet.tags.append(tag)
            self.session.commit()
            self.session.refresh(snippet)
            return snippet

    def remove_tag(self, snippet_id: int, tag: str) -> Snippet:
        snippet = self.session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        if tag not in snippet.tags:
            raise ValueError(f"Tag {tag} not found on snippet with id {snippet_id}.")
        snippet.tags.remove(tag)
        self.session.commit()
        self.session.refresh(snippet)
        return snippet

    def search(self, query: str) -> Sequence[Snippet]:
        stmt = select(Snippet).where(
            or_(
                Snippet.title.ilike(f"%{query}%"),  # type: ignore
                Snippet.code.ilike(f"%{query}%"),  # type: ignore
                Snippet.description.ilike(f"%{query}%"),  # type: ignore
                # This should work for both Sqlite and Postgres
                Snippet.tags.cast(Text).ilike(f"%{query}%"),  # type: ignore
            )
        )
        results = self.session.exec(stmt).all()
        return [snippet for snippet in results]

    def fuzzy_search(self, query: str) -> Sequence[Snippet]:
        all_snippets = self.session.exec(select(Snippet)).all()
        snippet_dict = {s.title.lower(): s for s in all_snippets}
        matches = rapidfuzz_process.extract(
            query, snippet_dict.keys(), limit=5, score_cutoff=70
        )
        results = [snippet_dict[m[0]] for m in matches]
        return results


class InMemorySnippetRepo(AbstractSnippetRepo):
    def __init__(self):
        self.snippets: dict[int, Snippet] = {}
        self._next_id = 1

    def add(self, snippet: SnippetCreate) -> Snippet:
        stored_snippet = Snippet.create_snippet(
            **snippet.model_dump(),
            id=self._next_id,
            created_at=datetime.now(timezone.utc),
            updated_at=None,
        )
        self.snippets[self._next_id] = stored_snippet
        self._next_id += 1
        return stored_snippet

    def get(self, snippet_id: int) -> Snippet:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError
        return snippet

    def list(self) -> Sequence[Snippet]:
        return list(self.snippets.values())

    def delete(self, snippet_id: int) -> None:
        self.snippets.pop(snippet_id, None)

    def toggle_favorite(self, snippet_id: int) -> Snippet:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        snippet.favorite = not snippet.favorite
        return snippet

    def add_tag(self, snippet_id: int, tag: str) -> Snippet | None:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        if tag not in snippet.tags:
            snippet.tags.append(tag)
            return snippet

    def remove_tag(self, snippet_id: int, tag: str) -> Snippet:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        if tag not in snippet.tags:
            raise ValueError(f"Tag {tag} not found on snippet with id {snippet_id}.")
        snippet.tags.remove(tag)
        return snippet

    def search(self, query: str) -> Sequence[Snippet]:
        query = query.lower()
        results = []
        for snippet in self.snippets.values():
            hit = False
            if query in snippet.title.lower():
                hit = True
            if query in snippet.code.lower():
                hit = True
            if snippet.description:
                if query in snippet.description.lower():
                    hit = True
            if len(snippet.tags) > 0:
                print(snippet.tags)
                if query in snippet.tags:
                    hit = True
            if hit:
                results.append(snippet)
        return list(results)

    def fuzzy_search(self, query: str) -> Sequence[Snippet]:
        snippet_dict = {s.title.lower(): s for s in self.snippets.values()}
        matches = rapidfuzz_process.extract(
            query, snippet_dict.keys(), limit=5, score_cutoff=70
        )
        results = [snippet_dict[m[0]] for m in matches]
        return results
