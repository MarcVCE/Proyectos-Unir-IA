"""Cliente de OpenAI: llamada con Structured Outputs y manejo de rechazos."""

from openai import OpenAI

from models.linkedin_post import LinkedinPost

MODEL = "gpt-4.1"

SYSTEM_PROMPT = (
    "Eres un experto en comunicacion profesional en LinkedIn. A partir de la idea "
    "del usuario, genera un post en español con tono profesional y cercano. "
    "Devuelve titulo, contenido, hashtags (sin el simbolo #) y categoria tematica."
)


class RechazoAPIError(Exception):
    """El modelo ha rechazado generar el contenido solicitado (refusal)."""


class OpenAIClient:
    """Encapsula la llamada a la API Responses con salidas estructuradas."""

    def __init__(self, model: str = MODEL) -> None:
        # El cliente lee OPENAI_API_KEY del entorno (cargado desde .env).
        self.client = OpenAI()
        self.model = model

    def generar_post(self, idea: str) -> LinkedinPost:
        """Genera un post de LinkedIn validado contra el modelo Pydantic.

        Usa responses.parse() con text_format=LinkedinPost: la API garantiza
        una salida que cumple el esquema y el SDK la parsea directamente a la
        clase Pydantic. Lanza RechazoAPIError si el modelo rechaza la peticion
        y deja propagarse los errores de API, limite de tokens y validacion
        para que la capa superior informe al usuario.
        """
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Idea para el post: {idea}"},
            ],
            text_format=LinkedinPost,
        )

        # Si el modelo rechaza la peticion (contenido inapropiado, filtros...),
        # el item de salida es un refusal y output_parsed viene vacio.
        for item in response.output:
            if item.type == "message":
                for part in item.content:
                    if part.type == "refusal":
                        raise RechazoAPIError(part.refusal)

        if response.output_parsed is None:
            raise RechazoAPIError("La API no devolvio un post estructurado valido.")

        return response.output_parsed
