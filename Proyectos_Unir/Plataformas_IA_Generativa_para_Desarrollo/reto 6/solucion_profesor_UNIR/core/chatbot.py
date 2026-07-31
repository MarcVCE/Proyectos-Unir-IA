"""Logica principal del chatbot: ejecuta el agente principal y muestra el resultado."""

from agents import Runner

from core.conversation import Conversation
from post_agents.main_agent import main_agent
from post_agents.specialized_agents import LinkedinPost


class Chatbot:
    """Chatbot de terminal sobre el OpenAI Agents SDK.

    Cada turno ejecuta el agente principal con el historial completo; el SDK
    resuelve los handoffs automaticamente y devuelve el agente que ha
    respondido (result.last_agent), que se muestra como indicador visual.
    """

    def __init__(self) -> None:
        self.conversation = Conversation()

    def ask(self, user_text: str) -> None:
        result = Runner.run_sync(main_agent, self.conversation.input_for(user_text))
        self.conversation.update(result)

        print(f"\n[agente: {result.last_agent.name}]")
        output = result.final_output
        if isinstance(output, LinkedinPost):
            self._mostrar_post(output)
        else:
            print(output)

    @staticmethod
    def _mostrar_post(post: LinkedinPost) -> None:
        print("=" * 60)
        print(f"Titulo    : {post.title}")
        print(f"Categoria : {post.category}")
        print("\nContenido:\n")
        print(post.content)
        print("\nHashtags  : " + " ".join(f"#{tag}" for tag in post.hashtags))
        print("=" * 60)
