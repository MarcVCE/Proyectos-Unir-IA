"""Gestion del historial y del estado de la conversacion."""


class Conversation:
    """Mantiene el historial de mensajes y el experto activo.

    El historial usa el formato {"role": ..., "content": ...} que espera
    ollama.chat. El mensaje de sistema (el prompt del experto activo) se
    guarda aparte para poder cambiar de experto sin perder el historial.
    """

    def __init__(self) -> None:
        self._system_prompt: str | None = None
        self._history: list[dict] = []

    @property
    def messages(self) -> list[dict]:
        """Historial completo listo para enviar al modelo (sistema + dialogo)."""
        system = [{"role": "system", "content": self._system_prompt}] if self._system_prompt else []
        return system + list(self._history)

    @property
    def exchanges(self) -> int:
        """Numero de mensajes de dialogo (sin contar el de sistema)."""
        return len(self._history)

    def set_expert(self, system_prompt: str, keep_history: bool = True) -> None:
        """Activa un experto. Por defecto conserva el historial para mantener
        el contexto del dialogo; con keep_history=False se reinicia."""
        self._system_prompt = system_prompt
        if not keep_history:
            self.reset()

    def add_user(self, content: str) -> None:
        self._history.append({"role": "user", "content": content})

    def add_assistant(self, content: str) -> None:
        self._history.append({"role": "assistant", "content": content})

    def reset(self) -> None:
        """Reinicia el dialogo conservando el experto activo."""
        self._history = []
