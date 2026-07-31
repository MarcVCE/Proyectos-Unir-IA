"""Punto de entrada: chatbot de agentes especializados para posts de LinkedIn."""

from dotenv import load_dotenv

from core.chatbot import Chatbot


def main() -> None:
    # Carga OPENAI_API_KEY desde el archivo .env
    load_dotenv()

    chatbot = Chatbot()

    print("=" * 60)
    print("Generador de posts de LinkedIn con agentes especializados")
    print("Tematicas: marketing, programacion y juridico-legal.")
    print("Describe el post que quieres. Escribe /salir para terminar.")
    print("=" * 60)

    while True:
        try:
            user_text = input("\nTu: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nHasta pronto.")
            break

        if not user_text:
            continue
        if user_text.lower() == "/salir":
            print("Hasta pronto.")
            break

        try:
            chatbot.ask(user_text)
        except Exception as error:  # noqa: BLE001 - errores de API o de red
            print(f"[error] No se pudo completar el turno: {error}")


if __name__ == "__main__":
    main()
