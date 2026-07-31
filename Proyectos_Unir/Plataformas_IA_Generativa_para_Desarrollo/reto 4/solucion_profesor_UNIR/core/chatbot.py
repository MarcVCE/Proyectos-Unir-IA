"""Logica del chatbot: consulta -> retrieval -> generacion -> respuesta."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from core.rag_system import RAGSystem

SYSTEM_PROMPT = (
    "Eres el asistente interno de la empresa TechNova Solutions. Responde en "
    "español, de forma clara y concisa, usando UNICAMENTE la informacion del "
    "contexto recuperado de los documentos internos. Si la respuesta no esta "
    "en el contexto, di que no dispones de esa informacion en los documentos, "
    "sin inventar nada."
)


class Chatbot:
    """Chatbot conversacional que integra el sistema RAG.

    Mantiene el historial de la conversacion durante la sesion y, para cada
    pregunta, recupera los fragmentos relevantes y se los pasa al modelo como
    contexto junto al historial.
    """

    def __init__(self, rag_system: RAGSystem, model: str = "gpt-4.1") -> None:
        self.rag = rag_system
        self.llm = ChatOpenAI(model=model)
        self._history: list = []

    def ask(self, question: str) -> str:
        """Responde a la pregunta usando RAG y conserva el contexto."""
        context = self.rag.retrieve_context(question)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *self._history,
            HumanMessage(
                content=(
                    f"Contexto recuperado de los documentos internos:\n\n{context}\n\n"
                    f"Pregunta: {question}"
                )
            ),
        ]
        response = self.llm.invoke(messages)
        answer = response.content if isinstance(response.content, str) else str(response.content)

        # En el historial guardamos la pregunta limpia (sin el contexto inyectado)
        # para que las siguientes vueltas mantengan la conversacion legible.
        self._history.append(HumanMessage(content=question))
        self._history.append(AIMessage(content=answer))
        return answer
