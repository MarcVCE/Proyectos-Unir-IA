"""Punto de entrada: chatbot de expertos tematicos con Ollama y gemma3:1b."""

from core.chatbot import Chatbot, OllamaNoDisponibleError
from core.conversation import Conversation
from experts.expert_prompts import EXPERTS

COMANDOS = "/experto (cambiar de experto) | /reiniciar (borrar dialogo) | /salir"


def elegir_experto() -> dict | None:
    """Muestra el menu de expertos y devuelve el elegido (None para salir)."""
    print("\nExpertos disponibles:")
    for opcion, experto in EXPERTS.items():
        print(f"  {opcion}. {experto['name']}")
    print("  0. Salir")

    while True:
        opcion = input("Elige experto (numero): ").strip()
        if opcion == "0":
            return None
        if opcion in EXPERTS:
            return EXPERTS[opcion]
        print("Opcion no valida. Prueba otra vez.")


def main() -> None:
    print("=" * 62)
    print("Chatbot de expertos tematicos con Ollama (modelo local gemma3:1b)")
    print("Funciona 100% offline con el servicio local de Ollama.")
    print("=" * 62)

    conversation = Conversation()
    chatbot = Chatbot(conversation)

    try:
        chatbot.check_model_available()
    except OllamaNoDisponibleError as error:
        print(f"\n[error] {error}")
        return

    experto = elegir_experto()
    if experto is None:
        print("Hasta pronto.")
        return
    conversation.set_expert(experto["system_prompt"])
    print(f"\nExperto activo: {experto['name']}")
    print(f"Comandos: {COMANDOS}")

    while True:
        try:
            user_text = input(f"\n[{experto['name']}] Tu: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nHasta pronto.")
            break

        if not user_text:
            continue

        if user_text.lower() == "/salir":
            print("Hasta pronto.")
            break

        if user_text.lower() == "/reiniciar":
            conversation.reset()
            print("Dialogo reiniciado. El experto activo se mantiene.")
            continue

        if user_text.lower() == "/experto":
            nuevo = elegir_experto()
            if nuevo is None:
                print("Hasta pronto.")
                break
            experto = nuevo
            # Cambiamos el prompt de sistema conservando el historial para
            # que el nuevo experto tenga el contexto de lo ya hablado.
            conversation.set_expert(experto["system_prompt"])
            print(f"Experto activo: {experto['name']}")
            print(f"Comandos: {COMANDOS}")
            continue

        print(f"{experto['name']}: ", end="", flush=True)
        try:
            chatbot.ask(user_text)
        except OllamaNoDisponibleError as error:
            print(f"\n[error] {error}")


if __name__ == "__main__":
    main()
