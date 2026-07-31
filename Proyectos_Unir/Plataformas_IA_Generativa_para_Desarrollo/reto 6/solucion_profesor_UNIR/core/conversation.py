"""Gestion del historial de la conversacion entre turnos."""


class Conversation:
    """Mantiene el historial en el formato de items del Agents SDK.

    El Runner devuelve en cada turno la lista completa de items de entrada
    para el siguiente turno (result.to_input_list()), de modo que el historial
    conserva tanto los mensajes como los handoffs entre agentes.
    """

    def __init__(self) -> None:
        self._items: list = []

    def input_for(self, user_text: str) -> list:
        """Historial previo + el nuevo mensaje del usuario, listo para el Runner."""
        return self._items + [{"role": "user", "content": user_text}]

    def update(self, result) -> None:
        """Guarda el estado devuelto por el Runner tras un turno."""
        self._items = result.to_input_list()

    @property
    def turns(self) -> int:
        return len(self._items)
