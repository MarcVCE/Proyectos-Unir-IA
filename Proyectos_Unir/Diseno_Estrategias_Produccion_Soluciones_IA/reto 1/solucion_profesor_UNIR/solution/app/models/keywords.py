"""Modelos del endpoint de generacion de keywords."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class KeywordRequest(BaseModel):
    topic: str = Field(min_length=2, description="Tema principal")
    industry: str = Field(default="general", description="Sector o industria")
    language: str = Field(default="es", description="Idioma del contenido")


class KeywordIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keyword: str
    intent: Literal["informacional", "transaccional"]


class KeywordResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seed_keywords: list[str] = Field(description="Keywords semilla del tema")
    long_tail_keywords: list[str] = Field(description="Variantes long-tail")
    questions: list[str] = Field(description="Preguntas relacionadas que busca la gente")
    intent_classification: list[KeywordIntent] = Field(
        description="Clasificacion de intencion por keyword"
    )
