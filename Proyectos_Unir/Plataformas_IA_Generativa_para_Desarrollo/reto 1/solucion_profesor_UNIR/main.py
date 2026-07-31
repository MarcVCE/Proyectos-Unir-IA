"""Punto de entrada: CLI interactiva del chatbot con fallback multiproveedor."""

from dotenv import load_dotenv

from core.chatbot import Chatbot
from core.conversation import Conversation
from providers.anthropic_provider import AnthropicProvider
from providers.gemini_provider import GeminiProvider
from providers.openai_provider import OpenAIProvider

SYSTEM_PROMPT = (
    "Eres un asistente conversacional util y directo. Respondes siempre en español "
    "de forma breve y clara."
)


def main() -> None:
    # Carga OPENAI_API_KEY, ANTHROPIC_API_KEY y GOOGLE_API_KEY desde el archivo .env
    load_dotenv()

    conversation = Conversation(system_prompt=SYSTEM_PROMPT)
    chatbot = Chatbot(
        providers=[OpenAIProvider(), AnthropicProvider(), GeminiProvider()],
        conversation=conversation,
    )

    print("=" * 60)
    print("Chatbot multiproveedor con fallback (OpenAI -> Claude -> Gemini)")
    print("Escribe tu mensaje y pulsa Enter. Escribe /salir para terminar.")
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

        chatbot.ask(user_text)


if __name__ == "__main__":
    main()
