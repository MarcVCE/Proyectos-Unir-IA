"""Proveedor Google Gemini usando el SDK google-genai en modo streaming."""

from collections.abc import Iterator

from google import genai
from google.genai import types


class GeminiProvider:
    """Genera respuestas con la API de Google Gemini (streaming)."""

    name = "Google Gemini"

    def __init__(self, model: str = "gemini-flash-latest") -> None:
        self.model = model
        self._client: genai.Client | None = None

    @property
    def client(self) -> genai.Client:
        # Cliente perezoso: lee GOOGLE_API_KEY (o GEMINI_API_KEY) del entorno
        # en el primer uso, de modo que una clave ausente activa el fallback
        # en vez de romper el arranque de la aplicacion.
        if self._client is None:
            self._client = genai.Client()
        return self._client

    def stream_chat(self, messages: list[dict]) -> Iterator[str]:
        """Envia el historial y devuelve la respuesta en trozos.

        Gemini usa los roles user y model, asi que traducimos el historial:
        assistant pasa a ser model y los mensajes de sistema se envian como
        system_instruction en la configuracion.
        """
        system_parts = [m["content"] for m in messages if m["role"] in ("system", "developer")]
        contents = [
            types.Content(
                role="model" if m["role"] == "assistant" else "user",
                parts=[types.Part.from_text(text=m["content"])],
            )
            for m in messages
            if m["role"] in ("user", "assistant")
        ]

        config = types.GenerateContentConfig(
            system_instruction="\n".join(system_parts) or None,
        )
        stream = self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=config,
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text
