"""Proveedor Anthropic (Claude) usando el SDK oficial en modo streaming."""

from collections.abc import Iterator

from anthropic import Anthropic


class AnthropicProvider:
    """Genera respuestas con la API Messages de Anthropic (streaming)."""

    name = "Anthropic Claude"

    def __init__(self, model: str = "claude-haiku-4-5") -> None:
        self.model = model
        self._client: Anthropic | None = None

    @property
    def client(self) -> Anthropic:
        # Cliente perezoso: lee ANTHROPIC_API_KEY del entorno en el primer uso,
        # de modo que una clave ausente activa el fallback en vez de romper
        # el arranque de la aplicacion.
        if self._client is None:
            self._client = Anthropic()
        return self._client

    def stream_chat(self, messages: list[dict]) -> Iterator[str]:
        """Envia el historial y devuelve la respuesta en trozos.

        Anthropic separa el mensaje de sistema del resto: los roles
        developer/system van en el parametro system y los mensajes de
        conversacion solo admiten user y assistant.
        """
        system_parts = [m["content"] for m in messages if m["role"] in ("system", "developer")]
        chat_messages = [m for m in messages if m["role"] in ("user", "assistant")]

        with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            system="\n".join(system_parts) or "Eres un asistente conversacional en español.",
            messages=chat_messages,
        ) as stream:
            for text in stream.text_stream:
                yield text
