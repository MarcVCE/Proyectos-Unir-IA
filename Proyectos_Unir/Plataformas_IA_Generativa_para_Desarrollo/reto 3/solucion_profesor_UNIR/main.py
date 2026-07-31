"""Punto de entrada: generador de posts de LinkedIn con salidas estructuradas."""

from dotenv import load_dotenv

from core.chatbot import Chatbot


def main() -> None:
    # Carga OPENAI_API_KEY desde el archivo .env
    load_dotenv()

    chatbot = Chatbot()

    print("=" * 60)
    print("Generador de posts de LinkedIn (OpenAI Structured Outputs)")
    print("Describe tu idea y la IA generara un post estructurado.")
    print("Escribe 'salir' para terminar.")
    print("=" * 60)

    while True:
        try:
            idea = chatbot.pedir_idea()
        except (KeyboardInterrupt, EOFError):
            print("\nHasta pronto.")
            break

        if not idea:
            continue
        if idea.lower() == "salir":
            print("Hasta pronto.")
            break

        post = chatbot.procesar(idea)
        if post is not None:
            chatbot.mostrar(post)


if __name__ == "__main__":
    main()
