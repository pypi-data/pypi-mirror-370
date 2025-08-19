from datetime import datetime, timezone
from enum import Enum
from typing import Any, List

from pydantic import field_validator
from sqlalchemy import JSON, Column
from sqlalchemy.ext.mutable import MutableList
from sqlmodel import Field, SQLModel


class Language(str, Enum):
    javascript = "javascript"
    python = "python"
    rust = "rust"


class SnippetBase(SQLModel, table=False):
    title: str = Field(description="Title of the snippet", min_length=3)
    code: str = Field(description="The actual code snippet content", min_length=3)
    language: str = Field(description="Programming language of the snippet")
    description: str | None = Field(
        default=None, description="Optional description of the snippet"
    )
    # This should work for both Sqlite and Postgres
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(MutableList.as_mutable(JSON)),
        description="List of tags associated with the snippet",
    )
    favorite: bool = Field(
        default=False, description="Whether this snippet is marked as favorite"
    )

    @field_validator("language")
    def validate_language(cls, v):
        if isinstance(v, str):
            v = v.lower()
        allowed = ["javascript", "python", "rust"]
        if v not in allowed:
            raise ValueError(f"Language must be one of: {allowed}")
        return v


class Snippet(SnippetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None

    def __str__(self) -> str:
        return (
            f"{self.id}: {self.title} ({self.language}) {'⭐️' if self.favorite else ''}"
        )

    @classmethod
    def create_snippet(cls, **kwargs: Any) -> "Snippet":
        title = kwargs.get("title")
        if title is None or len(title) < 3:
            raise ValueError("Title must be at least 3 characters.")
        code = kwargs.get("code")
        if code is None or len(code) < 3:
            raise ValueError("Code must be at least 3 characters.")
        return cls(**kwargs)


class SnippetCreate(SnippetBase, table=False):
    pass
