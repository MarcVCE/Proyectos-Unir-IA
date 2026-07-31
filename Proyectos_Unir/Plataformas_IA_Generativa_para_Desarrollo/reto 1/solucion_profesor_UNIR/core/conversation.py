"""Gestion del historial de conversacion en memoria."""


class Conversation:
    """Mantiene el historial completo de mensajes usuario-asistente.

    El historial se guarda como una lista de diccionarios con el formato
    {"role": ..., "content": ...} que aceptan los tres SDKs (con pequeñas
    adaptaciones por proveedor que hace cada provider).
    """

    def __init__(self, system_prompt: str | None = None) -> None:
        self._messages: list[dict] = []
        if system_prompt:
            self._messages.append({"role": "developer", "content": system_prompt})

    @property
    def messages(self) -> list[dict]:
        """Devuelve una copia del historial para que nadie lo mute por fuera."""
        return list(self._messages)

    def add_user(self, content: str) -> None:
        self._messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str) -> None:
        self._messages.append({"role": "assistant", "content": content})

    def clear(self) -> None:
        """Borra el historial conservando el mensaje de sistema si lo hay."""
        self._messages = [m for m in self._messages if m["role"] == "developer"]

    def __len__(self) -> int:
        return len(self._messages)
