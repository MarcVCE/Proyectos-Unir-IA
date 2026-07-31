"""Agente principal: recibe la peticion y delega en el especialista adecuado."""

from agents import Agent

from post_agents.specialized_agents import SPECIALIZED_AGENTS, MODEL

main_agent = Agent(
    name="Agente Principal",
    instructions=(
        "Eres el coordinador de un equipo de agentes que generan publicaciones "
        "de LinkedIn. Analiza la peticion del usuario y delega SIEMPRE en el "
        "agente especializado cuya tematica encaje mejor: marketing (ventas, "
        "marca, campañas, negocio), programacion (software, lenguajes, "
        "herramientas, ingenieria) o juridico-legal (normativa, contratos, "
        "cumplimiento, proteccion de datos). Si la peticion no encaja claramente "
        "en ninguna tematica o falta informacion, pide al usuario que concrete "
        "el tema de la publicacion. Responde siempre en español."
    ),
    model=MODEL,
    handoffs=list(SPECIALIZED_AGENTS),
)
