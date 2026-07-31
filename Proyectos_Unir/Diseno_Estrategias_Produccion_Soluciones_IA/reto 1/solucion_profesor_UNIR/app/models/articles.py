"""Modelos del endpoint de generacion de articulos SEO."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ArticleRequest(BaseModel):
    main_keyword: str = Field(min_length=2)
    secondary_keywords: list[str] = Field(default_factory=list)
    word_count: int = Field(default=800, ge=200, le=3000)
    tone: str = Field(default="profesional")


class ArticleSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    heading_level: Literal["H2", "H3"]
    title: str
    content: str


class ArticleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(description="Titulo H1 del articulo con la keyword principal")
    sections: list[ArticleSection] = Field(description="Secciones H2/H3 jerarquicas")
    keyword_density: float = Field(description="Densidad estimada de la keyword principal, en %")
    call_to_actions: list[str] = Field(description="Llamadas a la accion del articulo")
