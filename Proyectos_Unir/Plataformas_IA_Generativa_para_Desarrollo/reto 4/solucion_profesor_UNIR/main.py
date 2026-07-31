"""Punto de entrada: chatbot RAG sobre los documentos internos de la empresa."""

from dotenv import load_dotenv

from core.chatbot import Chatbot
from core.rag_system import RAGSystem


def main() -> None:
    # Carga OPENAI_API_KEY desde el archivo .env
    load_dotenv()

    print("=" * 62)
    print("Chatbot RAG de TechNova Solutions (LangChain + OpenAI)")
    print("Pregunta sobre la empresa o sus politicas internas.")
    print("Escribe /salir (o quit) para terminar.")
    print("=" * 62)

    rag = RAGSystem(documents_dir="documents")
    try:
        n_chunks = rag.load_documents()
    except FileNotFoundError as error:
        print(f"[error] {error}")
        return
    except Exception as error:  # noqa: BLE001 - p. ej. clave invalida al vectorizar
        print(f"[error] No se pudieron vectorizar los documentos: {error}")
        return
    print(f"[info] {n_chunks} fragmentos indexados en el vector store en memoria.")

    chatbot = Chatbot(rag)

    while True:
        try:
            question = input("\nTu: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nHasta pronto.")
            break

        if not question:
            continue
        if question.lower() in ("/salir", "quit"):
            print("Hasta pronto.")
            break

        try:
            answer = chatbot.ask(question)
        except Exception as error:  # noqa: BLE001 - errores de red o de la API
            print(f"[error] No se pudo obtener respuesta del modelo: {error}")
            continue
        print(f"Chatbot: {answer}")


if __name__ == "__main__":
    main()
