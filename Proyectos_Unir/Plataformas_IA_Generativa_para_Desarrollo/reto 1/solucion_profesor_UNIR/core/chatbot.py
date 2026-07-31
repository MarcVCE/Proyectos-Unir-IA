"""Logica principal del chatbot: cascada de proveedores con fallback automatico."""

from core.conversation import Conversation

RESPUESTA_PRECONFIGURADA = (
    "Lo siento, ahora mismo ninguno de los proveedores de IA esta disponible. "
    "Vuelve a intentarlo en unos minutos."
)


class Chatbot:
    """Chatbot con fallback automatico entre proveedores.

    Recibe la lista de proveedores en orden de prioridad (OpenAI primero,
    despues Anthropic y por ultimo Google Gemini). Si un proveedor falla por
    cualquier motivo (conectividad, limites de API, clave invalida...), pasa
    al siguiente manteniendo el mismo historial de conversacion.
    """

    def __init__(self, providers: list, conversation: Conversation | None = None) -> None:
        self.providers = providers
        self.conversation = conversation or Conversation()

    def ask(self, user_text: str) -> str:
        """Añade la pregunta al historial y devuelve la respuesta completa.

        Va imprimiendo la respuesta en streaming segun llega. Si todos los
        proveedores fallan, responde con una respuesta preconfigurada para
        garantizar la continuidad del servicio.
        """
        self.conversation.add_user(user_text)

        for provider in self.providers:
            try:
                return self._stream_from(provider)
            except Exception as error:  # noqa: BLE001 - cualquier fallo activa el fallback
                print(
                    f"\n[aviso] {provider.name} no esta disponible "
                    f"({type(error).__name__}). Probando con el siguiente proveedor..."
                )

        print(f"Chatbot: {RESPUESTA_PRECONFIGURADA}")
        self.conversation.add_assistant(RESPUESTA_PRECONFIGURADA)
        return RESPUESTA_PRECONFIGURADA

    def _stream_from(self, provider) -> str:
        """Pide la respuesta a un proveedor concreto y la muestra en streaming."""
        chunks: list[str] = []
        print(f"Chatbot ({provider.name}): ", end="", flush=True)
        for chunk in provider.stream_chat(self.conversation.messages):
            chunks.append(chunk)
            print(chunk, end="", flush=True)
        print()

        respuesta = "".join(chunks)
        if not respuesta.strip():
            raise RuntimeError("el proveedor devolvio una respuesta vacia")
        self.conversation.add_assistant(respuesta)
        return respuesta
