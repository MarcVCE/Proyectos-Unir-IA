"""Agentes especializados por tematica y modelo Pydantic de la publicacion.

Nota sobre la estructura: el enunciado sugiere una carpeta agents/, pero ese
nombre colisiona con el modulo agents del propio OpenAI Agents SDK (romperia
los imports), asi que el paquete local se llama post_agents/.
"""

from agents import Agent
from pydantic import BaseModel, ConfigDict, Field

MODEL = "gpt-4.1-mini"


class LinkedinPost(BaseModel):
    """Estructura comun de toda publicacion generada."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(description="Titulo atractivo de la publicacion")
    content: str = Field(description="Cuerpo principal de la publicacion")
    hashtags: list[str] = Field(description="Palabras clave relevantes, sin el simbolo #")
    category: str = Field(description="Tematica de la publicacion")


def _post_instructions(especialidad: str, enfoque: str) -> str:
    return (
        f"Eres un experto en {especialidad}. Genera publicaciones de LinkedIn en "
        f"español sobre la peticion del usuario, {enfoque}. La publicacion debe "
        "tener un titulo atractivo, un contenido profesional y cercano de 2 o 3 "
        "parrafos, hashtags relevantes (sin el simbolo #) y la categoria tematica."
    )


marketing_agent = Agent(
    name="Agente de Marketing",
    handoff_description="Especialista en publicaciones sobre marketing, ventas y marca",
    instructions=_post_instructions(
        "marketing digital y estrategia de marca",
        "con enfoque comercial, orientado a negocio y engagement",
    ),
    model=MODEL,
    output_type=LinkedinPost,
)

programacion_agent = Agent(
    name="Agente de Programacion",
    handoff_description="Especialista en publicaciones sobre desarrollo de software y tecnologia",
    instructions=_post_instructions(
        "desarrollo de software e ingenieria",
        "con rigor tecnico, ejemplos concretos y buenas practicas",
    ),
    model=MODEL,
    output_type=LinkedinPost,
)

juridico_agent = Agent(
    name="Agente Juridico Legal",
    handoff_description="Especialista en publicaciones sobre derecho, normativa y cumplimiento",
    instructions=_post_instructions(
        "derecho y cumplimiento normativo",
        "con lenguaje riguroso pero comprensible, sin dar consejo legal vinculante",
    ),
    model=MODEL,
    output_type=LinkedinPost,
)

SPECIALIZED_AGENTS = [marketing_agent, programacion_agent, juridico_agent]
