from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ScrapingResult(BaseModel):
    """Pydantic model for the result of a scraping operation."""

    url: HttpUrl
    content: str
    error: Optional[str] = None
    status_code: Optional[int] = None


class DocumentationResults(BaseModel):
    """Pydantic model for the documentation results dictionary."""

    crates_io: Optional[ScrapingResult] = Field(None, alias="crates_io")
    docs_rs: Optional[ScrapingResult] = Field(None, alias="docs_rs")
    lib_rs: Optional[ScrapingResult] = Field(None, alias="lib_rs")
    github: Optional[ScrapingResult] = None
