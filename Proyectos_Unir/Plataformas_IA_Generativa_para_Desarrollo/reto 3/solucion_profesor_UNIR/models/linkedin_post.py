"""Modelo Pydantic del post de LinkedIn con validacion estricta."""

from pydantic import BaseModel, ConfigDict, Field


class LinkedinPost(BaseModel):
    """Post de LinkedIn generado por la IA.

    Hereda de BaseModel para ser compatible con Structured Outputs de OpenAI.
    extra="forbid" prohibe propiedades adicionales fuera del esquema, de modo
    que la validacion es estricta: la respuesta debe cumplir exactamente este
    contrato o Pydantic lanza un error de validacion.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(description="Titulo llamativo del post, en una linea")
    content: str = Field(description="Cuerpo del post, en tono profesional y cercano")
    hashtags: list[str] = Field(description="Hashtags relevantes, sin el simbolo #")
    category: str = Field(description="Categoria tematica del post, p. ej. tecnologia")
