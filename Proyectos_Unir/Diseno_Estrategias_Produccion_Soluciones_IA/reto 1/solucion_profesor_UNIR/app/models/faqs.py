"""Modelos del endpoint de extraccion de FAQs con esquema JSON-LD."""

from pydantic import BaseModel, ConfigDict, Field


class FAQRequest(BaseModel):
    article_content: str = Field(min_length=50, description="Contenido del articulo")
    max_questions: int = Field(default=5, ge=1, le=10)


class FAQ(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    answer: str = Field(description="Respuesta corta y util (50-150 palabras)")


class FAQResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    faqs: list[FAQ]
    json_ld_schema: str = Field(
        description="Esquema JSON-LD FAQPage listo para insertar en la pagina"
    )
