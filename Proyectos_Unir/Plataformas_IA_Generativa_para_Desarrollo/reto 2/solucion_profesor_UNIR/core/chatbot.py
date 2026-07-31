"""Logica principal del chatbot: conexion con Ollama y modelo local gemma3:1b."""

import ollama

from core.conversation import Conversation

MODEL = "gemma3:1b"


class OllamaNoDisponibleError(Exception):
    """El servicio de Ollama no responde o el modelo no esta descargado."""


class Chatbot:
    """Chatbot que conversa con el modelo local gemma3:1b via Ollama SDK.

    Funciona completamente offline: solo necesita el servicio local de
    Ollama arrancado y el modelo descargado (ollama pull gemma3:1b).
    """

    def __init__(self, conversation: Conversation | None = None, model: str = MODEL) -> None:
        self.conversation = conversation or Conversation()
        self.model = model

    def check_model_available(self) -> None:
        """Comprueba que Ollama responde y que el modelo esta descargado."""
        try:
            models = [m.model for m in ollama.list().models]
        except ConnectionError as error:
            raise OllamaNoDisponibleError(
                "No se puede conectar con Ollama. Arranca el servicio local "
                "(ollama serve o la aplicacion de escritorio) y vuelve a intentarlo."
            ) from error
        if not any(name.startswith(self.model) for name in models):
            raise OllamaNoDisponibleError(
                f"El modelo {self.model} no esta descargado. "
                f"Descargalo con: ollama pull {self.model}"
            )

    def ask(self, user_text: str) -> str:
        """Envia la pregunta al modelo manteniendo el contexto del dialogo.

        Muestra la respuesta en streaming segun se genera y la añade al
        historial para conservar la coherencia entre intercambios.
        """
        self.conversation.add_user(user_text)
        chunks: list[str] = []
        try:
            stream = ollama.chat(
                model=self.model,
                messages=self.conversation.messages,
                stream=True,
            )
            for chunk in stream:
                text = chunk["message"]["content"]
                chunks.append(text)
                print(text, end="", flush=True)
            print()
        except ConnectionError as error:
            raise OllamaNoDisponibleError(
                "Se ha perdido la conexion con Ollama. Comprueba que el servicio "
                "local sigue arrancado (ollama serve)."
            ) from error
        except ollama.ResponseError as error:
            raise OllamaNoDisponibleError(
                f"Ollama ha devuelto un error: {error.error}. Si el modelo no esta "
                f"descargado, ejecuta: ollama pull {self.model}"
            ) from error

        respuesta = "".join(chunks)
        self.conversation.add_assistant(respuesta)
        return respuesta
