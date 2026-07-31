"""Proveedor OpenAI usando la API Responses en modo streaming."""

from collections.abc import Iterator

from openai import OpenAI


class OpenAIProvider:
    """Genera respuestas con la API Responses de OpenAI (streaming)."""

    name = "OpenAI"

    def __init__(self, model: str = "gpt-5.4-mini") -> None:
        self.model = model
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        # Cliente perezoso: lee OPENAI_API_KEY del entorno en el primer uso.
        # Si la clave falta, la excepcion salta al pedir la respuesta y la
        # captura la logica de fallback (en lugar de romper el arranque).
        if self._client is None:
            self._client = OpenAI()
        return self._client

    def stream_chat(self, messages: list[dict]) -> Iterator[str]:
        """Envia el historial completo y va devolviendo la respuesta en trozos.

        La API Responses acepta directamente una lista de mensajes con
        role (developer/user/assistant) y content, igual que el historial
        que mantiene la clase Conversation.
        """
        stream = self.client.responses.create(
            model=self.model,
            input=messages,
            stream=True,
        )
        for event in stream:
            # Solo nos interesan los deltas de texto de la respuesta.
            if event.type == "response.output_text.delta":
                yield event.delta
